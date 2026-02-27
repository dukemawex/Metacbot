from datetime import datetime, timezone

from src.metaculus.windows import is_question_open_now, is_tournament_open_now


def test_tournament_open_window():
    now = datetime(2026, 6, 1, tzinfo=timezone.utc)
    open_meta = {"is_open": True, "open_time": "2026-01-01T00:00:00Z", "close_time": "2026-12-31T00:00:00Z"}
    closed_meta = {"is_open": False}
    assert is_tournament_open_now(open_meta, now)[0] is True
    assert is_tournament_open_now(closed_meta, now)[1] == "CLOSED_WINDOW"


def test_question_states():
    now = datetime(2026, 6, 1, tzinfo=timezone.utc)
    q = {"is_open": True, "resolved": False, "close_time": "2026-12-31T00:00:00Z"}
    assert is_question_open_now(q, now)[0] is True
    assert is_question_open_now({"resolved": True}, now)[1] == "RESOLVED"
