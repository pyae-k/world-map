from __future__ import annotations

from typing import Any, Dict, List, Tuple

from world_map.data import COUNTRIES


def flatten_locations(countries: List[Dict[str, Any]]) -> Tuple[Tuple[str, str, float, float, str], ...]:
    rows: List[Tuple[str, str, float, float, str]] = []
    for item in countries:
        for location_name, lat, lon, tz_name in item["locations"]:
            rows.append((item["country"], location_name, lat, lon, tz_name))
    return tuple(rows)


def country_options(query: str, selected_regions: List[str]) -> List[Dict[str, Any]]:
    normalized_query = query.strip().lower()
    countries = []
    for item in COUNTRIES:
        if selected_regions and item["region"] not in selected_regions:
            continue
        if normalized_query and normalized_query not in item["country"].lower():
            continue
        countries.append(item)
    return countries
