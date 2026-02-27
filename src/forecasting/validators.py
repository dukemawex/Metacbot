def _clamp(v: float, low: float, high: float) -> float:
    return max(low, min(high, v))


def validate_forecast(qtype: str, forecast: dict, min_prob: float = 0.01, max_prob: float = 0.99) -> dict:
    if qtype == "binary":
        return {"probability": _clamp(float(forecast.get("probability", 0.5)), min_prob, max_prob)}

    if qtype in {"multiple_choice", "distribution"}:
        dist = [max(0.0, float(v)) for v in forecast.get("distribution", [])]
        total = sum(dist) or 1.0
        return {"distribution": [v / total for v in dist]}

    p10 = float(forecast.get("p10", 0.1))
    p50 = float(forecast.get("p50", 0.5))
    p90 = float(forecast.get("p90", 0.9))
    ordered = sorted([p10, p50, p90])
    return {"p10": ordered[0], "p50": ordered[1], "p90": ordered[2]}
