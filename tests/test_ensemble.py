from src.forecasting.ensemble import combine


def test_binary_ensemble_average():
    question = {"type": "binary"}
    out = combine(question, {"probability": 0.4}, {"probability": 0.6}, {"probability": 0.5}, 0.01, 0.99)
    assert out["probability"] == 0.5
