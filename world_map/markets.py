from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple
from urllib.parse import quote

import requests
import streamlit as st

from world_map.config import CACHE_TTL_MARKET_CAPS, CACHE_TTL_MARKET_INDEX, HTTP_HEADERS
from world_map.formatting import chunks, safe_float


@st.cache_data(ttl=CACHE_TTL_MARKET_INDEX, show_spinner=False)
def fetch_market_index(symbol: str) -> Dict[str, Any]:
    encoded_symbol = quote(symbol, safe="")
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{encoded_symbol}?range=2y&interval=1d"
    empty_result = {
        "last_price": None,
        "avg_365": None,
        "vs_avg_pct": None,
        "currency": "",
        "market_time": "",
        "status": "Unavailable",
    }

    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=12)
        response.raise_for_status()
        payload = response.json()
        chart = payload.get("chart", {})
        error = chart.get("error")
        if error:
            empty_result["status"] = str(error.get("description") or error.get("code") or error)
            return empty_result
        result = (chart.get("result") or [None])[0]
        if not result:
            return empty_result
        meta = result.get("meta", {})
        closes = (
            result.get("indicators", {})
            .get("quote", [{}])[0]
            .get("close", [])
        )
        close_values = [safe_float(value) for value in closes]
        close_values = [value for value in close_values if value is not None]
        if not close_values:
            return empty_result
        last_price = safe_float(meta.get("regularMarketPrice")) or close_values[-1]
        recent_values = close_values[-365:]
        avg_365 = sum(recent_values) / len(recent_values) if recent_values else None
        vs_avg_pct = ((last_price - avg_365) / avg_365 * 100) if avg_365 else None
        market_time = ""
        timestamp = meta.get("regularMarketTime")
        if timestamp:
            market_time = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        return {
            "last_price": last_price,
            "avg_365": avg_365,
            "vs_avg_pct": vs_avg_pct,
            "currency": meta.get("currency") or "",
            "market_time": market_time,
            "status": "OK",
        }
    except Exception as exc:
        empty_result["status"] = f"Market error: {exc}"
        return empty_result


@st.cache_data(ttl=CACHE_TTL_MARKET_CAPS, show_spinner=False)
def fetch_country_market_caps(iso3_codes: Tuple[str, ...]) -> Dict[str, Dict[str, Any]]:
    if not iso3_codes:
        return {}

    market_caps: Dict[str, Dict[str, Any]] = {}
    for chunk in chunks(list(iso3_codes), 35):
        url = (
            "https://api.worldbank.org/v2/country/"
            + ";".join(chunk)
            + "/indicator/CM.MKT.LCAP.CD?format=json&per_page=1000&MRV=10"
        )
        try:
            response = requests.get(url, headers=HTTP_HEADERS, timeout=12)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            continue

        rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for row in rows:
            iso3 = row.get("countryiso3code")
            value = safe_float(row.get("value"))
            if not iso3 or value is None or iso3 in market_caps:
                continue
            market_caps[iso3] = {"value": value, "year": row.get("date", "")}
    return market_caps
