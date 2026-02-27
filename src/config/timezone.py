from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

US_TZ = ZoneInfo("America/New_York")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_us(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(US_TZ)


def utc_and_us_iso(now: datetime | None = None) -> tuple[str, str]:
    current = now or now_utc()
    return current.astimezone(timezone.utc).isoformat(), to_us(current).isoformat()
