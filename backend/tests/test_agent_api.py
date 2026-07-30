from pathlib import Path

from fastapi.testclient import TestClient
from ped_agent.agent.contracts import RunStatus

from ped_agent_server.agent_repository import AgentRepository
from ped_agent_server.api import create_app
from ped_agent_server.catalog import Catalog
from ped_agent_server.index import FTSIndex


def create_agent_client(tmp_path: Path) -> tuple[TestClient, AgentRepository]:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild([], source_fingerprint=catalog.official_fingerprint())
    repository = AgentRepository(tmp_path / "agent.sqlite3")
    repository.initialize()
    client = TestClient(
        create_app(
            catalog_path=catalog.path,
            index_path=index.path,
            agent_repository=repository,
        )
    )
    return client, repository


def test_conversation_and_run_api_enforces_active_run_conflict(tmp_path: Path) -> None:
    client, repository = create_agent_client(tmp_path)
    created = client.post("/api/conversations", json={"title": "Flow review"})
    conversation_id = created.json()["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/runs",
        json={"query": "How does density affect speed?"},
    )

    assert response.status_code == 202
    assert response.json()["events_url"].startswith("/api/runs/")
    run_id = response.json()["run_id"]
    assert repository.get_run(run_id)["status"] in {
        RunStatus.QUEUED.value,
        RunStatus.RUNNING.value,
    }
    conflict = client.post(
        f"/api/conversations/{conversation_id}/runs",
        json={"query": "A second active question"},
    )
    assert conflict.status_code == 409

    listed = client.get("/api/conversations").json()
    detail = client.get(f"/api/conversations/{conversation_id}").json()
    assert listed[0]["id"] == conversation_id
    assert detail["messages"][0]["content"] == "How does density affect speed?"


def test_sse_replays_after_last_event_id_and_stops_at_terminal_event(tmp_path: Path) -> None:
    client, repository = create_agent_client(tmp_path)
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")
    first = repository.append_event(run["id"], "run.started", {"run_id": run["id"]})
    repository.append_event(run["id"], "stage.completed", {"stage": "verify"})
    repository.set_run_status(run["id"], RunStatus.COMPLETED)
    repository.append_event(run["id"], "run.completed", {"run_id": run["id"]})

    response = client.get(
        f"/api/runs/{run['id']}/events",
        headers={"Last-Event-ID": str(first["id"])},
    )

    assert response.status_code == 200
    assert "event: run.started" not in response.text
    assert "event: stage.completed" in response.text
    assert "event: run.completed" in response.text
    assert response.headers["content-type"].startswith("text/event-stream")


def test_cancel_endpoint_marks_active_run_and_emits_terminal_event(tmp_path: Path) -> None:
    client, repository = create_agent_client(tmp_path)
    conversation = repository.create_conversation()
    run = repository.create_run(conversation["id"], query="Question")

    response = client.post(f"/api/runs/{run['id']}/cancel")

    assert response.status_code == 202
    assert repository.get_run(run["id"])["status"] == RunStatus.CANCELLED.value
    assert repository.list_events(run["id"])[-1]["event"] == "run.cancelled"
