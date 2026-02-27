def baseline_forecast(question: dict) -> dict:
    qtype = question.get("type", "binary")
    if qtype == "binary":
        return {"probability": 0.5}
    if qtype in {"multiple_choice", "distribution"}:
        options = question.get("options", [])
        if not options:
            return {"distribution": [1.0]}
        p = 1.0 / len(options)
        return {"distribution": [p for _ in options]}
    if qtype in {"numeric", "date"}:
        return {"p10": 0.1, "p50": 0.5, "p90": 0.9}
    return {"probability": 0.5}
