from __future__ import annotations

import math
import warnings
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
from html import escape
from urllib.parse import quote
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st


COUNTRIES: List[Dict[str, Any]] = [
    {
        "country": "United States",
        "iso3": "USA",
        "region": "North America",
        "lat": 39.8283,
        "lon": -98.5795,
        "timezone": "America/New_York",
        "locations": [
            ("New York", 40.7128, -74.0060, "America/New_York"),
            ("Chicago", 41.8781, -87.6298, "America/Chicago"),
            ("Los Angeles", 34.0522, -118.2437, "America/Los_Angeles"),
        ],
        "index": {"name": "S&P 500", "symbol": "^GSPC"},
    },
    {
        "country": "Canada",
        "iso3": "CAN",
        "region": "North America",
        "lat": 56.1304,
        "lon": -106.3468,
        "timezone": "America/Toronto",
        "locations": [
            ("Toronto", 43.6532, -79.3832, "America/Toronto"),
            ("Vancouver", 49.2827, -123.1207, "America/Vancouver"),
            ("Calgary", 51.0447, -114.0719, "America/Edmonton"),
        ],
        "index": {"name": "S&P/TSX Composite", "symbol": "^GSPTSE"},
    },
    {
        "country": "Mexico",
        "iso3": "MEX",
        "region": "North America",
        "lat": 23.6345,
        "lon": -102.5528,
        "timezone": "America/Mexico_City",
        "locations": [("Mexico City", 19.4326, -99.1332, "America/Mexico_City")],
        "index": {"name": "S&P/BMV IPC", "symbol": "^MXX"},
    },
    {
        "country": "Brazil",
        "iso3": "BRA",
        "region": "South America",
        "lat": -14.2350,
        "lon": -51.9253,
        "timezone": "America/Sao_Paulo",
        "locations": [
            ("Sao Paulo", -23.5558, -46.6396, "America/Sao_Paulo"),
            ("Brasilia", -15.7939, -47.8828, "America/Sao_Paulo"),
            ("Manaus", -3.1190, -60.0217, "America/Manaus"),
        ],
        "index": {"name": "Bovespa", "symbol": "^BVSP"},
    },
    {
        "country": "Argentina",
        "iso3": "ARG",
        "region": "South America",
        "lat": -38.4161,
        "lon": -63.6167,
        "timezone": "America/Argentina/Buenos_Aires",
        "locations": [
            ("Buenos Aires", -34.6037, -58.3816, "America/Argentina/Buenos_Aires")
        ],
        "index": {"name": "MERVAL", "symbol": "^MERV"},
    },
    {
        "country": "Chile",
        "iso3": "CHL",
        "region": "South America",
        "lat": -35.6751,
        "lon": -71.5430,
        "timezone": "America/Santiago",
        "locations": [("Santiago", -33.4489, -70.6693, "America/Santiago")],
        "index": {"name": "S&P IPSA", "symbol": "^IPSA"},
    },
    {
        "country": "United Kingdom",
        "iso3": "GBR",
        "region": "Europe",
        "lat": 55.3781,
        "lon": -3.4360,
        "timezone": "Europe/London",
        "locations": [("London", 51.5072, -0.1276, "Europe/London")],
        "index": {"name": "FTSE 100", "symbol": "^FTSE"},
    },
    {
        "country": "Germany",
        "iso3": "DEU",
        "region": "Europe",
        "lat": 51.1657,
        "lon": 10.4515,
        "timezone": "Europe/Berlin",
        "locations": [("Berlin", 52.5200, 13.4050, "Europe/Berlin")],
        "index": {"name": "DAX", "symbol": "^GDAXI"},
    },
    {
        "country": "France",
        "iso3": "FRA",
        "region": "Europe",
        "lat": 46.2276,
        "lon": 2.2137,
        "timezone": "Europe/Paris",
        "locations": [("Paris", 48.8566, 2.3522, "Europe/Paris")],
        "index": {"name": "CAC 40", "symbol": "^FCHI"},
    },
    {
        "country": "Spain",
        "iso3": "ESP",
        "region": "Europe",
        "lat": 40.4637,
        "lon": -3.7492,
        "timezone": "Europe/Madrid",
        "locations": [("Madrid", 40.4168, -3.7038, "Europe/Madrid")],
        "index": {"name": "IBEX 35", "symbol": "^IBEX"},
    },
    {
        "country": "Italy",
        "iso3": "ITA",
        "region": "Europe",
        "lat": 41.8719,
        "lon": 12.5674,
        "timezone": "Europe/Rome",
        "locations": [("Rome", 41.9028, 12.4964, "Europe/Rome")],
        "index": {"name": "FTSE MIB", "symbol": "FTSEMIB.MI"},
    },
    {
        "country": "Netherlands",
        "iso3": "NLD",
        "region": "Europe",
        "lat": 52.1326,
        "lon": 5.2913,
        "timezone": "Europe/Amsterdam",
        "locations": [("Amsterdam", 52.3676, 4.9041, "Europe/Amsterdam")],
        "index": {"name": "AEX", "symbol": "^AEX"},
    },
    {
        "country": "Switzerland",
        "iso3": "CHE",
        "region": "Europe",
        "lat": 46.8182,
        "lon": 8.2275,
        "timezone": "Europe/Zurich",
        "locations": [("Zurich", 47.3769, 8.5417, "Europe/Zurich")],
        "index": {"name": "Swiss Market Index", "symbol": "^SSMI"},
    },
    {
        "country": "Sweden",
        "iso3": "SWE",
        "region": "Europe",
        "lat": 60.1282,
        "lon": 18.6435,
        "timezone": "Europe/Stockholm",
        "locations": [("Stockholm", 59.3293, 18.0686, "Europe/Stockholm")],
        "index": {"name": "OMX Stockholm 30", "symbol": "^OMX"},
    },
    {
        "country": "Norway",
        "iso3": "NOR",
        "region": "Europe",
        "lat": 60.4720,
        "lon": 8.4689,
        "timezone": "Europe/Oslo",
        "locations": [("Oslo", 59.9139, 10.7522, "Europe/Oslo")],
        "index": {"name": "Oslo Bors Benchmark", "symbol": "OSEBX.OL"},
    },
    {
        "country": "Poland",
        "iso3": "POL",
        "region": "Europe",
        "lat": 51.9194,
        "lon": 19.1451,
        "timezone": "Europe/Warsaw",
        "locations": [("Warsaw", 52.2297, 21.0122, "Europe/Warsaw")],
        "index": {"name": "WIG20", "symbol": "^WIG20"},
    },
    {
        "country": "Turkey",
        "iso3": "TUR",
        "region": "Europe / Asia",
        "lat": 38.9637,
        "lon": 35.2433,
        "timezone": "Europe/Istanbul",
        "locations": [("Istanbul", 41.0082, 28.9784, "Europe/Istanbul")],
        "index": {"name": "BIST 100", "symbol": "XU100.IS"},
    },
    {
        "country": "Russia",
        "iso3": "RUS",
        "region": "Europe / Asia",
        "lat": 61.5240,
        "lon": 105.3188,
        "timezone": "Europe/Moscow",
        "locations": [
            ("Moscow", 55.7558, 37.6173, "Europe/Moscow"),
            ("Yekaterinburg", 56.8389, 60.6057, "Asia/Yekaterinburg"),
            ("Vladivostok", 43.1155, 131.8855, "Asia/Vladivostok"),
        ],
        "index": {"name": "MOEX Russia", "symbol": "IMOEX.ME"},
    },
    {
        "country": "China",
        "iso3": "CHN",
        "region": "Asia",
        "lat": 35.8617,
        "lon": 104.1954,
        "timezone": "Asia/Shanghai",
        "locations": [
            ("Beijing", 39.9042, 116.4074, "Asia/Shanghai"),
            ("Shanghai", 31.2304, 121.4737, "Asia/Shanghai"),
            ("Chengdu", 30.5728, 104.0668, "Asia/Shanghai"),
        ],
        "index": {"name": "SSE Composite", "symbol": "000001.SS"},
    },
    {
        "country": "Hong Kong",
        "iso3": "HKG",
        "region": "Asia",
        "lat": 22.3193,
        "lon": 114.1694,
        "timezone": "Asia/Hong_Kong",
        "locations": [("Hong Kong", 22.3193, 114.1694, "Asia/Hong_Kong")],
        "index": {"name": "Hang Seng", "symbol": "^HSI"},
    },
    {
        "country": "Japan",
        "iso3": "JPN",
        "region": "Asia",
        "lat": 36.2048,
        "lon": 138.2529,
        "timezone": "Asia/Tokyo",
        "locations": [("Tokyo", 35.6762, 139.6503, "Asia/Tokyo")],
        "index": {"name": "Nikkei 225", "symbol": "^N225"},
    },
    {
        "country": "South Korea",
        "iso3": "KOR",
        "region": "Asia",
        "lat": 35.9078,
        "lon": 127.7669,
        "timezone": "Asia/Seoul",
        "locations": [("Seoul", 37.5665, 126.9780, "Asia/Seoul")],
        "index": {"name": "KOSPI", "symbol": "^KS11"},
    },
    {
        "country": "India",
        "iso3": "IND",
        "region": "Asia",
        "lat": 20.5937,
        "lon": 78.9629,
        "timezone": "Asia/Kolkata",
        "locations": [
            ("Mumbai", 19.0760, 72.8777, "Asia/Kolkata"),
            ("Delhi", 28.6139, 77.2090, "Asia/Kolkata"),
            ("Bengaluru", 12.9716, 77.5946, "Asia/Kolkata"),
        ],
        "index": {"name": "NIFTY 50", "symbol": "^NSEI"},
    },
    {
        "country": "Singapore",
        "iso3": "SGP",
        "region": "Asia",
        "lat": 1.3521,
        "lon": 103.8198,
        "timezone": "Asia/Singapore",
        "locations": [("Singapore", 1.3521, 103.8198, "Asia/Singapore")],
        "index": {"name": "Straits Times", "symbol": "^STI"},
    },
    {
        "country": "Thailand",
        "iso3": "THA",
        "region": "Asia",
        "lat": 15.8700,
        "lon": 100.9925,
        "timezone": "Asia/Bangkok",
        "locations": [("Bangkok", 13.7563, 100.5018, "Asia/Bangkok")],
        "index": {"name": "SET Index", "symbol": "^SET.BK"},
    },
    {
        "country": "Indonesia",
        "iso3": "IDN",
        "region": "Asia",
        "lat": -0.7893,
        "lon": 113.9213,
        "timezone": "Asia/Jakarta",
        "locations": [
            ("Jakarta", -6.2088, 106.8456, "Asia/Jakarta"),
            ("Surabaya", -7.2575, 112.7521, "Asia/Jakarta"),
            ("Makassar", -5.1477, 119.4327, "Asia/Makassar"),
        ],
        "index": {"name": "Jakarta Composite", "symbol": "^JKSE"},
    },
    {
        "country": "Malaysia",
        "iso3": "MYS",
        "region": "Asia",
        "lat": 4.2105,
        "lon": 101.9758,
        "timezone": "Asia/Kuala_Lumpur",
        "locations": [("Kuala Lumpur", 3.1390, 101.6869, "Asia/Kuala_Lumpur")],
        "index": {"name": "FTSE Bursa Malaysia KLCI", "symbol": "^KLSE"},
    },
    {
        "country": "Philippines",
        "iso3": "PHL",
        "region": "Asia",
        "lat": 12.8797,
        "lon": 121.7740,
        "timezone": "Asia/Manila",
        "locations": [("Manila", 14.5995, 120.9842, "Asia/Manila")],
        "index": {"name": "PSEi", "symbol": "PSEI.PS"},
    },
    {
        "country": "Vietnam",
        "iso3": "VNM",
        "region": "Asia",
        "lat": 14.0583,
        "lon": 108.2772,
        "timezone": "Asia/Ho_Chi_Minh",
        "locations": [("Ho Chi Minh City", 10.8231, 106.6297, "Asia/Ho_Chi_Minh")],
        "index": {"name": "VN Index", "symbol": "^VNINDEX"},
    },
    {
        "country": "Australia",
        "iso3": "AUS",
        "region": "Oceania",
        "lat": -25.2744,
        "lon": 133.7751,
        "timezone": "Australia/Sydney",
        "locations": [
            ("Sydney", -33.8688, 151.2093, "Australia/Sydney"),
            ("Perth", -31.9523, 115.8613, "Australia/Perth"),
            ("Brisbane", -27.4698, 153.0251, "Australia/Brisbane"),
        ],
        "index": {"name": "S&P/ASX 200", "symbol": "^AXJO"},
    },
    {
        "country": "New Zealand",
        "iso3": "NZL",
        "region": "Oceania",
        "lat": -40.9006,
        "lon": 174.8860,
        "timezone": "Pacific/Auckland",
        "locations": [("Auckland", -36.8509, 174.7645, "Pacific/Auckland")],
        "index": {"name": "NZX 50", "symbol": "^NZ50"},
    },
    {
        "country": "South Africa",
        "iso3": "ZAF",
        "region": "Africa",
        "lat": -30.5595,
        "lon": 22.9375,
        "timezone": "Africa/Johannesburg",
        "locations": [
            ("Johannesburg", -26.2041, 28.0473, "Africa/Johannesburg"),
            ("Cape Town", -33.9249, 18.4241, "Africa/Johannesburg"),
        ],
        "index": {"name": "FTSE/JSE Top 40", "symbol": "^J200.JO"},
    },
    {
        "country": "Egypt",
        "iso3": "EGY",
        "region": "Africa",
        "lat": 26.8206,
        "lon": 30.8025,
        "timezone": "Africa/Cairo",
        "locations": [("Cairo", 30.0444, 31.2357, "Africa/Cairo")],
        "index": {"name": "EGX 30", "symbol": "CASE30.CA"},
    },
    {
        "country": "Saudi Arabia",
        "iso3": "SAU",
        "region": "Middle East",
        "lat": 23.8859,
        "lon": 45.0792,
        "timezone": "Asia/Riyadh",
        "locations": [("Riyadh", 24.7136, 46.6753, "Asia/Riyadh")],
        "index": {"name": "Tadawul All Share", "symbol": "^TASI.SR"},
    },
    {
        "country": "United Arab Emirates",
        "iso3": "ARE",
        "region": "Middle East",
        "lat": 23.4241,
        "lon": 53.8478,
        "timezone": "Asia/Dubai",
        "locations": [("Dubai", 25.2048, 55.2708, "Asia/Dubai")],
        "index": {"name": "Dubai Financial Market", "symbol": "DFMGI.AE"},
    },
]


G7_MARKET_CARDS: List[Dict[str, str]] = [
    {
        "title": "United States",
        "iso3": "USA",
        "index_name": "S&P 500",
        "symbol": "^GSPC",
    },
    {
        "title": "United Kingdom",
        "iso3": "GBR",
        "index_name": "FTSE 100",
        "symbol": "^FTSE",
    },
    {
        "title": "European Union",
        "iso3": "EUU",
        "index_name": "EURO STOXX 50",
        "symbol": "^STOXX50E",
    },
    {
        "title": "Japan",
        "iso3": "JPN",
        "index_name": "Nikkei 225",
        "symbol": "^N225",
    },
]


WEATHER_CODE_LABELS = {
    0: "Clear",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Fog",
    48: "Depositing fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm",
}


HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; StreamlitWorldDashboard/1.0)",
    "Accept": "application/json,text/csv;q=0.8,*/*;q=0.5",
}


def safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def zone_now(tz_name: str) -> datetime:
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz = timezone.utc
    return datetime.now(tz)


def format_time(tz_name: str) -> str:
    return zone_now(tz_name).strftime("%a %H:%M")


def format_full_time(tz_name: str) -> str:
    return zone_now(tz_name).strftime("%Y-%m-%d %H:%M")


def format_number(value: Optional[float], decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def format_usd_compact(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    absolute = abs(value)
    if absolute >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if absolute >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if absolute >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


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


def chunks(items: List[Any], size: int) -> Iterable[List[Any]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def flatten_locations(countries: List[Dict[str, Any]]) -> Tuple[Tuple[str, str, float, float, str], ...]:
    rows: List[Tuple[str, str, float, float, str]] = []
    for item in countries:
        for location_name, lat, lon, tz_name in item["locations"]:
            rows.append((item["country"], location_name, lat, lon, tz_name))
    return tuple(rows)


@st.cache_data(ttl=600, show_spinner=False)
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


@st.cache_data(ttl=900, show_spinner=False)
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


@st.cache_data(ttl=43200, show_spinner=False)
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
