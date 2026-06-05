from __future__ import annotations

from html import escape
from typing import Any, Dict, List, Optional

import pydeck as pdk
import streamlit as st

from world_map.formatting import format_number, format_percent


def render_map(map_rows: List[Dict[str, Any]]) -> None:
    if not map_rows:
        st.info("No countries match the current filters.")
        return

    layer_points = pdk.Layer(
        "ScatterplotLayer",
        data=map_rows,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True,
    )
    layer_labels = pdk.Layer(
        "TextLayer",
        data=map_rows,
        get_position="[lon, lat]",
        get_text="label",
        get_size=11,
        get_color=[21, 31, 43],
        get_angle=0,
        get_pixel_offset=[0, -12],
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
        pickable=False,
    )
    view_state = pdk.ViewState(latitude=18, longitude=10, zoom=1.05, min_zoom=0.8, max_zoom=7)
    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=view_state,
        layers=[layer_points, layer_labels],
        tooltip={
            "html": (
                "<b>{country}</b><br/>"
                "{location}<br/>"
                "{time_label}<br/>"
                "{weather_label}<br/>"
                "{index_label}"
            ),
            "style": {"backgroundColor": "white", "color": "#18212f", "fontFamily": "Arial"},
        },
    )
    st.pydeck_chart(deck, use_container_width=True, height=560)


def delta_class(value: Optional[float]) -> str:
    if value is None:
        return "neutral"
    return "positive" if value >= 0 else "negative"


def render_focus_market_cards(rows: List[Dict[str, Any]]) -> None:
    columns = st.columns(len(rows))
    for column, row in zip(columns, rows):
        cap_year = f" ({escape(str(row.get('Cap year', '')))})" if row.get("Cap year") else ""
        price = format_number(row.get("Last price"))
        average = format_number(row.get("Avg price 365d"))
        comparison = row.get("Vs 365d avg %")
        with column:
            st.markdown(
                f"""
                <div class="market-card">
                    <div class="market-card-title">{escape(str(row["Country"]))}</div>
                    <div class="market-card-cap">{escape(str(row["Market cap label"]))}</div>
                    <div class="market-card-note">Listed market cap{cap_year}</div>
                    <div class="market-card-index">
                        {escape(str(row["Index"]))}: {price} {escape(str(row.get("Currency", "")))}
                    </div>
                    <div class="market-card-delta {delta_class(comparison)}">
                        {format_percent(comparison)} vs 365d avg
                    </div>
                    <div class="market-card-note">Avg price 365d: {average}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def style_page() -> None:
    st.markdown(
        """
        <style>
            .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
            .market-card {
                background: #f8fafb;
                border: 1px solid #d9e1e8;
                border-radius: 8px;
                min-height: 176px;
                padding: 1rem 1.05rem;
                color: #172033;
                box-shadow: 0 1px 2px rgba(26, 37, 51, 0.08);
            }
            .market-card-title {
                font-size: 1.02rem;
                font-weight: 700;
                line-height: 1.2;
                margin-bottom: 0.65rem;
            }
            .market-card-cap {
                font-size: 2rem;
                font-weight: 750;
                line-height: 1.1;
                margin-bottom: 0.25rem;
            }
            .market-card-index {
                font-size: 0.95rem;
                font-weight: 650;
                line-height: 1.3;
                margin-top: 0.8rem;
            }
            .market-card-delta {
                display: inline-block;
                font-size: 0.95rem;
                font-weight: 750;
                margin-top: 0.35rem;
            }
            .market-card-delta.positive { color: #126c50; }
            .market-card-delta.negative { color: #b33f35; }
            .market-card-delta.neutral { color: #556270; }
            .market-card-note {
                color: #596779;
                font-size: 0.78rem;
                line-height: 1.35;
            }
            div[data-testid="stDataFrame"] {
                border: 1px solid #e2e5e9;
                border-radius: 8px;
                overflow: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
