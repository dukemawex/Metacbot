def dirichlet_update(k: int, evidence_weight: float = 1.0) -> dict:
    alpha = [1.0 + evidence_weight for _ in range(max(k, 1))]
    s = sum(alpha)
    return {"distribution": [a / s for a in alpha]}
