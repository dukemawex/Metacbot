from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class QuestionMeta:
    id: int
    title: str
    qtype: str
    status: str = "open"
    is_open: bool | None = None
    is_locked: bool | None = None
    resolved: bool | None = None
    open_time: str | None = None
    close_time: str | None = None
    prediction_end_time: str | None = None
    resolve_time: str | None = None
    options: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastPayload:
    question_id: int
    qtype: str
    payload: dict[str, Any]
    reasoning: str


@dataclass
class SubmissionResult:
    question_id: int
    submitted: bool
    status: str
    response: dict[str, Any]
    timestamp: datetime
