from pathlib import Path

import pytest
from ped_agent.agent.contracts import RunStatus

from ped_agent_server.agent_repository import ActiveRunError, AgentRepository


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
