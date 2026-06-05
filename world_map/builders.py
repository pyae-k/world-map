from __future__ import annotations

from typing import Any, Dict, List

from world_map.data import G7_MARKET_CARDS
from world_map.formatting import format_full_time, format_number, format_percent, format_time, format_usd_compact
from world_map.markets import fetch_market_index


def first_weather_for_country(country: Dict[str, Any], weather: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    first_location = country["locations"][0][0]
    return weather.get(f"{country['country']}::{first_location}", {})


def build_weather_rows(
    countries: List[Dict[str, Any]], weather: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    rows = []
    for item in countries:
        for location_name, _lat, _lon, tz_name in item["locations"]:
            current = weather.get(f"{item['country']}::{location_name}", {})
            rows.append(
                {
                    "Country": item["country"],
                    "Location": location_name,
                    "Local time": format_full_time(tz_name),
                    "Condition": current.get("condition", "Unavailable"),
                    "Temp C": current.get("temperature_c"),
                    "Humidity %": current.get("humidity_pct"),
                    "Wind km/h": current.get("wind_kmh"),
                    "Status": current.get("status", "Unavailable"),
                }
            )
    return rows


def build_market_rows(
    countries: List[Dict[str, Any]], market_caps: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    rows = []
    for item in countries:
        index = item.get("index")
        cap = market_caps.get(item["iso3"], {})
        market = fetch_market_index(index["symbol"]) if index else {}
        rows.append(
            {
                "Country": item["country"],
                "Index": index["name"] if index else "N/A",
                "Symbol": index["symbol"] if index else "N/A",
                "Last price": market.get("last_price"),
                "Currency": market.get("currency", ""),
                "Avg price 365d": market.get("avg_365"),
                "Vs 365d avg %": market.get("vs_avg_pct"),
                "Country market cap": format_usd_compact(cap.get("value")),
                "Cap year": cap.get("year", ""),
                "Updated": market.get("market_time", ""),
                "Status": market.get("status", "No index"),
            }
        )
    return rows


def build_focus_market_rows(market_caps: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for item in G7_MARKET_CARDS:
        cap = market_caps.get(item["iso3"], {})
        market = fetch_market_index(item["symbol"])
        rows.append(
            {
                "Country": item["title"],
                "Index": item["index_name"],
                "Symbol": item["symbol"],
                "Last price": market.get("last_price"),
                "Currency": market.get("currency", ""),
                "Avg price 365d": market.get("avg_365"),
                "Vs 365d avg %": market.get("vs_avg_pct"),
                "Market cap": cap.get("value"),
                "Market cap label": format_usd_compact(cap.get("value")),
                "Cap year": cap.get("year", ""),
                "Updated": market.get("market_time", ""),
                "Status": market.get("status", "Unavailable"),
            }
        )
    return rows


def build_time_rows(countries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows = []
    for item in countries:
        for location_name, _lat, _lon, tz_name in item["locations"]:
            rows.append(
                {
                    "Country": item["country"],
                    "Location": location_name,
                    "Region": item["region"],
                    "Timezone": tz_name,
                    "Local time": format_full_time(tz_name),
                }
            )
    return rows


def build_map_rows(
    countries: List[Dict[str, Any]],
    weather: Dict[str, Dict[str, Any]],
    market_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    market_by_country = {row["Country"]: row for row in market_rows}
    rows = []
    location_total = sum(len(item["locations"]) for item in countries)
    for item in countries:
        market = market_by_country.get(item["country"], {})
        index_percent = market.get("Vs 365d avg %")
        marker_color = [42, 157, 143, 190]
        if index_percent is not None and index_percent < 0:
            marker_color = [214, 91, 75, 190]
        elif index_percent is not None and index_percent >= 0:
            marker_color = [50, 130, 184, 190]

        for location_name, lat, lon, tz_name in item["locations"]:
            current_weather = weather.get(f"{item['country']}::{location_name}", {})
            temperature = current_weather.get("temperature_c")
            condition = current_weather.get("condition", "Unavailable")
            rows.append(
                {
                    "country": item["country"],
                    "location": location_name,
                    "lat": lat,
                    "lon": lon,
                    "label": f"{location_name}\n{format_time(tz_name)}",
                    "time_label": format_full_time(tz_name),
                    "weather_label": (
                        f"{format_number(temperature, 1)} C, {condition}"
                        if temperature is not None
                        else condition
                    ),
                    "index_label": (
                        f"{market.get('Index', 'Index')}: {format_number(market.get('Last price'))} "
                        f"{market.get('Currency', '')} ({format_percent(index_percent)} vs 365d avg)"
                    ),
                    "fill_color": marker_color,
                    "radius": 120000 if location_total <= 30 else 85000,
                }
            )
    return rows
