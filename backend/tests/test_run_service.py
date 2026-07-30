from pathlib import Path

import pytest
from ped_agent.agent.contracts import (
    AnswerDocument,
    CitationRef,
    EvidenceItem,
    EvidenceOrigin,
    VerificationSummary,
)

from ped_agent_server.agent_repository import AgentRepository
from ped_agent_server.run_service import RunExecutionResult, RunService


class FakeExecutor:
    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        await emit("stage.started", {"stage": "local_retrieval"})
        evidence = EvidenceItem(
            evidence_id="local-1",
            origin=EvidenceOrigin.LOCAL_OFFICIAL,
            title="Paper",
            quote="Verified quote",
            locator="page 2",
            retrieved_at="2026-07-30T00:00:00Z",
            content_hash="a" * 64,
            score=0.9,
        )
        await emit("stage.completed", {"stage": "local_retrieval"})
        await emit("evidence.summary", {"total": 1, "local": 1})
        answer = AnswerDocument(
            answer_markdown="Verified answer [L1]",
            citations=[CitationRef(label="L1", evidence_id="local-1", claim_ids=["c1"])],
            limitations=[],
            verification=VerificationSummary(
                status="verified",
                rules_passed=True,
                semantic_passed=True,
            ),
        )
        return RunExecutionResult(answer=answer, evidence=[evidence])


@pytest.mark.asyncio
async def test_run_service_persists_only_verified_final_answer(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    service = RunService(repository, FakeExecutor(), max_concurrent_runs=2)

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    events = repository.list_events(run["id"])
    detail = repository.get_conversation(conversation["id"])
    assert [item["event"] for item in events] == [
        "run.started",
        "stage.started",
        "stage.completed",
        "evidence.summary",
        "answer.delta",
        "run.completed",
    ]
    assert detail is not None
    assert detail["messages"][-1]["content"] == "Verified answer [L1]"
    assert detail["messages"][-1]["citations"][0]["evidence"]["origin"] == "local_official"
    assert repository.get_run(run["id"])["status"] == "completed"


class FailingExecutor:
    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        raise RuntimeError("provider failed with key sk-secret")


@pytest.mark.asyncio
async def test_run_service_fails_closed_without_persisting_draft_or_secret(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    service = RunService(repository, FailingExecutor())

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    detail = repository.get_conversation(conversation["id"])
    terminal = repository.list_events(run["id"])[-1]
    assert detail is not None
    assert [message["role"] for message in detail["messages"]] == ["user"]
    assert terminal["event"] == "run.failed"
    assert "sk-secret" not in str(terminal)
