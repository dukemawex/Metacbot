from datetime import datetime

from src.forecasting.stats.date_models import forecast_date


def test_date_forecast_has_iso_values():
    out = forecast_date(5)
    datetime.fromisoformat(out["p10"])
    datetime.fromisoformat(out["p50"])
    datetime.fromisoformat(out["p90"])
