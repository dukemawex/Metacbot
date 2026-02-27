from src.forecasting.validators import validate_forecast


def combine(question: dict, baseline: dict, stats: dict, llm: dict, min_prob: float, max_prob: float) -> dict:
    qtype = question.get("type", "binary")
    if qtype == "binary":
        values = [
            baseline.get("probability", 0.5),
            stats.get("probability", 0.5),
            llm.get("probability", 0.5),
        ]
        result = {"probability": sum(values) / len(values)}
    elif qtype in {"multiple_choice", "distribution"}:
        result = {"distribution": stats.get("distribution") or baseline.get("distribution", [1.0])}
    else:
        result = {k: llm.get(k, stats.get(k, baseline.get(k))) for k in ["p10", "p50", "p90"]}
    return validate_forecast(qtype, result, min_prob=min_prob, max_prob=max_prob)
