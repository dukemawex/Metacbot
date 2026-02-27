def calibrate_probability(p: float, min_prob: float = 0.01, max_prob: float = 0.99) -> float:
    return max(min_prob, min(max_prob, p))
