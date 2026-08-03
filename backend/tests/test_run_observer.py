import asyncio
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass

import pytest
from ped_agent import __version__ as application_version
from ped_agent.agent.contracts import (
    AnswerDocument,
    CitationRef,
    InferenceItem,
    VerificationSummary,
)
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


class FailingItemsMapping(Mapping[str, bool | int | float | str | None]):
    def __getitem__(self, key: str) -> bool | int | float | str | None:
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(())

    def __len__(self) -> int:
        return 0

    def items(self):
        raise RuntimeError("PRIVATE metrics iteration failure")


def observer_settings() -> LangSmithSettings:
    return LangSmithSettings(
        enabled=True,
        api_key=SecretStr("langsmith-secret"),
        project="ped-agent-local",
        sampling_rate=1.0,
        content_policy="redacted",
    )


def answer_document_payload() -> dict[str, object]:
    answer = AnswerDocument(
        answer_markdown="Verified answer [L1]",
        citations=[
            CitationRef(
                label="L1",
                evidence_id="local:chunk-1",
                claim_ids=["claim-1"],
            )
        ],
        inferences=[
            InferenceItem(
                text="Preserved inference text",
                basis_evidence_ids=["local:chunk-1"],
            )
        ],
        limitations=["Preserved limitation text"],
        verification=VerificationSummary(
            status="verified",
            rules_passed=True,
            semantic_passed=True,
        ),
    )
    payload = answer.model_dump(mode="json")
    payload["claims"] = [{"claim_id": "claim-1", "text": "Preserved claim text"}]
    return payload


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


@pytest.mark.asyncio
async def test_langsmith_invalid_run_id_preserves_feedback_failure_log_contract(caplog) -> None:
    observer = build_observer(FakeLangSmithClient())

    await observer.record_feedback("not-a-uuid", {"run_success": True})

    assert "LangSmith feedback failed" in caplog.text
    assert "run_id" in caplog.text
    assert "ValueError" in caplog.text
    assert "not-a-uuid" not in caplog.text
    assert "Traceback" not in caplog.text


@pytest.mark.asyncio
async def test_langsmith_metrics_iteration_failure_is_swallowed(caplog) -> None:
    observer = build_observer(FakeLangSmithClient())

    await observer.record_feedback(
        "11111111-1111-1111-1111-111111111111",
        FailingItemsMapping(),
    )

    assert "LangSmith feedback failed" in caplog.text
    assert "metrics" in caplog.text
    assert "RuntimeError" in caplog.text
    assert "PRIVATE metrics iteration failure" not in caplog.text
    assert "Traceback" not in caplog.text


def test_langsmith_observer_keeps_explicit_falsey_client() -> None:
    client = FalseyLangSmithClient()

    observer = build_observer(client)

    assert observer.client is client


def test_langsmith_client_anonymizer_preserves_final_answer_and_redacts_private_data(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    class CapturingClient:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr(run_observer_module, "Client", CapturingClient)
    monkeypatch.setattr(
        run_observer_module,
        "create_secret_anonymizer",
        lambda: lambda payload: payload,
    )
    run_observer_module._build_client(observer_settings())
    final_answer = answer_document_payload()
    payload = {
        "final_answer": final_answer,
        "raw": {"text": "PRIVATE raw output"},
        "messages": [{"text": "PRIVATE history"}],
    }

    redacted = captured["anonymizer"](payload)

    assert redacted["final_answer"] == final_answer
    assert redacted["raw"]["text"] == "[REDACTED]"
    assert redacted["messages"] == "[REDACTED]"


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
    shutdown_grace = 0.02
    monkeypatch.setattr(
        run_observer_module,
        "LANGSMITH_SHUTDOWN_TIMEOUT_SECONDS",
        shutdown_timeout,
    )
    monkeypatch.setattr(
        run_observer_module,
        "LANGSMITH_SHUTDOWN_GRACE_SECONDS",
        shutdown_grace,
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
