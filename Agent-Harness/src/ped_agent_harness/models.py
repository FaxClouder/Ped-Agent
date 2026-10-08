"""Budgeted model attempts; provider retries must be disabled by the injected port."""

from __future__ import annotations

import asyncio
import math
from enum import StrEnum

from pydantic import ValidationError

from ped_agent_harness.budget import BudgetMeter
from ped_agent_harness.execution import ExecutionCancelled, ExecutionTimeout, run_cancellable
from ped_agent_harness.model_contracts import (
    ModelPort,
    ModelReply,
    ModelRequest,
    UnsupportedModelCapability,
)
from ped_agent_harness.recorder import Recorder


class ModelErrorCode(StrEnum):
    UNSUPPORTED = "unsupported"
    BUDGET_EXHAUSTED = "budget_exhausted"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    INVALID_RESPONSE = "invalid_response"


class ModelExecutionError(RuntimeError):
    def __init__(self, code: ModelErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code


class ModelExecutor:
    def __init__(
        self,
        provider: ModelPort,
        meter: BudgetMeter,
        recorder: Recorder,
        *,
        timeout_seconds: float = 60,
        max_retries: int = 0,
    ) -> None:
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0 or max_retries < 0:
            raise ValueError("invalid model execution policy")
        self.provider = provider
        self.meter = meter
        self.recorder = recorder
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def _reject(self, request: ModelRequest, code: ModelErrorCode, message: str) -> None:
        self.recorder.emit(
            request.run_id,
            "model_failure",
            {
                "call_id": request.call_id,
                "attempt": 0,
                "code": code.value,
            },
        )
        raise ModelExecutionError(code, message)

    async def execute(self, request: ModelRequest, cancel: asyncio.Event) -> ModelReply:
        try:
            capabilities = self.provider.capabilities(request.role)
            if (request.response_schema is not None and not capabilities.structured) or (
                request.tools and not capabilities.tools
            ):
                raise UnsupportedModelCapability("requested model mode is unsupported")
        except UnsupportedModelCapability as exc:
            self._reject(request, ModelErrorCode.UNSUPPORTED, str(exc))
        estimate = request.input_estimate()
        for attempt in range(1, self.max_retries + 2):
            if cancel.is_set():
                self._reject(request, ModelErrorCode.CANCELLED, "cancelled before dispatch")
            refusal = self.meter.reserve_model_attempt(estimate, request.max_output_tokens)
            if refusal:
                self._reject(request, ModelErrorCode.BUDGET_EXHAUSTED, refusal)
            reply: ModelReply | None = None
            failure: ModelExecutionError | None = None
            recording = True
            try:
                self.recorder.emit(
                    request.run_id,
                    "model_call",
                    {
                        "request": request.model_dump(mode="json"),
                        "attempt": attempt,
                        "input_estimate": estimate,
                        "output_cap": request.max_output_tokens,
                    },
                )
                recording = False
                remaining = self.meter.remaining_seconds()
                timeout = (
                    min(self.timeout_seconds, remaining)
                    if remaining is not None
                    else (self.timeout_seconds)
                )
                received = await run_cancellable(
                    lambda: self.provider.invoke(request), cancel, timeout
                )
                if not isinstance(received, ModelReply):
                    raise ValueError("provider did not return a typed ModelReply")
                reply = ModelReply.model_validate(received.model_dump())
                if reply.tool_calls and not request.tools and request.response_schema is None:
                    raise ValueError("provider returned unsolicited tool calls")
                names = {tool.name for tool in request.tools}
                if request.tools and any(call.name not in names for call in reply.tool_calls):
                    raise ValueError("provider proposed a tool outside the request definitions")
                if len({call.id for call in reply.tool_calls}) != len(reply.tool_calls):
                    raise ValueError("duplicate provider tool-call identities")
            except asyncio.CancelledError:
                self.recorder.emit(
                    request.run_id,
                    "model_failure",
                    {
                        "call_id": request.call_id,
                        "attempt": attempt,
                        "code": "cancelled",
                    },
                )
                raise
            except ExecutionCancelled as exc:
                failure = ModelExecutionError(ModelErrorCode.CANCELLED, str(exc))
            except ExecutionTimeout as exc:
                code = (
                    ModelErrorCode.BUDGET_EXHAUSTED
                    if self.meter.deadline_passed()
                    else ModelErrorCode.TIMEOUT
                )
                failure = ModelExecutionError(code, str(exc))
            except UnsupportedModelCapability as exc:
                failure = ModelExecutionError(ModelErrorCode.UNSUPPORTED, str(exc))
            except (ValidationError, ValueError, TypeError) as exc:
                failure = ModelExecutionError(ModelErrorCode.INVALID_RESPONSE, type(exc).__name__)
            except Exception as exc:
                if recording:
                    raise  # Recorder failures are fatal, not transport failures to retry.
                failure = ModelExecutionError(ModelErrorCode.PROVIDER_ERROR, type(exc).__name__)
            finally:
                self.meter.settle_model_attempt(
                    estimate,
                    request.max_output_tokens,
                    reply.usage.input_tokens if reply else None,
                    reply.usage.output_tokens if reply else None,
                )
            if failure is None and reply is not None:
                self.recorder.emit(
                    request.run_id,
                    "model_reply",
                    {
                        "call_id": request.call_id,
                        "attempt": attempt,
                        "reply": reply.model_dump(mode="json"),
                    },
                )
                if self.meter.tokens_overrun():
                    self._reject(request, ModelErrorCode.BUDGET_EXHAUSTED, "provider token overrun")
                if self.meter.deadline_passed():
                    self._reject(request, ModelErrorCode.BUDGET_EXHAUSTED, "run deadline reached")
                return reply
            assert failure is not None
            self.recorder.emit(
                request.run_id,
                "model_failure",
                {
                    "call_id": request.call_id,
                    "attempt": attempt,
                    "code": failure.code.value,
                    "reply": reply.model_dump(mode="json") if reply else None,
                },
            )
            if failure.code not in (ModelErrorCode.PROVIDER_ERROR, ModelErrorCode.TIMEOUT) or (
                attempt > self.max_retries
            ):
                raise failure
        raise AssertionError("bounded model attempt loop exhausted without outcome")
