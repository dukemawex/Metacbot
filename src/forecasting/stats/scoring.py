import math


def brier(prob: float, outcome: int) -> float:
    return (prob - outcome) ** 2


def log_score(prob: float, outcome: int) -> float:
    p = max(1e-9, min(1 - 1e-9, prob))
    return -math.log(p if outcome else 1 - p)
