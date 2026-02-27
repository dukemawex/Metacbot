from __future__ import annotations

from pathlib import Path

from src.llm.structured import parse_strict_json

PROMPT_DIR = Path(__file__).parent / "prompts"


def _prompt(name: str) -> str:
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")


def run_roles(question: dict, evidence, llm_client) -> dict:
    base = f"Question: {question.get('title')}\nEvidence count: {len(evidence.items)}"
    researcher = parse_strict_json(llm_client.chat_json(_prompt("researcher") + "\n" + base))
    parser = parse_strict_json(llm_client.chat_json(_prompt("parser") + "\n" + base))
    summarizer = parse_strict_json(llm_client.chat_json(_prompt("summarizer") + "\n" + base))
    forecaster = parse_strict_json(llm_client.chat_json(_prompt("forecaster") + "\n" + base))
    return {
        "researcher": researcher,
        "parser": parser,
        "summarizer": summarizer,
        "forecaster": forecaster,
    }
