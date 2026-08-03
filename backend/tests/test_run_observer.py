from contextlib import contextmanager
from dataclasses import dataclass

import pytest
from ped_agent import __version__ as application_version
from pydantic import SecretStr

import ped_agent_server.run_observer as run_observer_module
from ped_agent_server.run_observer import LangSmithObserver, NoOpRunObserver
from ped_agent_server.settings import LangSmithSettings


@dataclass(frozen=True)
class FakeContext:
    run_id: str = "11111111-1111-1111-1111-111111111111"
    conversation_id: str = "conversation-1"


async def return_value(value: str) -> str:
    return value


class FakeLangSmithClient:
    def __init__(self) -> None:
        self.feedback: list[dict[str, object]] = []
        self.flushed = False
        self.closed = False

    def create_feedback(self, **kwargs) -> None:
        self.feedback.append(kwargs)

    def flush(self) -> None:
        self.flushed = True

    def close(self) -> None:
        self.closed = True


class FailingLangSmithClient(FakeLangSmithClient):
    def create_feedback(self, **kwargs) -> None:
        raise RuntimeError("offline")


class FailingCloseLangSmithClient(FakeLangSmithClient):
    def flush(self) -> None:
        raise RuntimeError("flush offline")

    def close(self) -> None:
        self.closed = True
        raise RuntimeError("close offline")


def observer_settings() -> LangSmithSettings:
    return LangSmithSettings(
        enabled=True,
        api_key=SecretStr("langsmith-secret"),
        project="ped-agent-local",
        sampling_rate=1.0,
        content_policy="redacted",
    )


def build_observer(client) -> LangSmithObserver:
    return LangSmithObserver(
        observer_settings(),
        answer_model="deepseek-v4-flash",
        verify_model="deepseek-v4-pro",
        embedding_model="embed-test",
        external_search_enabled=True,
        verification_required=True,
        client=client,
    )


@pytest.mark.asyncio
async def test_noop_observer_disables_ambient_tracing(monkeypatch) -> None:
    captured: dict[str, object] = {}

    @contextmanager
    def capture_tracing_context(**kwargs):
        captured.update(kwargs)
        yield

    monkeypatch.setattr(run_observer_module, "tracing_context", capture_tracing_context)
    observer = NoOpRunObserver()
    result = await observer.observe_run(FakeContext(), lambda: return_value("ok"))

    assert result == "ok"
    assert captured == {"enabled": False}


@pytest.mark.asyncio
async def test_langsmith_observer_sets_safe_tags_and_metadata(monkeypatch) -> None:
    captured: dict[str, object] = {}

    @contextmanager
    def capture_tracing_context(**kwargs):
        captured.update(kwargs)
        yield

    monkeypatch.setattr(run_observer_module, "tracing_context", capture_tracing_context)
    observer = build_observer(FakeLangSmithClient())

    result = await observer.observe_run(FakeContext(), lambda: return_value("ok"))

    assert result == "ok"
    assert captured["project_name"] == "ped-agent-local"
    assert captured["tags"] == [
        "feature:evidence-qa",
        "environment:local",
        "answer-model:deepseek-v4-flash",
        "verify-model:deepseek-v4-pro",
        "embedding-model:embed-test",
        "graph-version:v1",
    ]
    assert captured["metadata"] == {
        "run_id": "11111111-1111-1111-1111-111111111111",
        "conversation_id": "conversation-1",
        "graph_version": "v1",
        "application_version": application_version,
        "answer_model": "deepseek-v4-flash",
        "verify_model": "deepseek-v4-pro",
        "embedding_model": "embed-test",
        "external_search_enabled": True,
        "verification_required": True,
    }


@pytest.mark.asyncio
async def test_langsmith_observer_records_each_non_null_metric() -> None:
    client = FakeLangSmithClient()
    observer = build_observer(client)

    await observer.record_feedback(
        "11111111-1111-1111-1111-111111111111",
        {"run_success": True, "revision_count": 1, "semantic_verification_passed": None},
    )

    assert [(item["key"], item.get("score"), item.get("value")) for item in client.feedback] == [
        ("run_success", True, None),
        ("revision_count", None, 1),
    ]


@pytest.mark.asyncio
async def test_langsmith_feedback_failure_is_swallowed(caplog) -> None:
    observer = build_observer(FailingLangSmithClient())
    await observer.record_feedback("11111111-1111-1111-1111-111111111111", {"run_success": True})
    assert "LangSmith feedback failed" in caplog.text


@pytest.mark.asyncio
async def test_langsmith_close_failures_are_swallowed_and_both_steps_run(caplog) -> None:
    client = FailingCloseLangSmithClient()
    observer = build_observer(client)
    await observer.close()
    assert client.closed is True
    assert caplog.text.count("LangSmith shutdown failed") == 2
