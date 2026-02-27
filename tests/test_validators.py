from src.forecasting.validators import validate_forecast


def test_binary_clamp():
    out = validate_forecast("binary", {"probability": 2})
    assert out["probability"] == 0.99


def test_distribution_normalized():
    out = validate_forecast("multiple_choice", {"distribution": [1, 1, 2]})
    assert round(sum(out["distribution"]), 6) == 1.0
