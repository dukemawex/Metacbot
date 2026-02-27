def extract_features(question: dict, evidence_bundle) -> dict:
    return {
        "evidence_count": len(evidence_bundle.items),
        "has_close_time": bool(question.get("close_time") or question.get("prediction_end_time")),
    }
