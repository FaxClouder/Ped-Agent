import json
from datetime import UTC, datetime

import pytest
from ped_agent.agent.contracts import EvidenceItem, EvidenceOrigin, ModelOutput, RetrievalBatch
from ped_agent.agent.evidence_graph import EvidenceGraph, VerificationFailed

from ped_agent_server.evidence_executor import LangGraphRunExecutor
from ped_agent_server.run_service import RunExecutionContext


def local_evidence() -> EvidenceItem:
    return EvidenceItem(
        evidence_id="local-1",
        origin=EvidenceOrigin.LOCAL_OFFICIAL,
        title="Paper",
        quote="Density rises near the bottleneck.",
        locator="p.4",
        resource_id="paper-1",
        retrieved_at=datetime.now(UTC),
        content_hash="a" * 64,
        score=0.9,
    )


def external_evidence() -> EvidenceItem:
    return EvidenceItem(
        evidence_id="academic-1",
        origin=EvidenceOrigin.EXTERNAL_ACADEMIC,
        title="External paper",
        quote="External verified abstract.",
        url="https://example.org/paper",
        retrieved_at=datetime.now(UTC),
        content_hash="b" * 64,
    )


def draft_json(*, label: str = "L1", evidence_id: str = "local-1", text: str = "Answer") -> str:
    return json.dumps(
        {
            "answer_markdown": f"{text} [{label}]",
            "claims": [{"claim_id": "c1", "text": text, "citation_labels": [label]}],
            "citations": [
                {"label": label, "evidence_id": evidence_id, "claim_ids": ["c1"]}
            ],
            "inferences": [],
            "limitations": [],
        }
    )


class FakeLocalRetriever:
    def __init__(self, *, sufficient: bool) -> None:
        self.sufficient = sufficient

    async def retrieve(self, query: str) -> RetrievalBatch:
        return RetrievalBatch(items=[local_evidence()], sufficient=self.sufficient)


class FakeExternalSearcher:
    def __init__(self) -> None:
        self.calls = 0

    async def search(self, query: str) -> list[EvidenceItem]:
        self.calls += 1
        return [external_evidence()]


class FakeGateway:
    def __init__(self, generated: list[str], verified: list[str]) -> None:
        self.generated = list(generated)
        self.verified = list(verified)

    @property
    def verification_enabled(self) -> bool:
        return True

    async def generate(self, prompt: str) -> ModelOutput:
        return ModelOutput(content=self.generated.pop(0), model="fake-answer")

    async def verify(self, prompt: str) -> ModelOutput:
        return ModelOutput(content=self.verified.pop(0), model="fake-verify")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return []


def review(status: str) -> str:
    return json.dumps({"claims": [{"claim_id": "c1", "status": status}]})


def context() -> RunExecutionContext:
    return RunExecutionContext(
        run_id="run-1",
        conversation_id="conversation-1",
        query="Follow-up question",
        recent_messages=[{"role": "user", "content": "Previous question"}],
        previous_evidence_ids=["local-1"],
    )


@pytest.mark.asyncio
async def test_graph_uses_local_evidence_and_emits_deterministic_stages() -> None:
    searcher = FakeExternalSearcher()
    gateway = FakeGateway(["standalone query", draft_json()], [review("supported")])
    executor = LangGraphRunExecutor(EvidenceGraph(gateway, FakeLocalRetriever(sufficient=True), searcher))
    events: list[tuple[str, dict[str, object]]] = []

    result = await executor.execute(
        context(),
        lambda event, payload: _record(events, event, payload),
        lambda: False,
    )

    assert result.answer.answer_markdown == "Answer [L1]"
    assert result.answer.verification.semantic_passed is True
    assert searcher.calls == 0
    assert events[0][0] == "stage.started"
    assert "evidence.summary" in [event for event, _ in events]
    rewrite_trace = next(
        payload
        for event, payload in events
        if event == "stage.completed" and payload["stage"] == "rewrite_query"
    )
    verify_trace = next(
        payload
        for event, payload in events
        if event == "stage.completed" and payload["stage"] == "semantic_verify"
    )
    assert rewrite_trace["duration_ms"] >= 0
    assert rewrite_trace["model"] == "fake-answer"
    assert verify_trace["model"] == "fake-verify"


@pytest.mark.asyncio
async def test_graph_searches_once_when_local_evidence_is_insufficient() -> None:
    searcher = FakeExternalSearcher()
    gateway = FakeGateway(
        ["standalone query", draft_json(label="A1", evidence_id="academic-1")],
        [review("supported")],
    )
    graph = EvidenceGraph(gateway, FakeLocalRetriever(sufficient=False), searcher)

    result = await graph.execute(context(), lambda *_: _noop(), lambda: False)

    assert searcher.calls == 1
    assert {item.evidence_id for item in result.evidence} == {"local-1", "academic-1"}


@pytest.mark.asyncio
async def test_graph_revises_once_then_fails_closed_if_still_unsupported() -> None:
    gateway = FakeGateway(
        ["standalone query", draft_json(), draft_json(text="Revised")],
        [review("unsupported"), review("unsupported")],
    )
    graph = EvidenceGraph(
        gateway,
        FakeLocalRetriever(sufficient=True),
        FakeExternalSearcher(),
    )

    with pytest.raises(VerificationFailed, match="semantic verification failed after revision"):
        await graph.execute(context(), lambda *_: _noop(), lambda: False)

    assert gateway.generated == []
    assert gateway.verified == []


async def _record(
    events: list[tuple[str, dict[str, object]]],
    event: str,
    payload: dict[str, object],
) -> None:
    events.append((event, payload))


async def _noop() -> None:
    return None
