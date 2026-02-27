def forecast_numeric(values: list[float] | None = None) -> dict:
    values = values or [0.2, 0.5, 0.8]
    values = sorted(values)
    return {"p10": values[0], "p50": values[len(values)//2], "p90": values[-1]}
