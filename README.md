# ✈️ Airline Passenger Satisfaction Dashboard

🚀 **[View Live Dashboard](https://airline-passenger-satisfaction-dashboard-9enywzuzeprw4xh3aq969.streamlit.app/)**

An interactive Streamlit dashboard exploring airline passenger satisfaction, service quality, and flight delays.

**Current status:** Section 1 (Executive Overview) is complete. The other
sections are planned.

## Executive Overview

- Four KPI cards: total passengers, satisfaction rate, and average departure
  and arrival delay (median shown beneath each).
- Satisfaction donut chart with counts and percentages on hover.
- Grouped bar chart comparing departure and arrival delay categories.
- A "Data notes" panel that discloses excluded records and every denominator.

## Project structure

```
Airline_Passenger_Dashboard/
├── .streamlit/config.toml     # light theme colours
├── data/airline_cleaned.csv   # cleaned dataset (read-only, never modified)
├── app.py                     # the dashboard
├── requirements.txt
├── README.md
└── .gitignore
```

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## How the numbers are calculated

- **Blank records:** a record with no satisfaction answer and no departure or
  arrival delay is excluded from all calculations, and the count is shown.
  Partly filled records are kept; each metric skips only its own missing values.
- **Satisfaction rate:** satisfied passengers / passengers with a valid answer.
- **Delay categories** (built from the raw minute columns; upper bound inclusive):
  No delay = 0, Short = >0 to 60, Moderate = >60 to 180, Long = >180 to 360,
  Very long = >360.
- **Delay percentages:** each delay type uses its own count of valid
  observations as the denominator.

## Data

The dataset was cleaned beforehand in Google Colab. This app only reads it.
