#!/usr/bin/env python
"""
TrailIQ-IN ETL · final “clean 300” version
-----------------------------------------
• forward + reverse geocode (OSM)          • NASA POWER climatology (°C)
• IMD rainfall merge                       • 2018 tourism crowd-score
• drops rows that still lack coordinates   • full subdivision spelling map
"""

import os, re, json, requests, pandas as pd
from functools              import lru_cache
from geopy.geocoders        import Nominatim
from geopy.extra.rate_limiter import RateLimiter

RAW      = "data/raw"
GCACHE   = f"{RAW}/geocode_cache.json"
CJSON    = f"{RAW}/climate_json"
os.makedirs(CJSON, exist_ok=True)

# ╭─► set to True the very first time you run this cleaned-up script
RESET_CACHE = False
# ╰───────────────────────────────────────────────────────────────

# ───────────────────────── helpers ──────────────────────────
def load_csv(name): return pd.read_csv(f"{RAW}/{name}")

def parse_length(txt):
    m = re.search(r"([\d\.]+)", str(txt)); n = float(m.group(1)) if m else pd.NA
    if pd.isna(n): return pd.NA, pd.NA
    return ((n*1.60934, n) if "mi" in str(txt).lower() else (n, n*0.621371))

# ---------- heat-index from NASA POWER (climatology, °C) ----------
@lru_cache(maxsize=None)
def fetch_heat(lat, lon):
    if pd.isna(lat) or pd.isna(lon): return pd.NA
    fn = f"{CJSON}/{lat:.3f}_{lon:.3f}.json"
    if not os.path.exists(fn):
        url = ("https://power.larc.nasa.gov/api/temporal/climatology/point"
               f"?parameters=T2M_MAX,T2M_MIN&latitude={lat}&longitude={lon}"
               "&community=RE&format=JSON")
        js  = requests.get(url, timeout=12).json()
        json.dump(js, open(fn, "w"))
    else:
        js  = json.load(open(fn))
    p      = js["properties"]["parameter"]
    annual = (sum(p["T2M_MAX"].values()) + sum(p["T2M_MIN"].values())) / 24
    return round(float(annual), 2)

# ---------- reverse-geocode helper (lat,lon ➜ state) ----------
rev_cache = {}
def state_from_coord(lat, lon, geocode_rev):
    if pd.isna(lat) or pd.isna(lon): return None
    key = f"{lat:.5f},{lon:.5f}"
    if key in rev_cache: return rev_cache[key]
    try:
        loc = geocode_rev((lat, lon), timeout=8, addressdetails=True)
        st  = loc.raw["address"].get("state") if loc else None
    except Exception: st = None
    rev_cache[key] = st.title() if st else None
    return rev_cache[key]

# ---------- subdivision spelling fixes ----------
state_map = {
    "Andaman And Nicobar Islands": "Andaman & Nicobar Islands",
    "Andhra Pradesh":              "Coastal Andhra Pradesh",
    "Arunachal Pradesh":           "Arunachal Pradesh",
    "Assam":                       "Assam & Meghalaya",
    "Bihar":                       "Bihar",
    "Chhattisgarh":                "Chhattisgarh",
    "Delhi":                       "Haryana Delhi & Chandigarh",
    "Goa":                         "Konkan & Goa",
    "Gujarat":                     "Gujarat Region",
    "Haryana":                     "Haryana Delhi & Chandigarh",
    "Himachal Pradesh":            "Himachal Pradesh",
    "Jammu And Kashmir":           "Jammu & Kashmir",
    "Jharkhand":                   "Jharkhand",
    "Karnataka":                   "Coastal Karnataka",
    "Kerala":                      "Kerala",
    "Ladakh":                      "Jammu & Kashmir",
    "Madhya Pradesh":              "West Madhya Pradesh",
    "Maharashtra":                 "Madhya Maharashtra",
    "Manipur":                     "Naga Mani Mizo Tripura",
    "Meghalaya":                   "Assam & Meghalaya",
    "Mizoram":                     "Naga Mani Mizo Tripura",
    "Nagaland":                    "Naga Mani Mizo Tripura",
    "Odisha":                      "Orissa",
    "Puducherry":                  "Tamil Nadu",
    "Punjab":                      "Punjab",
    "Rajasthan":                   "East Rajasthan",
    "Sikkim":                      "Sub Himalayan West Bengal & Sikkim",
    "Tamil Nadu":                  "Tamil Nadu",
    "Telangana":                   "Telangana",
    "Tripura":                     "Naga Mani Mizo Tripura",
    "Uttar Pradesh":               "East Uttar Pradesh",
    "Uttarakhand":                 "Uttarakhand",
    "West Bengal":                 "Gangetic West Bengal",
}

# ───────────────────────── main ETL ─────────────────────────
def main():

    # optionally wipe caches
    if RESET_CACHE:
        if os.path.exists(GCACHE): os.remove(GCACHE)
        for f in os.listdir(CJSON):
            os.remove(os.path.join(CJSON, f))

    df = load_csv("Trails_data.csv")
    df.columns = df.columns.str.strip().str.lower()
    df["distance_km"], df["distance_mi"] = zip(*df["length"].map(parse_length))

    # build search string
    df["search"] = df.apply(lambda r:
        (r["location"] if pd.notna(r["location"]) else r["location.1"]) + ", India", axis=1)

    # ---------- forward geocode ----------
    cache  = json.load(open(GCACHE)) if os.path.exists(GCACHE) else {}
    geoloc = Nominatim(user_agent="trailiq_in")
    fwd    = RateLimiter(geoloc.geocode , min_delay_seconds=1)
    rev    = RateLimiter(geoloc.reverse, min_delay_seconds=1)

    hits = misses = 0
    for s in df["search"].unique():
        if s in cache and cache[s]["lat"] is not None: continue
        try:
            g = fwd(s, addressdetails=True, timeout=10)
            cache[s] = {"lat": g.latitude,
                         "lon": g.longitude,
                         "state": g.raw["address"].get("state")}
            hits += 1
        except Exception:
            cache[s] = {"lat": None, "lon": None, "state": None}
            misses += 1
    json.dump(cache, open(GCACHE,"w"))
    print(f"✔ geocoder hits {hits}   ✘ misses {misses}")

    # attach coords & initial state
    df["lat"]   = df["search"].map(lambda s: cache[s]["lat"])
    df["lon"]   = df["search"].map(lambda s: cache[s]["lon"])
    df["state"] = df["search"].map(lambda s: cache[s]["state"])

    # ---------- reverse geocode any “India/None” states ----------
    mask_bad = df["state"].isin(["India", None]) | df["state"].isna()
    print(f"↺ reverse-geocoding {mask_bad.sum()} fuzzy rows …")
    for idx, row in df[mask_bad].iterrows():
        st = state_from_coord(row.lat, row.lon, rev)
        if st: df.at[idx, "state"] = st

    # ---------- drop rows still missing coords ----------
    before = len(df)
    df = df.dropna(subset=["lat","lon"]).reset_index(drop=True)
    print(f"✂ dropped {before-len(df)} rows still lacking coords ⇒ {len(df)} remain")

    # ---------- normalise state spelling ----------
    df["state"] = df["state"].str.title().replace(state_map)

    # ---------- rainfall merge ----------
    rain = load_csv("rainfall in india 1901-2015.csv")
    rain["SUBDIVISION"] = rain["SUBDIVISION"].str.title()

    rain_mean = (rain.groupby("SUBDIVISION")[[
        "JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"
    ]].mean().mean(axis=1).rename("rain_longterm"))

    rain_best = (rain.groupby("SUBDIVISION")[[
        "JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"
    ]].mean().idxmin(axis=1).rename("best_month"))

    rain_stats = pd.concat([rain_mean, rain_best], axis=1)

    df = df.merge(rain_stats, left_on="state", right_index=True, how="left")

    #df = df.merge(rain_best, left_on="state", right_index=True, how="left")
    #df = df.merge(rain_mean, left_on="state", right_index=True, how="left")

    # ---------- tourism crowd-score ----------
    tour = load_csv("Tourism_In_India_Statistics_2018-Table_5.1.2_1.csv")
    tour = tour.rename(columns={"State/UT":"state","2017 - Domestic":"dom"})
    tour["state"] = tour["state"].str.title().replace(state_map)
    tour["crowd_score"] = (tour["dom"]-tour["dom"].min())/(tour["dom"].max()-tour["dom"].min())
    df = df.merge(tour[["state","crowd_score"]], on="state", how="left")

    # ---------- heat-index ----------
    df["heat_index"] = df.apply(
        lambda r: fetch_heat(r.lat,r.lon) if pd.notna(r.lat) else pd.NA, axis=1)

    # ---------- save ----------
    keep = ["trail_name","state","lat","lon",
            "distance_km","distance_mi",
            "difficulty","average_rating","number_of_reviews",
            "rain_longterm","crowd_score","heat_index", "best_month"]
    df[keep].to_parquet("data/clean_trails.parquet", index=False)
    print("Yes! wrote clean_trails.parquet", len(df), "rows")

if __name__ == "__main__":
    main()
