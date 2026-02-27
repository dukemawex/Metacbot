from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvidenceItem:
    idx: int
    title: str
    url: str
    snippet: str
    score: float = 0.0


@dataclass
class EvidenceBundle:
    question_id: int
    items: list[EvidenceItem]
