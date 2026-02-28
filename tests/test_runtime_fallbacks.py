from src.llm.roles import run_roles
from src.research.evidence import EvidenceBundle
from src.research.retrieval import retrieve_evidence


class StubFailingExa:
    def search(self, _query: str) -> list[dict]:
        raise RuntimeError("boom")


class StubFailingLLM:
    def chat_json(self, _prompt: str) -> dict:
        raise ValueError("bad")


class StubEmptyExa:
    def search(self, _query: str) -> list[dict]:
        return []


def test_retrieve_evidence_handles_missing_id():
    evidence = retrieve_evidence({"title": "Test", "id": None}, StubEmptyExa())
    assert evidence.question_id == 0
    assert evidence.items == []


def test_retrieve_evidence_handles_search_failures():
    evidence = retrieve_evidence({"title": "Test", "id": 42}, StubFailingExa())
    assert evidence.question_id == 42
    assert evidence.items == []


def test_run_roles_returns_empty_payloads_on_failure():
    evidence = EvidenceBundle(question_id=1, items=[])
    outputs = run_roles({"id": 123, "title": "Test"}, evidence, StubFailingLLM())
    assert outputs["researcher"] == {}
    assert outputs["parser"] == {}
    assert outputs["summarizer"] == {}
    assert outputs["forecaster"] == {}
