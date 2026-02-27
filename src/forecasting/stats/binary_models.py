def beta_update(prior_alpha: float, prior_beta: float, positive: int, negative: int) -> dict:
    alpha = prior_alpha + positive
    beta = prior_beta + negative
    mean = alpha / (alpha + beta)
    return {"alpha": alpha, "beta": beta, "probability": mean}


def forecast_binary(features: dict) -> dict:
    pos = int(features.get("evidence_count", 0) // 2)
    neg = max(int(features.get("evidence_count", 0)) - pos, 0)
    return beta_update(1.0, 1.0, pos, neg)
