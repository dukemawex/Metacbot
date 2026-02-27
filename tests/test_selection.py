from datetime import datetime, timezone

from src.metaculus.selection import select_questions


def test_selection_limit_and_unresolved():
    now = datetime.now(timezone.utc)
    questions = [
        {"id": 1, "resolved": False, "close_time": "2027-01-01T00:00:00Z"},
        {"id": 2, "resolved": True, "close_time": "2026-01-01T00:00:00Z"},
    ]
    selected = select_questions(questions, now=now, limit=1)
    assert len(selected) == 1
    assert selected[0]["id"] == 1
