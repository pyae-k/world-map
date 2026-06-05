from __future__ import annotations

from typing import Any, Dict, Tuple

import requests
import streamlit as st

from world_map.config import CACHE_TTL_WEATHER, HTTP_HEADERS
from world_map.data import WEATHER_CODE_LABELS
from world_map.formatting import chunks, safe_float


def weather_label(code: Any) -> str:
    try:
        return WEATHER_CODE_LABELS.get(int(code), "Unknown")
    except (TypeError, ValueError):
        return "N/A"


def empty_weather(status: str = "Pending") -> Dict[str, Any]:
    return {
        "temperature_c": None,
        "humidity_pct": None,
        "wind_kmh": None,
        "condition": "Unavailable",
        "status": status,
    }


def parse_weather_item(item: Dict[str, Any]) -> Dict[str, Any]:
    current = item.get("current", {}) if isinstance(item, dict) else {}
    if current:
        code = current.get("weather_code")
        return {
            "temperature_c": safe_float(current.get("temperature_2m")),
            "humidity_pct": safe_float(current.get("relative_humidity_2m")),
            "wind_kmh": safe_float(current.get("wind_speed_10m")),
            "condition": weather_label(code),
            "status": "OK",
        }

    current_weather = item.get("current_weather", {}) if isinstance(item, dict) else {}
    if current_weather:
        code = current_weather.get("weathercode")
        return {
            "temperature_c": safe_float(current_weather.get("temperature")),
            "humidity_pct": None,
            "wind_kmh": safe_float(current_weather.get("windspeed")),
            "condition": weather_label(code),
            "status": "OK",
        }

    return empty_weather("Unavailable")


@st.cache_data(ttl=CACHE_TTL_WEATHER, show_spinner=False)
def fetch_weather(locations: Tuple[Tuple[str, str, float, float, str], ...]) -> Dict[str, Dict[str, Any]]:
    results: Dict[str, Dict[str, Any]] = {}
    for chunk in chunks(list(locations), 40):
        for country, location_name, *_ in chunk:
            results[f"{country}::{location_name}"] = empty_weather()

        latitudes = ",".join(str(row[2]) for row in chunk)
        longitudes = ",".join(str(row[3]) for row in chunk)
        params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        }

        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params=params,
                headers=HTTP_HEADERS,
                timeout=12,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            for country, location_name, *_ in chunk:
                results[f"{country}::{location_name}"]["status"] = f"Weather error: {exc}"
        else:
            payload_items = payload if isinstance(payload, list) else [payload]
            for location, item in zip(chunk, payload_items):
                country, location_name, *_ = location
                results[f"{country}::{location_name}"] = parse_weather_item(item)

        if all(results[f"{country}::{location_name}"]["status"] == "OK" for country, location_name, *_ in chunk):
            continue

        fallback_params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "current_weather": "true",
            "timezone": "auto",
        }
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params=fallback_params,
                headers=HTTP_HEADERS,
                timeout=12,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            continue

        payload_items = payload if isinstance(payload, list) else [payload]
        for location, item in zip(chunk, payload_items):
            country, location_name, *_ = location
            key = f"{country}::{location_name}"
            if results[key]["status"] != "OK":
                results[key] = parse_weather_item(item)

    return results
