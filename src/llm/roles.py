from __future__ import annotations

import logging
from pathlib import Path

from src.llm.structured import parse_strict_json

PROMPT_DIR = Path(__file__).parent / "prompts"
logger = logging.getLogger(__name__)


def _prompt(name: str) -> str:
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")


def run_roles(question: dict, evidence, llm_client) -> dict:
    base = f"Question: {question.get('title')}\nEvidence count: {len(evidence.items)}"
    def _safe_role(name: str) -> dict:
        try:
            return parse_strict_json(llm_client.chat_json(_prompt(name) + "\n" + base))
        except Exception as exc:
            logger.warning(
                "Failed to execute LLM role \"%s\" for question_id=%s: %s",
                name,
                question.get("id"),
                exc,
            )
            return {}

    researcher = _safe_role("researcher")
    parser = _safe_role("parser")
    summarizer = _safe_role("summarizer")
    forecaster = _safe_role("forecaster")
    return {
        "researcher": researcher,
        "parser": parser,
        "summarizer": summarizer,
        "forecaster": forecaster,
    }
