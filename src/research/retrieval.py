from __future__ import annotations

from src.research.evidence import EvidenceBundle, EvidenceItem
from src.research.source_ranker import deduplicate_and_rank


def build_queries(question: dict) -> list[str]:
    title = question.get("title", "")
    return [title, f"{title} latest evidence"]


def retrieve_evidence(question: dict, exa_client) -> EvidenceBundle:
    rows: list[dict] = []
    for query in build_queries(question):
        rows.extend(exa_client.search(query))
    ranked = deduplicate_and_rank(rows)
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
    return EvidenceBundle(question_id=question.get("id", 0), items=items)
