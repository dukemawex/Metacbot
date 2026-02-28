"""Tests for Metaculus API payload formatting."""

from src.metaculus.client import _format_payload_for_api


def test_binary_question_format():
    question = {"id": 1, "type": "binary"}
    forecast = {"probability": 0.75}
    result = _format_payload_for_api(question, forecast)
    assert result == {"probability_yes": 0.75}


def test_binary_question_default():
    question = {"id": 1, "type": "binary"}
    forecast = {}
    result = _format_payload_for_api(question, forecast)
    assert result == {"probability_yes": 0.5}


def test_multiple_choice_format():
    question = {"id": 2, "type": "multiple_choice"}
    forecast = {"distribution": [0.3, 0.5, 0.2]}
    result = _format_payload_for_api(question, forecast)
    assert result == {"probability_yes_per_category": [0.3, 0.5, 0.2]}


def test_numeric_format():
    question = {"id": 3, "type": "numeric"}
    forecast = {"p10": 0.2, "p50": 0.5, "p90": 0.8}
    result = _format_payload_for_api(question, forecast)
    assert result == {"percentiles": [0.2, 0.5, 0.8]}


def test_discrete_format():
    question = {"id": 4, "type": "discrete"}
    forecast = {"p10": 0.1, "p50": 0.4, "p90": 0.9}
    result = _format_payload_for_api(question, forecast)
    assert result == {"percentiles": [0.1, 0.4, 0.9]}


def test_date_format():
    question = {"id": 5, "type": "date"}
    forecast = {"date_quantiles": {"p10": 0.15, "p50": 0.55, "p90": 0.85}}
    result = _format_payload_for_api(question, forecast)
    assert result == {"p10": 0.15, "p50": 0.55, "p90": 0.85}


def test_date_format_defaults():
    question = {"id": 5, "type": "date"}
    forecast = {"date_quantiles": {}}
    result = _format_payload_for_api(question, forecast)
    assert result == {"p10": 0.1, "p50": 0.5, "p90": 0.9}
