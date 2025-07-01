# 🏔️ TrailIQ-IN

**Find your perfect Indian trek through data-driven insight.**

TrailIQ-IN is a full-stack web application designed for trekking enthusiasts to explore, 
compare, and discover over 300 treks across India. By combining climatology data from NASA, 
rainfall data from the IMD, and tourism statistics, this platform provides unique analytical views 
to help users find treks that match their preferences for climate, difficulty, and seasonality.

---

## Features

The core of TrailIQ is an interactive dashboard with four dynamically linked visualizations:

| Visual                  | What You Learn                                                  |
| ----------------------- | --------------------------------------------------------------- |
| **Heat-Index Map** | See all 311 treks plotted on a map, colored by long-term mean air temperature. |
| **Distance × Rating Scatter** | Discover underrated gems (low distance, high rating) or elite endurance challenges. |
| **Climate Histogram** | Understand the overall climatic spread of treks, from cool alpine routes to warm coastal paths. |
| **Crowd-Score Leaderboard** | See which states have the highest relative tourist load, based on 2018 tourism statistics. |

---

## Tech Stack

* **Frontend:** React, Vite, Figma/Lottie for animations
* **Backend & Data Viz:** Python, Flask, Dash/Plotly
* **Data Processing:** Pandas, GeoPy
* **DevOps:** Docker

---

## Getting Started

You can run TrailIQ-IN using Docker (recommended for ease of use) or by setting up the frontend and backend locally.

### Using Docker (Recommended)

This is the simplest way to get the entire application running.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/)hrithikdevaiah-999/trailiq-in.git
    cd trailiq-in
    ```

2.  **Run the data pipeline first:**
    The `docker-compose` setup is configured to use the pre-processed data file. Ensure you run the ETL script at least once to generate it.
    ```bash
    python backend/etl/load_trails.py
    ```

3.  **Build and run the containers:**
    This command will build the images for the frontend and backend services and start them up.
    ```bash
    docker-compose build
    docker-compose up
    ```

4.  **Access the application:**
    * The **React landing page** will be available at `http://localhost:3001`.
    * Click the "Launch App" button to open the **Dash analytics dashboard**.


---

## Data Pipeline (ETL)

The core data processing is handled by the `backend/etl/load_trails.py` script. This script must be run before starting the application for the first time.

**What it does:**
* Parses the raw trek data from CSV.
* Geocodes trek locations and caches the results to avoid repeated API calls.
* Enriches the data with climatology information from NASA POWER and rainfall data from IMD.
* Adds a `crowd_score` based on 2018 tourism statistics.
* Cleans the data and outputs a single, analysis-ready `data/clean_trails.parquet` file with **311 rows and 0 NULLs** in key columns.
