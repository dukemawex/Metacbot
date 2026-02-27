from __future__ import annotations

from datetime import datetime


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def select_questions(questions: list[dict], now, limit: int) -> list[dict]:
    def score(q: dict) -> tuple[int, datetime]:
        close = _parse(q.get("close_time") or q.get("prediction_end_time"))
        urgency = 0 if close is None else 1
        return (urgency, close or now)

    eligible = [q for q in questions if q.get("resolved") is not True]
    return sorted(eligible, key=score)[:limit]
