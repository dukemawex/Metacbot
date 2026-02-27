from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone


def submission_hash(question_id: int, payload: dict, reasoning: str, model_version: str) -> str:
    raw = f"{question_id}|{payload}|{reasoning}|{model_version}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def should_submit(last: dict | None, new_hash: str, cooldown_minutes: int, now: datetime | None = None) -> bool:
    if not last:
        return True
    if last.get("hash") != new_hash:
        return True
    ts = datetime.fromisoformat(last.get("timestamp"))
    current = now or datetime.now(timezone.utc)
    return current >= ts + timedelta(minutes=cooldown_minutes)
