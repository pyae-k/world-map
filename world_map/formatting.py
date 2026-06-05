from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Iterable, List, Optional

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


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


def chunks(items: List[Any], size: int) -> Iterable[List[Any]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]
