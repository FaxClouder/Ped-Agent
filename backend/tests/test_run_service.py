import asyncio
from pathlib import Path

import pytest
from ped_agent.agent.contracts import (
    AnswerDocument,
    CitationRef,
    EvidenceItem,
    EvidenceOrigin,
    EvidenceRunMetrics,
    VerificationSummary,
)
from ped_agent.agent.evidence_graph import RunCancelled

from ped_agent_server.agent_repository import AgentRepository
from ped_agent_server.run_service import RunExecutionResult, RunService


class RecordingObserver:
    def __init__(self) -> None:
        self.observed_run_ids: list[str] = []
        self.feedback: list[dict[str, object]] = []

    async def observe_run(self, context, operation):
        self.observed_run_ids.append(context.run_id)
        return await operation()

    async def record_feedback(self, run_id, metrics) -> None:
        self.feedback.append({"run_id": run_id, **dict(metrics)})

    async def close(self) -> None:
        return None


class CancelBeforeCompletionRepository(AgentRepository):
    def complete_run(self, run_id: str, **kwargs) -> str | None:
        assert self.request_cancel(run_id) is True
        return super().complete_run(run_id, **kwargs)


class CancelBeforeStartRepository(AgentRepository):
    def start_run(self, run_id: str) -> bool:
        assert self.request_cancel(run_id) is True
        return super().start_run(run_id)


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
        return RunExecutionResult(
            answer=answer,
            evidence=[evidence],
            metrics=EvidenceRunMetrics(
                local_evidence_count=1,
                citation_rules_passed=True,
                semantic_verification_passed=True,
            ),
        )


class CountingExecutor(FakeExecutor):
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        self.calls += 1
        return await super().execute(context, emit, is_cancelled)


@pytest.mark.asyncio
async def test_run_service_persists_only_verified_final_answer(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    observer = RecordingObserver()
    service = RunService(
        repository,
        FakeExecutor(),
        observer=observer,
        max_concurrent_runs=2,
    )

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
    assert observer.observed_run_ids == [run["id"]]
    assert observer.feedback[0]["run_success"] is True
    assert observer.feedback[0]["answer_displayed"] is True
    assert observer.feedback[0]["local_evidence_count"] == 1


class FailingExecutor:
    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        raise RuntimeError("provider failed with key sk-secret")


class CancellingThenFailingExecutor:
    def __init__(self, repository: AgentRepository) -> None:
        self.repository = repository

    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        self.repository.request_cancel(context.run_id)
        raise RuntimeError("provider failed after cancellation")


@pytest.mark.asyncio
async def test_run_service_fails_closed_without_persisting_draft_or_secret(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    observer = RecordingObserver()
    service = RunService(repository, FailingExecutor(), observer=observer)

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    detail = repository.get_conversation(conversation["id"])
    terminal = repository.list_events(run["id"])[-1]
    assert detail is not None
    assert [message["role"] for message in detail["messages"]] == ["user"]
    assert terminal["event"] == "run.failed"
    assert observer.feedback[-1]["run_success"] is False
    assert observer.feedback[-1]["answer_displayed"] is False
    assert "sk-secret" not in str(repository.list_events(run["id"])[-1])


class CancellingExecutor:
    def __init__(self, repository: AgentRepository) -> None:
        self.repository = repository

    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        self.repository.request_cancel(context.run_id)
        raise RunCancelled("cancelled")


class LateCancellingExecutor(FakeExecutor):
    def __init__(self, repository: AgentRepository) -> None:
        self.repository = repository

    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        result = await super().execute(context, emit, is_cancelled)
        self.repository.request_cancel(context.run_id)
        return result


class BlockingExecutor(FakeExecutor):
    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def execute(self, context, emit, is_cancelled) -> RunExecutionResult:
        self.started.set()
        await self.release.wait()
        return await super().execute(context, emit, is_cancelled)


@pytest.mark.asyncio
async def test_run_service_does_not_overwrite_cancelled_status_with_failure(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    observer = RecordingObserver()
    service = RunService(
        repository,
        CancellingExecutor(repository),
        observer=observer,
    )

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    assert repository.get_run(run["id"])["status"] == "cancelled"
    assert [event["event"] for event in repository.list_events(run["id"])] == [
        "run.started",
        "run.cancelled",
    ]
    assert observer.feedback[-1] == {
        "run_id": run["id"],
        "run_success": False,
        "answer_displayed": False,
        "cancelled": True,
    }


@pytest.mark.asyncio
async def test_run_service_records_feedback_for_late_cancellation(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    observer = RecordingObserver()
    service = RunService(
        repository,
        LateCancellingExecutor(repository),
        observer=observer,
    )

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    detail = repository.get_conversation(conversation["id"])
    assert repository.get_run(run["id"])["status"] == "cancelled"
    assert [event["event"] for event in repository.list_events(run["id"])] == [
        "run.started",
        "stage.started",
        "stage.completed",
        "evidence.summary",
        "run.cancelled",
    ]
    assert detail is not None
    assert [message["role"] for message in detail["messages"]] == ["user"]
    assert observer.feedback[-1] == {
        "run_id": run["id"],
        "run_success": False,
        "answer_displayed": False,
        "cancelled": True,
    }


@pytest.mark.asyncio
async def test_run_service_cancel_before_atomic_completion_wins_without_answer(
    tmp_path: Path,
) -> None:
    repository = CancelBeforeCompletionRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    observer = RecordingObserver()
    service = RunService(repository, FakeExecutor(), observer=observer)

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    detail = repository.get_conversation(conversation["id"])
    assert repository.get_run(run["id"])["status"] == "cancelled"
    assert [event["event"] for event in repository.list_events(run["id"])] == [
        "run.started",
        "stage.started",
        "stage.completed",
        "evidence.summary",
        "run.cancelled",
    ]
    assert detail is not None
    assert [message["role"] for message in detail["messages"]] == ["user"]
    assert observer.feedback == [
        {
            "run_id": run["id"],
            "run_success": False,
            "answer_displayed": False,
            "cancelled": True,
        }
    ]


@pytest.mark.asyncio
async def test_run_service_keeps_cancelled_when_executor_raises_generic_error(
    tmp_path: Path,
) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    observer = RecordingObserver()
    service = RunService(
        repository,
        CancellingThenFailingExecutor(repository),
        observer=observer,
    )

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    assert repository.get_run(run["id"])["status"] == "cancelled"
    assert [event["event"] for event in repository.list_events(run["id"])] == [
        "run.started",
        "run.cancelled",
    ]
    assert observer.feedback == [
        {
            "run_id": run["id"],
            "run_success": False,
            "answer_displayed": False,
            "cancelled": True,
        }
    ]


@pytest.mark.asyncio
async def test_run_service_records_feedback_for_queued_cancellation(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    first_conversation = repository.create_conversation()
    second_conversation = repository.create_conversation()
    observer = RecordingObserver()
    executor = BlockingExecutor()
    service = RunService(
        repository,
        executor,
        observer=observer,
        max_concurrent_runs=1,
    )

    first_run = await service.submit(first_conversation["id"], "First question")
    await executor.started.wait()
    second_run = await service.submit(second_conversation["id"], "Second question")
    assert repository.request_cancel(second_run["id"]) is True
    executor.release.set()
    await service.wait(first_run["id"])
    await service.wait(second_run["id"])

    second_detail = repository.get_conversation(second_conversation["id"])
    assert repository.get_run(second_run["id"])["status"] == "cancelled"
    assert [event["event"] for event in repository.list_events(second_run["id"])] == [
        "run.cancelled"
    ]
    assert second_detail is not None
    assert [message["role"] for message in second_detail["messages"]] == ["user"]
    assert [
        feedback for feedback in observer.feedback if feedback["run_id"] == second_run["id"]
    ] == [
        {
            "run_id": second_run["id"],
            "run_success": False,
            "answer_displayed": False,
            "cancelled": True,
        }
    ]
    assert observer.observed_run_ids == [first_run["id"]]


@pytest.mark.asyncio
async def test_run_service_cancel_before_atomic_start_wins_without_executor(
    tmp_path: Path,
) -> None:
    repository = CancelBeforeStartRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    observer = RecordingObserver()
    executor = CountingExecutor()
    service = RunService(repository, executor, observer=observer)

    run = await service.submit(conversation["id"], "Question")
    await service.wait(run["id"])

    assert repository.get_run(run["id"])["status"] == "cancelled"
    assert [event["event"] for event in repository.list_events(run["id"])] == ["run.cancelled"]
    assert executor.calls == 0
    assert observer.observed_run_ids == []
    assert observer.feedback == [
        {
            "run_id": run["id"],
            "run_success": False,
            "answer_displayed": False,
            "cancelled": True,
        }
    ]
