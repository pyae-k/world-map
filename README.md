# World Time, Weather, and Market Dashboard

A Streamlit dashboard that combines live local time, weather, and stock market data on an interactive world map. Filter countries by region, explore G7 market snapshots, and browse detailed tables for weather, markets, and time zones.

## Features

- **Interactive world map** — PyDeck map with location markers colored by index performance vs. 365-day average
- **G7 market snapshot** — At-a-glance cards for major economies (US, UK, EU, Japan)
- **Live weather** — Current conditions from [Open-Meteo](https://open-meteo.com/) for cities worldwide
- **Market indices** — Latest prices and 365-day comparisons from Yahoo Finance chart data
- **Country market caps** — Listed market capitalization from World Bank data
- **Sidebar filters** — Search countries, filter by region, limit results, and refresh cached data

## Requirements

- Python 3.9 or newer (uses stdlib `zoneinfo`)
- Internet access for live API data

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run world_map.py
```

The app opens in your browser at `http://localhost:8501`.

## Project structure

```
world-map/
├── world_map/              # Python package
│   ├── data.py             # Country, G7, and weather code datasets
│   ├── config.py           # HTTP headers and cache TTL constants
│   ├── formatting.py       # Number, time, and currency formatters
│   ├── weather.py          # Open-Meteo API client
│   ├── markets.py          # Yahoo Finance and World Bank API clients
│   ├── builders.py         # DataFrame and map row builders
│   ├── filters.py          # Country search and region filters
│   └── ui.py               # Map, cards, and page styling
├── world_map.py            # Streamlit entry point
├── requirements.txt
├── .streamlit/config.toml
└── scripts/package.sh      # Build upload-ready zip archive
```

## Configuration

Use the sidebar to:

- Search countries by name
- Filter by geographic region
- Limit how many countries appear on the map
- Show only countries with a stock market index
- **Refresh live data** — clears Streamlit cache and reloads all API data

Cache TTLs (in `world_map/config.py`):

| Data source | TTL |
|-------------|-----|
| Weather | 10 minutes |
| Market index | 15 minutes |
| Country market cap | 12 hours |

## Data sources

| Data | Provider | Endpoint / Indicator |
|------|----------|----------------------|
| Weather | [Open-Meteo](https://open-meteo.com/) | `/v1/forecast` |
| Index prices | Yahoo Finance | Chart API (`query2.finance.yahoo.com`) |
| Market capitalization | [World Bank](https://data.worldbank.org/) | `CM.MKT.LCAP.CD` |

No API keys are required. All data is fetched on demand and cached by Streamlit.

## Upload to GitHub

### Option A: Zip upload

```bash
bash scripts/package.sh
```

Upload `world-map-upload.zip` to a new GitHub repository via the web UI.

### Option B: Git push

```bash
git init
git add .
git commit -m "Initial commit: modular Streamlit world map dashboard"
git branch -M main
git remote add origin https://github.com/<user>/world-map.git
git push -u origin main
```

## Copyright

Built by **Pyae Phyo Kyaw** — [pyaek@icloud.com](mailto:pyaek@icloud.com)

All rights reserved.
