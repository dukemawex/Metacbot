from src.forecasting.stats.binary_models import beta_update


def test_beta_update_probability():
    out = beta_update(1, 1, 3, 1)
    assert round(out["probability"], 3) == 0.667
