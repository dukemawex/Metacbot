from __future__ import annotations

from datetime import datetime


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    candidate = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        return None


def is_tournament_open_now(tournament_meta: dict, now_us_time: datetime) -> tuple[bool, str]:
    if tournament_meta.get("is_locked") is True:
        return False, "LOCKED"
    if tournament_meta.get("is_open") is False:
        return False, "CLOSED_WINDOW"
    start = _parse_dt(tournament_meta.get("open_time") or tournament_meta.get("start_time"))
    end = _parse_dt(tournament_meta.get("close_time") or tournament_meta.get("prediction_end_time"))
    if start and now_us_time < start.astimezone(now_us_time.tzinfo):
        return False, "NOT_YET_OPEN"
    if end and now_us_time >= end.astimezone(now_us_time.tzinfo):
        return False, "CLOSED_WINDOW"
    return True, "OPEN"


def is_question_open_now(question_meta: dict, now_us_time: datetime) -> tuple[bool, str]:
    if question_meta.get("resolved") or question_meta.get("status") in {"resolved", "closed"}:
        return False, "RESOLVED"
    if question_meta.get("is_locked") is True:
        return False, "LOCKED"
    if question_meta.get("is_open") is False:
        return False, "CLOSED_WINDOW"
    start = _parse_dt(question_meta.get("open_time"))
    end = _parse_dt(
        question_meta.get("prediction_end_time")
        or question_meta.get("close_time")
        or question_meta.get("resolve_time")
    )
    if start and now_us_time < start.astimezone(now_us_time.tzinfo):
        return False, "NOT_YET_OPEN"
    if end and now_us_time >= end.astimezone(now_us_time.tzinfo):
        return False, "CLOSED_WINDOW"
    return True, "OPEN"
