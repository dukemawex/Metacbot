from src.forecasting.stats.numeric_models import forecast_numeric


def test_numeric_quantiles_monotonic():
    out = forecast_numeric([0.3, 0.9, 0.5])
    assert out["p10"] <= out["p50"] <= out["p90"]
