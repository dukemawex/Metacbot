import pytest

from src.llm.structured import parse_strict_json


def test_parse_strict_json_with_wrapper_text():
    raw = "noise {\"probability\": 0.55} trailing"
    out = parse_strict_json(raw)
    assert out["probability"] == pytest.approx(0.55)
