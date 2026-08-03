from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Protocol, TypeVar
from uuid import UUID

from langsmith import Client
from langsmith.anonymizer import create_secret_anonymizer
from langsmith.run_helpers import tracing_context
from ped_agent import __version__ as application_version

from ped_agent_server.settings import LangSmithSettings
from ped_agent_server.trace_sanitization import redact_trace_payload

T = TypeVar("T")
logger = logging.getLogger(__name__)
LANGSMITH_SHUTDOWN_TIMEOUT_SECONDS = 5.0


class ObservableRunContext(Protocol):
    run_id: str
    conversation_id: str


class RunObserver(Protocol):
    async def observe_run(
        self,
        context: ObservableRunContext,
        operation: Callable[[], Awaitable[T]],
    ) -> T: ...

    async def record_feedback(
        self,
        run_id: str,
        metrics: Mapping[str, bool | int | float | str | None],
    ) -> None: ...

    async def close(self) -> None: ...


class NoOpRunObserver:
    async def observe_run(
        self,
        context: ObservableRunContext,
        operation: Callable[[], Awaitable[T]],
    ) -> T:
        with tracing_context(enabled=False):
            return await operation()

    async def record_feedback(
        self,
        run_id: str,
        metrics: Mapping[str, bool | int | float | str | None],
    ) -> None:
        return None

    async def close(self) -> None:
        return None


class LangSmithObserver:
    def __init__(
        self,
        settings: LangSmithSettings,
        *,
        answer_model: str,
        verify_model: str,
        embedding_model: str,
        external_search_enabled: bool,
        verification_required: bool,
        client: Client | None = None,
    ) -> None:
        self.settings = settings
        self.answer_model = answer_model
        self.verify_model = verify_model
        self.embedding_model = embedding_model
        self.external_search_enabled = external_search_enabled
        self.verification_required = verification_required
        self.client = client if client is not None else _build_client(settings)

    async def observe_run(
        self,
        context: ObservableRunContext,
        operation: Callable[[], Awaitable[T]],
    ) -> T:
        with tracing_context(
            project_name=self.settings.project,
            tags=[
                "feature:evidence-qa",
                "environment:local",
                f"answer-model:{self.answer_model}",
                f"verify-model:{self.verify_model}",
                f"embedding-model:{self.embedding_model}",
                "graph-version:v1",
            ],
            metadata={
                "run_id": context.run_id,
                "conversation_id": context.conversation_id,
                "graph_version": "v1",
                "application_version": application_version,
                "answer_model": self.answer_model,
                "verify_model": self.verify_model,
                "embedding_model": self.embedding_model,
                "external_search_enabled": self.external_search_enabled,
                "verification_required": self.verification_required,
            },
            enabled=True,
            client=self.client,
        ):
            return await operation()

    async def record_feedback(
        self,
        run_id: str,
        metrics: Mapping[str, bool | int | float | str | None],
    ) -> None:
        try:
            feedback_run_id = UUID(run_id)
        except (AttributeError, TypeError, ValueError) as error:
            logger.warning(
                "LangSmith feedback skipped for invalid run_id: %s",
                type(error).__name__,
            )
            return

        for key, value in metrics.items():
            if value is None:
                continue
            kwargs = {"score": value} if isinstance(value, (bool, float)) else {"value": value}
            try:
                await asyncio.to_thread(
                    self.client.create_feedback,
                    run_id=feedback_run_id,
                    key=key,
                    **kwargs,
                )
            except Exception as error:  # noqa: BLE001 - observability must not break runs
                logger.warning(
                    "LangSmith feedback failed for key %s: %s",
                    key,
                    type(error).__name__,
                )

    async def close(self) -> None:
        timeout = LANGSMITH_SHUTDOWN_TIMEOUT_SECONDS
        for name, operation in (
            ("flush", self.client.flush),
            ("close", self.client.close),
        ):
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(operation, timeout=timeout),
                    timeout=timeout,
                )
            except Exception as error:  # noqa: BLE001 - shutdown must attempt both steps
                logger.warning(
                    "LangSmith shutdown failed during %s: %s",
                    name,
                    type(error).__name__,
                )


def _build_client(settings: LangSmithSettings) -> Client:
    secret_anonymizer = create_secret_anonymizer()

    def anonymizer(payload: dict[str, Any]) -> dict[str, Any]:
        return redact_trace_payload(secret_anonymizer(payload))

    def tracing_error(error: Exception) -> None:
        logger.warning("LangSmith tracing failed: %s", type(error).__name__)

    return Client(
        api_url=settings.endpoint,
        api_key=(settings.api_key.get_secret_value() if settings.api_key is not None else None),
        anonymizer=anonymizer,
        tracing_sampling_rate=settings.sampling_rate,
        tracing_error_callback=tracing_error,
    )
