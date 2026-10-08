"""Focused execution checks: accounting and owned-task cleanup, entirely offline."""

import asyncio

import pytest

from ped_agent_harness import BudgetMeter, MemoryRecorder, RunBudget
from ped_agent_harness.model_contracts import (
    ModelCapabilities,
    ModelMessage,
    ModelReply,
    ModelRequest,
    ModelUsage,
)
from ped_agent_harness.models import ModelErrorCode, ModelExecutionError, ModelExecutor


class Port:
    def __init__(self, *, usage=ModelUsage(), block=False, fail_once=False):
        self.usage = usage
        self.block = block
        self.fail_once = fail_once
        self.calls = 0
        self.started = asyncio.Event()
        self.settled = asyncio.Event()

    def capabilities(self, role):
        return ModelCapabilities()

    async def invoke(self, request):
        self.calls += 1
        self.started.set()
        try:
            if self.block:
                await asyncio.Event().wait()
            if self.fail_once and self.calls == 1:
                raise RuntimeError("synthetic transport failure")
            return ModelReply(content="call knowledge.search", model="synthetic", usage=self.usage)
        finally:
            self.settled.set()


def request(**kwargs):
    return ModelRequest(
        run_id="run",
        role="answer",
        max_output_tokens=10,
        messages=(ModelMessage(role="user", content="q"),),
        **kwargs,
    )


@pytest.mark.asyncio
async def test_unknown_usage_is_reserved_not_free_and_no_tool_is_guessed():
    port = Port()
    meter = BudgetMeter(RunBudget(max_tool_calls=1, max_model_calls=2, max_total_output_tokens=10))
    executor = ModelExecutor(port, meter, MemoryRecorder())
    reply = await executor.execute(request(), asyncio.Event())
    assert reply.usage.input_tokens is None and not reply.tool_calls
    usage = meter.usage()
    assert usage.unknown_token_calls == 1 and usage.estimated_output_tokens == 10
    assert usage.estimated_input_tokens > 0 and usage.reserved_input_tokens == 0
    with pytest.raises(ModelExecutionError) as failure:
        await executor.execute(request(), asyncio.Event())
    assert failure.value.code is ModelErrorCode.BUDGET_EXHAUSTED and port.calls == 1


@pytest.mark.asyncio
async def test_retry_attempts_and_repairs_share_the_same_call_budget():
    port = Port(fail_once=True, usage=ModelUsage(input_tokens=2, output_tokens=1))
    meter = BudgetMeter(RunBudget(max_tool_calls=1, max_model_calls=2))
    recorder = MemoryRecorder()
    executor = ModelExecutor(port, meter, recorder, max_retries=1)
    await executor.execute(request(), asyncio.Event())
    assert port.calls == meter.usage().model_calls == 2
    assert meter.usage().unknown_token_calls == 1
    assert [
        event.payload["attempt"] for event in recorder.events if event.type == "model_call"
    ] == [1, 2]
    with pytest.raises(ModelExecutionError):
        await executor.execute(request(), asyncio.Event())
    assert port.calls == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("stop", ["signal", "caller", "timeout"])
async def test_cancel_or_timeout_drains_provider_and_settles_reservation(stop):
    port = Port(block=True)
    meter = BudgetMeter(RunBudget(max_tool_calls=1, max_model_calls=2))
    executor = ModelExecutor(port, meter, MemoryRecorder(), timeout_seconds=0.02)
    cancel = asyncio.Event()
    task = asyncio.create_task(executor.execute(request(), cancel))
    await port.started.wait()
    if stop == "signal":
        cancel.set()
    elif stop == "caller":
        task.cancel()
    with pytest.raises(asyncio.CancelledError if stop == "caller" else ModelExecutionError):
        await task
    assert port.settled.is_set()
    assert meter.usage().model_calls == 1 and meter.usage().reserved_output_tokens == 0


@pytest.mark.asyncio
async def test_unsupported_mode_and_insufficient_budget_never_dispatch():
    port = Port()
    meter = BudgetMeter(RunBudget(max_tool_calls=1, max_model_calls=2, max_total_input_tokens=1))
    executor = ModelExecutor(port, meter, MemoryRecorder())
    for wanted, code in [
        (request(response_schema={"type": "object"}), ModelErrorCode.UNSUPPORTED),
        (request(), ModelErrorCode.BUDGET_EXHAUSTED),
    ]:
        with pytest.raises(ModelExecutionError) as failure:
            await executor.execute(wanted, asyncio.Event())
        assert failure.value.code is code
    assert port.calls == meter.usage().model_calls == 0
