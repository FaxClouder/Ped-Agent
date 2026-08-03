import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from ped_agent.agent.contracts import RunStatus

from ped_agent_server.agent_repository import ActiveRunError, AgentRepository


class SynchronizedCancelRepository(AgentRepository):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.synchronize_cancels = False
        self.cancel_barrier = threading.Barrier(2)

    def get_run(self, run_id: str) -> dict[str, object] | None:
        run = super().get_run(run_id)
        if self.synchronize_cancels and run is not None and run["status"] == "running":
            self.cancel_barrier.wait(timeout=5)
        return run


def test_repository_migrates_wal_and_enforces_one_active_run(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation(title="Bottleneck review")
    run = repository.create_run(conversation["id"], query="What changes near a bottleneck?")

    assert repository.journal_mode() == "wal"
    assert repository.schema_version() == 1
    assert run["status"] == RunStatus.QUEUED.value
    with pytest.raises(ActiveRunError):
        repository.create_run(conversation["id"], query="Follow-up")


def test_repository_replays_events_and_interrupts_unfinished_runs(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")
    first = repository.append_event(run["id"], "run.started", {"status": "running"})
    repository.set_run_status(run["id"], RunStatus.RUNNING)
    second = repository.append_event(
        run["id"],
        "stage.started",
        {"stage": "local_retrieval"},
    )

    assert [item["id"] for item in repository.list_events(run["id"], after_id=first["id"])] == [
        second["id"]
    ]

    interrupted = repository.interrupt_active_runs()

    assert interrupted == [run["id"]]
    assert repository.get_run(run["id"])["status"] == RunStatus.INTERRUPTED.value
    assert repository.list_events(run["id"])[-1]["event"] == "run.failed"


def test_repository_returns_conversation_messages_and_citations(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    repository.add_message(conversation["id"], role="user", content="Question")
    message = repository.add_message(
        conversation["id"],
        role="assistant",
        content="Answer [L1]",
        answer_document={"answer_markdown": "Answer [L1]"},
    )
    repository.save_evidence(
        run_id=None,
        items=[
            {
                "evidence_id": "local-1",
                "origin": "local_official",
                "title": "Paper",
                "quote": "Quoted text",
                "locator": "page 4",
                "retrieved_at": "2026-07-30T00:00:00+00:00",
                "content_hash": "a" * 64,
                "score": 0.9,
            }
        ],
    )
    repository.link_citation(message["id"], "L1", "local-1", ["claim-1"])

    detail = repository.get_conversation(conversation["id"])

    assert detail is not None
    assert [item["role"] for item in detail["messages"]] == ["user", "assistant"]
    assert detail["messages"][1]["citations"][0]["evidence"]["locator"] == "page 4"


def test_request_cancel_has_one_atomic_winner(tmp_path: Path) -> None:
    repository = SynchronizedCancelRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")
    repository.set_run_status(run["id"], RunStatus.RUNNING)
    repository.synchronize_cancels = True

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(repository.request_cancel, run["id"]) for _ in range(2)]
        results = [future.result(timeout=10) for future in futures]

    assert sorted(results) == [False, True]
    assert repository.get_run(run["id"])["status"] == RunStatus.CANCELLED.value
    assert [event["event"] for event in repository.list_events(run["id"])] == ["run.cancelled"]


@pytest.mark.parametrize("status", [RunStatus.COMPLETED, RunStatus.FAILED])
def test_request_cancel_rejects_finished_run_without_event(
    tmp_path: Path,
    status: RunStatus,
) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")
    repository.set_run_status(run["id"], RunStatus.RUNNING)
    repository.set_run_status(run["id"], status)

    assert repository.request_cancel(run["id"]) is False
    assert repository.list_events(run["id"]) == []


def test_request_cancel_is_idempotent_for_cancelled_run(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")

    assert repository.request_cancel(run["id"]) is True
    assert repository.request_cancel(run["id"]) is False
    assert [event["event"] for event in repository.list_events(run["id"])] == ["run.cancelled"]


def test_start_run_starts_queued_run_once(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")

    assert hasattr(repository, "start_run")
    assert repository.start_run(run["id"]) is True
    started = repository.get_run(run["id"])
    assert started["status"] == RunStatus.RUNNING.value
    assert started["started_at"] is not None
    assert repository.start_run(run["id"]) is False
    assert [event["event"] for event in repository.list_events(run["id"])] == ["run.started"]


def test_start_run_rejects_cancelled_run_without_event(tmp_path: Path) -> None:
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")
    assert repository.request_cancel(run["id"]) is True

    assert hasattr(repository, "start_run")
    assert repository.start_run(run["id"]) is False
    assert repository.get_run(run["id"])["status"] == RunStatus.CANCELLED.value
    assert [event["event"] for event in repository.list_events(run["id"])] == ["run.cancelled"]
