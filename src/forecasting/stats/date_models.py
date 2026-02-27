from datetime import datetime, timedelta, timezone


def forecast_date(days_out: int = 30) -> dict:
    center = datetime.now(timezone.utc) + timedelta(days=days_out)
    return {
        "p10": (center - timedelta(days=10)).isoformat(),
        "p50": center.isoformat(),
        "p90": (center + timedelta(days=10)).isoformat(),
    }
