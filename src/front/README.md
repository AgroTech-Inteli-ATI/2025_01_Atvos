# Streamlit Travel Dashboard

This Streamlit app consumes the Agro-Server API and turns travel data into an interactive dashboard focused on transportation costs.

## Features

- Summary cards with total cost, distance, trip count, and averages
- Cost evolution charts with optional distance breakdown
- Ranking of the most expensive travels
- Raw data table with CSV export
- Flexible filters: date range, unit, aggregation period, and record limit

## Prerequisites

- Python 3.10 or newer
- Agro-Server API running and reachable (default assumed: `http://localhost:8000/api`)

## Setup

```bash
cd src/front
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the dashboard

```bash
streamlit run streamlit_app.py
```

The app opens in your default browser. Use the sidebar to:

- Set the API base URL (`http://localhost:8000/api` by default)
- Provide an optional bearer token if your API requires authentication
- Choose the analysis period, date range, unit, and how many travels to fetch

### Environment variables (optional)

You can preconfigure defaults before launching Streamlit:

```bash
export AGRO_API_BASE_URL="https://your-api.example.com/api"
export AGRO_API_TOKEN="your-token"
streamlit run streamlit_app.py
```

## Tips

- The "Limpar cache de chamadas" button in the sidebar forces a fresh API fetch.
- If the API does not expose cost aggregates, the app tries to reconstruct costs from travel bills when available.
- Use the CSV download button to analyze the filtered dataset in external tools.
- When the backend is unavailable, activate "Usar dados simulados" in the sidebar to explore the dashboard with built-in mock data.
