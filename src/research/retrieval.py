from __future__ import annotations

import logging

from src.research.evidence import EvidenceBundle, EvidenceItem
from src.research.source_ranker import deduplicate_and_rank

logger = logging.getLogger(__name__)


def build_queries(question: dict) -> list[str]:
    title = question.get("title", "")
    return [title, f"{title} latest evidence"]


def retrieve_evidence(question: dict, exa_client) -> EvidenceBundle:
    rows: list[dict] = []
    for query in build_queries(question):
        try:
            rows.extend(exa_client.search(query))
        except Exception as exc:
            logger.warning(
                "Failed to search evidence for question_id=%s with query=\"%s\": %s",
                question.get("id"),
                query,
                exc,
            )
    ranked = deduplicate_and_rank(rows)
    question_id = 0
    raw_id = question.get("id")
    if raw_id is not None:
        try:
            question_id = int(raw_id)
        except (TypeError, ValueError):
            question_id = 0
    items = [
        EvidenceItem(
            idx=i + 1,
            title=row.get("title", "Untitled"),
            url=row.get("url", ""),
            snippet=row.get("text", "")[:400],
            score=float(row.get("score", 0.0)),
        )
        for i, row in enumerate(ranked)
    ]
    return EvidenceBundle(question_id=question_id, items=items)
