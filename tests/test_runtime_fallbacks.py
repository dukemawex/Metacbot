from src.llm.roles import run_roles
from src.research.evidence import EvidenceBundle
from src.research.retrieval import retrieve_evidence


class _FailingExa:
    def search(self, query: str) -> list[dict]:
        raise RuntimeError("boom")


class _FailingLLM:
    def chat_json(self, prompt: str) -> dict:
        raise ValueError("bad")


def test_retrieve_evidence_handles_failures_and_missing_id():
    evidence = retrieve_evidence({"title": "Test", "id": None}, _FailingExa())
    assert evidence.question_id == 0
    assert evidence.items == []


def test_run_roles_returns_empty_payloads_on_failure():
    evidence = EvidenceBundle(question_id=1, items=[])
    outputs = run_roles({"id": 123, "title": "Test"}, evidence, _FailingLLM())
    assert outputs["researcher"] == {}
    assert outputs["parser"] == {}
    assert outputs["summarizer"] == {}
    assert outputs["forecaster"] == {}
