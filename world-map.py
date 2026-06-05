from __future__ import annotations

import warnings
from datetime import datetime, timezone

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")

import pandas as pd
import streamlit as st

from world_map.builders import (
    build_focus_market_rows,
    build_map_rows,
    build_market_rows,
    build_time_rows,
    build_weather_rows,
)
from world_map.data import COUNTRIES, G7_MARKET_CARDS
from world_map.filters import country_options, flatten_locations
from world_map.markets import fetch_country_market_caps
from world_map.ui import render_focus_market_cards, render_map, style_page
from world_map.weather import fetch_weather


def main() -> None:
    st.set_page_config(
        page_title="World Time Weather Markets",
        page_icon="W",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    style_page()

    st.title("World Time, Weather, and Market Dashboard")

    regions = sorted({item["region"] for item in COUNTRIES})
    with st.sidebar:
        st.header("Filters")
        query = st.text_input("Country search", "")
        selected_regions = st.multiselect("Regions", regions, default=regions)
        max_countries = st.slider("Countries shown", 5, len(COUNTRIES), min(24, len(COUNTRIES)))
        show_markets_only = st.checkbox("Only countries with an index", value=False)
        if st.button("Refresh live data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.divider()
        st.caption("Built by Pyae Phyo Kyaw • pyaek@icloud.com")

    filtered = country_options(query, selected_regions)
    if show_markets_only:
        filtered = [item for item in filtered if item.get("index")]
    selected_countries = filtered[:max_countries]

    location_count = sum(len(item["locations"]) for item in selected_countries)
    index_count = sum(1 for item in selected_countries if item.get("index"))

    locations = flatten_locations(selected_countries)
    iso3_codes = tuple(
        sorted({item["iso3"] for item in selected_countries} | {item["iso3"] for item in G7_MARKET_CARDS})
    )

    with st.spinner("Loading live weather and market data..."):
        weather = fetch_weather(locations)
        market_caps = fetch_country_market_caps(iso3_codes)
        market_rows = build_market_rows(selected_countries, market_caps)
        focus_market_rows = build_focus_market_rows(market_caps)

    map_rows = build_map_rows(selected_countries, weather, market_rows)

    st.subheader("G7 Market Snapshot")
    render_focus_market_cards(focus_market_rows)

    st.caption(
        f"Map selection: {len(selected_countries)} countries, {location_count} weather/time points, "
        f"{index_count} market indices. UTC {datetime.now(timezone.utc).strftime('%H:%M')}."
    )

    st.subheader("World Map")
    render_map(map_rows)

    tab_weather, tab_markets, tab_times = st.tabs(["Weather", "Markets", "Times"])

    weather_df = pd.DataFrame(build_weather_rows(selected_countries, weather))
    market_df = pd.DataFrame(market_rows)
    time_df = pd.DataFrame(build_time_rows(selected_countries))

    with tab_weather:
        st.dataframe(
            weather_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Temp C": st.column_config.NumberColumn("Temp C", format="%.1f"),
                "Humidity %": st.column_config.NumberColumn("Humidity %", format="%.0f"),
                "Wind km/h": st.column_config.NumberColumn("Wind km/h", format="%.1f"),
            },
        )

    with tab_markets:
        st.dataframe(
            market_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Last price": st.column_config.NumberColumn("Last price", format="%.2f"),
                "Avg price 365d": st.column_config.NumberColumn("Avg price 365d", format="%.2f"),
                "Vs 365d avg %": st.column_config.NumberColumn("Vs 365d avg %", format="%+.2f%%"),
            },
        )

    with tab_times:
        st.dataframe(time_df, width="stretch", hide_index=True)

    st.caption(
        "Weather: Open-Meteo. Index price/history: Yahoo chart data. "
        "Country market cap: World Bank CM.MKT.LCAP.CD latest available annual value."
    )


if __name__ == "__main__":
    main()
