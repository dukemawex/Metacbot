def fit_distribution(values: list[float]) -> dict:
    if not values:
        return {"mean": 0.5, "std": 0.0}
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return {"mean": mean, "std": var ** 0.5}
