import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.io as pio
import json, os
import numpy as np

pio.templates.default = "plotly_white"

DATA = pd.read_parquet("data/clean_trails.parquet")

app = Dash(__name__)

def card(children):
    return html.Div(children, style={
        "border":"2px solid #2E3B4E",
        "borderRadius":"8px",
        "padding":"12px",
        "margin":"8px",
        "backgroundColor":"#FAFAFA",
        "boxShadow":"2px 2px 5px rgba(0,0,0,0.1)",
        "flex": "1 1 45%",     # grow / shrink / basis 45%
        "minWidth": "300px"
    })

app.layout = html.Div([
    html.Div([
        html.H3("TrailIQ-IN Dashboard", style={"margin":"0 16px", "color":"#2E3B4E", "whiteSpace":"nowrap"}),
        html.Label("Search trek by name", htmlFor="search", 
               style={"position":"absolute","left":"-10000px","top":"auto","width":"1px","height":"1px","overflow":"hidden"}),
        dcc.Input(id="search", type="text", placeholder="Search trek…", style={"minWidth":"220px", "padding":"6px 8px"}),
        dcc.Dropdown(id="difficulty", options=[{"label": d, "value": d} 
                          for d in sorted(DATA["difficulty"].dropna().unique())], 
                 placeholder="Filter difficulty",
                 style={"minWidth":"160px"})
    ], style={"display":"flex", "alignItems":"center", "justifyContent":"center", "gap":"12px", "padding":"12px 8px", "flexWrap":"wrap"}),
    html.Div([
        card(dcc.Graph(id="map", config={"displayModeBar":False}, style={"height": "360px", "paddingBottom": "40px"})),
        card(dcc.Graph(id="scatter", config={"displayModeBar":False}))
    ], style={"display":"flex","flexWrap":"wrap","justifyContent":"center"}),
    html.Div([
        card(dcc.Graph(id="heat", config={"displayModeBar":False})),
        card(dcc.Graph(id="crowd", config={"displayModeBar":False}))
    ], style={"display":"flex","flexWrap":"wrap","justifyContent":"center"}),
])

@app.callback(
    Output("map", "figure"),
    Output("scatter", "figure"),
    Output("heat", "figure"),
    Output("crowd", "figure"),
    Input("difficulty", "value"),
    Input("search", "value")
)
def update_graphs(diff, search):
    #filtering the df
    df = DATA.copy()
    if search:
        df = df[df["trail_name"].str.contains(search, case=False, na=False)]
    if diff:
        df = df[df["difficulty"] == diff]

    df_num = df.copy()                       # helper for numeric casts
    df_num["heat_index"]   = pd.to_numeric(df["heat_index"],   errors="coerce")
    df_num["crowd_score"]  = pd.to_numeric(df["crowd_score"],  errors="coerce")

    #mapviz-----------------------------------------------------------
    df_plot = df.copy()
    rng = np.random.default_rng(seed=42)          # repeatable
    df_plot['lat_jit'] = df_plot['lat'] + rng.normal(0, 0.05, len(df_plot))
    df_plot['lon_jit'] = df_plot['lon'] + rng.normal(0, 0.05, len(df_plot))



    india_center = {"lat": 22.5, "lon": 78.5}
    fig_map = px.scatter_map(
        df_plot,
        lat="lat_jit", 
        lon="lon_jit",
        hover_name="trail_name",
        color="heat_index",
        custom_data=["lat","lon","heat_index","best_month"],
        color_continuous_scale="Rainbow", #old - RdYlBu_r, Viridus
        zoom=3, 
        height=350, 
        center=india_center
    )
    fig_map.update_traces(
        marker_size=9,
        marker_opacity=0.8,
        

        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Lat: %{customdata[0]:.3f}<br>"
            "Lon: %{customdata[1]:.3f}<br>"
            "Heat index: %{customdata[2]:.1f}°C<br>"
            "Best month: %{customdata[3]}<extra></extra>"
        )
    )
    fig_map.update_layout(map_style="open-street-map", margin=dict(l=0,r=0,t=0,b=0))
    print("Map points actually sent to front-end(lat):", len(fig_map.data[0]["lat"]))
    print("Map points actually sent to front-end(lon):", len(fig_map.data[0]["lon"]))
    #distancevsrating-----------------------------------------------------------
    fig_scatter = px.scatter(
        df, x="distance_km", y="average_rating",
        color="difficulty", 
        hover_name="trail_name",
        labels={"distance_km":"Distance (km)", "average_rating":"Rating"},
        height=350
    )
    fig_scatter.update_layout(
        legend_title="Difficulty",
        legend=dict(bordercolor="#2E3B4E", borderwidth=1)
    )

    #heatindexhistogram-----------------------------------------------------------
    hi_ok = df_num.dropna(subset=["heat_index"])
    if hi_ok.empty:
        fig_heat = px.scatter(title="No heat-index data")
    else:
        fig_heat = px.histogram(
            hi_ok, x="heat_index", nbins=20,
            title="Heat-index distribution", height=400
        )
        fig_heat.update_traces(marker_color="#2E7D32")

    #crowdscorebarchart-----------------------------------------------------------
    cs_ok = df_num.dropna(subset=["crowd_score"])
    if cs_ok.empty:
        fig_crowd = px.scatter(title="No crowd data")
    else:
        state_avg = (
            cs_ok.groupby("state")["crowd_score"]
            .mean().nlargest(10).reset_index()
        )
        fig_crowd = px.bar(
            state_avg, x="state", y="crowd_score",
            title="Avg crowd-score (top 10 states)", height=400
        )
        fig_crowd.update_traces(marker_color="#1565C0")

    return fig_map, fig_scatter, fig_heat, fig_crowd

server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)