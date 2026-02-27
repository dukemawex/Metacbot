from __future__ import annotations

from datetime import datetime, timezone

from src.config.constants import MODEL_VERSION
from src.execution.dedupe import should_submit, submission_hash


def maybe_submit(client, settings, state: dict, question: dict, final_forecast: dict, reasoning: str, can_submit: bool):
    qid = str(question["id"])
    digest = submission_hash(question["id"], final_forecast, reasoning, MODEL_VERSION)
    last = state.get("submissions", {}).get(qid)

    if not can_submit:
        return {"submitted": False, "status": "SKIPPED_NOT_OPEN", "hash": digest}
    if settings.dry_run:
        return {"submitted": False, "status": "DRY_RUN", "hash": digest}
    if not should_submit(last, digest, settings.cooldown_minutes):
        return {"submitted": False, "status": "SKIPPED_UNCHANGED", "hash": digest}

    response = client.submit(question["id"], final_forecast, reasoning)
    state.setdefault("submissions", {})[qid] = {
        "hash": digest,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return {"submitted": True, "status": "SUBMITTED", "hash": digest, "response": response}
