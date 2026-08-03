import asyncio
import threading
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
        self.flush_timeout: float | None = None
        self.close_timeout: float | None = None

    def create_feedback(self, **kwargs) -> None:
        self.feedback.append(kwargs)

    def flush(self, timeout: float | None = None) -> None:
        self.flush_timeout = timeout
        self.flushed = True

    def close(self, timeout: float | None = None) -> None:
        self.close_timeout = timeout
        self.closed = True


class FailingLangSmithClient(FakeLangSmithClient):
    def create_feedback(self, **kwargs) -> None:
        raise RuntimeError("offline")


class FirstFeedbackFailsLangSmithClient(FakeLangSmithClient):
    def create_feedback(self, **kwargs) -> None:
        if kwargs["key"] == "first_metric":
            raise RuntimeError("PRIVATE feedback failure")
        super().create_feedback(**kwargs)


class FalseyLangSmithClient(FakeLangSmithClient):
    def __bool__(self) -> bool:
        return False


class FailingCloseLangSmithClient(FakeLangSmithClient):
    def flush(self, timeout: float | None = None) -> None:
        self.flush_timeout = timeout
        raise RuntimeError("PRIVATE flush offline")

    def close(self, timeout: float | None = None) -> None:
        self.close_timeout = timeout
        self.closed = True
        raise RuntimeError("PRIVATE close offline")


class HangingFlushLangSmithClient(FakeLangSmithClient):
    def __init__(self) -> None:
        super().__init__()
        self.release_flush = threading.Event()

    def flush(self, timeout: float | None = None) -> None:
        self.flush_timeout = timeout
        self.release_flush.wait()


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
    assert "offline" not in caplog.text
    assert "Traceback" not in caplog.text


@pytest.mark.asyncio
async def test_langsmith_feedback_failure_does_not_skip_later_metrics(caplog) -> None:
    client = FirstFeedbackFailsLangSmithClient()
    observer = build_observer(client)

    await observer.record_feedback(
        "11111111-1111-1111-1111-111111111111",
        {"first_metric": True, "second_metric": 2},
    )

    assert [item["key"] for item in client.feedback] == ["second_metric"]
    assert "first_metric" in caplog.text
    assert "RuntimeError" in caplog.text
    assert "PRIVATE feedback failure" not in caplog.text
    assert "Traceback" not in caplog.text


def test_langsmith_observer_keeps_explicit_falsey_client() -> None:
    client = FalseyLangSmithClient()

    observer = build_observer(client)

    assert observer.client is client


@pytest.mark.asyncio
async def test_langsmith_close_failures_are_swallowed_and_both_steps_run(caplog) -> None:
    client = FailingCloseLangSmithClient()
    observer = build_observer(client)
    await observer.close()
    assert client.closed is True
    assert caplog.text.count("LangSmith shutdown failed") == 2
    assert "RuntimeError" in caplog.text
    assert "PRIVATE" not in caplog.text
    assert "Traceback" not in caplog.text


@pytest.mark.asyncio
async def test_langsmith_close_has_deadline_and_attempts_close_after_flush_timeout(
    monkeypatch, caplog
) -> None:
    shutdown_timeout = 0.05
    monkeypatch.setattr(
        run_observer_module,
        "LANGSMITH_SHUTDOWN_TIMEOUT_SECONDS",
        shutdown_timeout,
    )
    client = HangingFlushLangSmithClient()
    observer = build_observer(client)
    loop = asyncio.get_running_loop()

    started_at = loop.time()
    try:
        await observer.close()
    finally:
        client.release_flush.set()
    elapsed = loop.time() - started_at

    assert elapsed < 0.5
    assert client.closed is True
    assert client.flush_timeout == shutdown_timeout
    assert client.close_timeout == shutdown_timeout
    assert "flush" in caplog.text
    assert "TimeoutError" in caplog.text
    assert "Traceback" not in caplog.text
