"""Single-call execution pipeline.

Order: identity → lookup → argument validation → policy (allowlist, budget) → dispatch with
timeout and cancellation → output validation → render → record. Every failure becomes a
ToolFailure; nothing is raised to the caller except the caller's own cancellation.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, JsonValue, ValidationError

from ped_agent_harness.budget import BudgetMeter
from ped_agent_harness.contracts import (
    SideEffect,
    ToolCall,
    ToolErrorCode,
    ToolFailure,
    ToolProvenance,
    ToolRunContext,
    ToolSpec,
    ToolSuccess,
    sha256_json,
)
from ped_agent_harness.recorder import Recorder
from ped_agent_harness.registry import ToolRegistry


@dataclass(frozen=True)
class _Dispatch:
    kind: Literal["ok", "timeout", "cancelled", "error"]
    value: Any = None
    error: BaseException | None = None


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        meter: BudgetMeter,
        recorder: Recorder,
        *,
        allowlist: Iterable[str] | None = None,
    ) -> None:
        self.registry = registry
        self.meter = meter
        self.recorder = recorder
        self.allowlist = None if allowlist is None else frozenset(allowlist)

    def validated_arguments(self, call: ToolCall) -> BaseModel | None:
        tool = self.registry.get(call.tool_name)
        if tool is None:
            return None
        try:
            return tool.input_model.model_validate(call.arguments)
        except ValidationError:
            return None

    async def execute(
        self,
        call: ToolCall,
        cancel_event: asyncio.Event | None = None,
    ) -> ToolSuccess | ToolFailure:
        cancel = cancel_event or asyncio.Event()
        self.recorder.emit(call.run_id, "tool_call", {"call": call.model_dump(mode="json")})
        outcome = await self._run(call, cancel)
        self.recorder.emit(
            call.run_id,
            "tool_outcome",
            {"outcome": outcome.model_dump(mode="json")},
        )
        return outcome

    async def _run(self, call: ToolCall, cancel: asyncio.Event) -> ToolSuccess | ToolFailure:
        provenance = ToolProvenance()
        tool = self.registry.get(call.tool_name)
        if tool is None:
            return _failure(call, ToolErrorCode.UNKNOWN_TOOL, "tool is not registered", provenance)
        provenance.tool_version = tool.version
        provenance.side_effect = tool.side_effect

        try:
            args = tool.input_model.model_validate(call.arguments)
        except ValidationError as exc:
            return _failure(call, ToolErrorCode.INVALID_ARGUMENTS, _short(exc), provenance)

        if self.allowlist is not None and tool.name not in self.allowlist:
            return _failure(call, ToolErrorCode.DENIED, "tool is not in the allowlist", provenance)

        retries = tool.max_retries if tool.side_effect is SideEffect.READONLY else 0
        last: ToolFailure | None = None
        while True:
            if cancel.is_set():
                if last is not None:
                    return last
                return _failure(
                    call,
                    ToolErrorCode.ABORTED_BEFORE_DISPATCH,
                    "run was cancelled before dispatch",
                    provenance,
                )
            refusal = self.meter.try_reserve_tool_call()
            if refusal is not None:
                if last is not None:
                    return last
                return _failure(call, ToolErrorCode.BUDGET_EXHAUSTED, refusal, provenance)

            provenance.attempts += 1
            started = time.perf_counter()
            if provenance.started_at is None:
                provenance.started_at = datetime.now(UTC)
            context = ToolRunContext(call=call, cancel_event=cancel, attempt=provenance.attempts)
            result = await _dispatch(tool, args, context, self._timeout(tool))
            provenance.finished_at = datetime.now(UTC)
            provenance.duration_ms = (time.perf_counter() - started) * 1000

            if result.kind == "ok":
                return _success(call, tool, args, result.value, provenance)

            last = _dispatch_failure(call, tool, result, provenance)
            retryable = result.kind in ("timeout", "error") and not cancel.is_set()
            if not retryable or provenance.attempts > retries:
                return last

    def _timeout(self, tool: ToolSpec[Any, Any]) -> float | None:
        limits = [
            value
            for value in (tool.timeout_seconds, self.meter.remaining_seconds())
            if value is not None
        ]
        return min(limits) if limits else None


async def _dispatch(
    tool: ToolSpec[Any, Any],
    args: BaseModel,
    context: ToolRunContext,
    timeout: float | None,
) -> _Dispatch:
    work = asyncio.create_task(tool.execute(args, context))
    cancel_wait = asyncio.create_task(context.cancel_event.wait())
    try:
        done, _ = await asyncio.wait(
            {work, cancel_wait},
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED,
        )
        if work in done:
            if work.cancelled():
                return _Dispatch("error", error=RuntimeError("tool cancelled itself"))
            error = work.exception()
            if error is not None:
                return _Dispatch("error", error=error)
            return _Dispatch("ok", value=work.result())
        work.cancel()
        # Wait for the tool to settle so no work outlives its recorded outcome.
        await asyncio.gather(work, return_exceptions=True)
        return _Dispatch("cancelled" if cancel_wait in done else "timeout")
    except asyncio.CancelledError:
        work.cancel()
        await asyncio.gather(work, return_exceptions=True)
        raise
    finally:
        cancel_wait.cancel()


def _success(
    call: ToolCall,
    tool: ToolSpec[Any, Any],
    args: BaseModel,
    raw: Any,
    provenance: ToolProvenance,
) -> ToolSuccess | ToolFailure:
    try:
        if isinstance(raw, tool.output_model):
            value_model = tool.output_model.model_validate(raw.model_dump())
        else:
            value_model = tool.output_model.model_validate(raw)
        value: JsonValue = value_model.model_dump(mode="json")
        content = tool.render(args, value_model)
        if not isinstance(content, str):
            raise TypeError("render must return str")
    except (ValidationError, TypeError, ValueError) as exc:
        return _failure(
            call,
            ToolErrorCode.INVALID_OUTPUT,
            _short(exc),
            provenance,
            dispatched=True,
        )
    except Exception as exc:  # renderer bugs must not escape the pipeline
        return _failure(
            call,
            ToolErrorCode.INVALID_OUTPUT,
            f"render failed: {exc!r}",
            provenance,
            dispatched=True,
        )
    return ToolSuccess(
        call=call,
        value=value,
        value_sha256=sha256_json(value),
        content=content,
        provenance=provenance,
    )


def _dispatch_failure(
    call: ToolCall,
    tool: ToolSpec[Any, Any],
    result: _Dispatch,
    provenance: ToolProvenance,
) -> ToolFailure:
    readonly = tool.side_effect is SideEffect.READONLY
    if result.kind == "error":
        return _failure(
            call,
            ToolErrorCode.TOOL_ERROR,
            f"{type(result.error).__name__}: {result.error}",
            provenance,
            dispatched=True,
        )
    if not readonly:
        return _failure(
            call,
            ToolErrorCode.OUTCOME_UNKNOWN,
            f"{result.kind} after dispatch; side effects may have happened",
            provenance,
            dispatched=True,
        )
    if result.kind == "timeout":
        return _failure(call, ToolErrorCode.TIMEOUT, "tool timed out", provenance, dispatched=True)
    return _failure(
        call,
        ToolErrorCode.CANCELLED,
        "run was cancelled during dispatch",
        provenance,
        dispatched=True,
    )


def _failure(
    call: ToolCall,
    code: ToolErrorCode,
    message: str,
    provenance: ToolProvenance,
    *,
    dispatched: bool = False,
) -> ToolFailure:
    return ToolFailure(
        call=call,
        code=code,
        message=message,
        dispatched=dispatched,
        provenance=provenance.model_copy(deep=True),
    )


def _short(exc: Exception) -> str:
    text = str(exc)
    return text if len(text) <= 500 else text[:497] + "..."
