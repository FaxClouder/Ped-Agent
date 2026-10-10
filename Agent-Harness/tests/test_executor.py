from __future__ import annotations

import asyncio
from typing import Any

import pytest
from pydantic import BaseModel, Field

from ped_agent_harness import (
    TOOL_OUTCOME_ADAPTER,
    BudgetMeter,
    JsonlRecorder,
    MemoryRecorder,
    RunBudget,
    SideEffect,
    ToolCall,
    ToolErrorCode,
    ToolExecutor,
    ToolFailure,
    ToolRegistry,
    ToolRunContext,
    ToolScheduler,
    ToolSpec,
    ToolSuccess,
)
from ped_agent_harness.recorder import read_events


class SearchArgs(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=3, ge=1, le=20)


class SearchValue(BaseModel):
    evidence_ids: list[str]
    degraded: bool = False


class Search(ToolSpec[SearchArgs, SearchValue]):
    name = "knowledge.search"
    version = "test-1"
    description = "Search frozen evidence."
    input_model = SearchArgs
    output_model = SearchValue

    def __init__(self, delay: float = 0.0) -> None:
        self.delay = delay
        self.executed: list[str] = []
        self.active = 0
        self.max_active = 0

    def parallel_safe(self, args: SearchArgs) -> bool:
        return True

    async def execute(self, args: SearchArgs, ctx: ToolRunContext) -> SearchValue:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(self.delay)
            self.executed.append(args.query)
            return SearchValue(evidence_ids=[f"{args.query}-{i}" for i in range(args.limit)])
        finally:
            self.active -= 1

    def render(self, args: SearchArgs, value: SearchValue) -> str:
        return ", ".join(value.evidence_ids)


class Empty(BaseModel):
    pass


class Done(BaseModel):
    ok: bool = True


class Slow(ToolSpec[Empty, Done]):
    name = "slow"
    version = "test-1"
    description = "Sleeps."
    input_model = Empty
    output_model = Done
    timeout_seconds = 0.05

    def __init__(self) -> None:
        self.started = 0
        self.settled = 0

    async def execute(self, args: Empty, ctx: ToolRunContext) -> Done:
        self.started += 1
        try:
            await asyncio.sleep(10)
        finally:
            self.settled += 1
        return Done()


class SlowWrite(Slow):
    name = "slow_write"
    side_effect = SideEffect.CREATES_ARTIFACT


class Flaky(ToolSpec[Empty, Done]):
    name = "flaky"
    version = "test-1"
    description = "Fails a fixed number of times."
    input_model = Empty
    output_model = Done
    max_retries = 2

    def __init__(self, failures: int) -> None:
        self.failures = failures
        self.calls = 0

    async def execute(self, args: Empty, ctx: ToolRunContext) -> Done:
        self.calls += 1
        if self.calls <= self.failures:
            raise ConnectionError("index unavailable")
        return Done()


class FlakyWrite(Flaky):
    name = "flaky_write"
    side_effect = SideEffect.CREATES_ARTIFACT


class BadOutput(ToolSpec[Empty, Done]):
    name = "bad_output"
    version = "test-1"
    description = "Returns the wrong shape."
    input_model = Empty
    output_model = Done

    async def execute(self, args: Empty, ctx: ToolRunContext) -> Any:
        return {"ok": "not-a-bool"}


class BadRender(ToolSpec[Empty, Done]):
    name = "bad_render"
    version = "test-1"
    description = "Renderer raises."
    input_model = Empty
    output_model = Done

    async def execute(self, args: Empty, ctx: ToolRunContext) -> Done:
        return Done()

    def render(self, args: Empty, value: Done) -> str:
        raise KeyError("missing")


def make(
    *tools: ToolSpec[Any, Any],
    max_tool_calls: int = 10,
    allowlist: list[str] | None = None,
    deadline: float | None = None,
) -> tuple[ToolExecutor, MemoryRecorder]:
    recorder = MemoryRecorder()
    meter = BudgetMeter(
        RunBudget(max_tool_calls=max_tool_calls, max_model_calls=5, deadline_seconds=deadline)
    )
    return ToolExecutor(ToolRegistry(tools), meter, recorder, allowlist=allowlist), recorder


def call(tool_name: str, round: int = 0, **arguments: Any) -> ToolCall:
    return ToolCall.create(run_id="run-1", tool_name=tool_name, arguments=arguments, round=round)


def run(coro: Any) -> Any:
    return asyncio.run(coro)


def test_success_keeps_canonical_value_and_rendered_content() -> None:
    executor, recorder = make(Search())

    outcome = run(executor.execute(call("knowledge.search", query="flow", limit=2)))

    assert isinstance(outcome, ToolSuccess)
    assert outcome.value == {"evidence_ids": ["flow-0", "flow-1"], "degraded": False}
    assert outcome.content == "flow-0, flow-1"
    assert outcome.provenance.tool_version == "test-1"
    assert outcome.provenance.attempts == 1
    assert [event.type for event in recorder.events] == ["tool_call", "tool_outcome"]
    assert [event.seq for event in recorder.events] == [1, 2]


def test_invalid_arguments_never_reach_the_tool_or_the_budget() -> None:
    search = Search()
    executor, _ = make(search)

    outcome = run(executor.execute(call("knowledge.search", query="", limit=99)))

    assert isinstance(outcome, ToolFailure)
    assert outcome.code is ToolErrorCode.INVALID_ARGUMENTS
    assert outcome.dispatched is False
    assert search.executed == []
    assert executor.meter.usage().tool_calls == 0


def test_unknown_and_denied_tools_fail_without_dispatch() -> None:
    executor, _ = make(Search(), allowlist=[])

    unknown = run(executor.execute(call("missing")))
    denied = run(executor.execute(call("knowledge.search", query="flow")))

    assert unknown.code is ToolErrorCode.UNKNOWN_TOOL
    assert denied.code is ToolErrorCode.DENIED
    assert not unknown.dispatched and not denied.dispatched


def test_budget_exhaustion_is_reported_and_not_dispatched() -> None:
    search = Search()
    executor, _ = make(search, max_tool_calls=1)

    first = run(executor.execute(call("knowledge.search", query="a")))
    second = run(executor.execute(call("knowledge.search", query="b")))

    assert isinstance(first, ToolSuccess)
    assert second.code is ToolErrorCode.BUDGET_EXHAUSTED
    assert search.executed == ["a"]


def test_readonly_retries_are_charged_to_the_budget() -> None:
    flaky = Flaky(failures=2)
    executor, _ = make(flaky)

    outcome = run(executor.execute(call("flaky")))

    assert isinstance(outcome, ToolSuccess)
    assert outcome.provenance.attempts == 3
    assert executor.meter.usage().tool_calls == 3


def test_retry_stops_at_budget_and_returns_last_failure() -> None:
    flaky = Flaky(failures=5)
    executor, _ = make(flaky, max_tool_calls=2)

    outcome = run(executor.execute(call("flaky")))

    assert outcome.code is ToolErrorCode.TOOL_ERROR
    assert outcome.provenance.attempts == 2
    assert flaky.calls == 2


def test_side_effect_tools_are_never_retried() -> None:
    flaky = FlakyWrite(failures=1)
    executor, _ = make(flaky)

    outcome = run(executor.execute(call("flaky_write")))

    assert outcome.code is ToolErrorCode.TOOL_ERROR
    assert flaky.calls == 1


def test_timeout_waits_for_the_tool_to_settle() -> None:
    slow = Slow()
    executor, _ = make(slow)

    outcome = run(executor.execute(call("slow")))

    assert outcome.code is ToolErrorCode.TIMEOUT
    assert outcome.dispatched is True
    assert slow.started == slow.settled == 1


def test_timeout_on_side_effect_tool_is_outcome_unknown() -> None:
    executor, _ = make(SlowWrite())

    outcome = run(executor.execute(call("slow_write")))

    assert outcome.code is ToolErrorCode.OUTCOME_UNKNOWN


def test_deadline_bounds_tool_timeout() -> None:
    class Unbounded(Slow):
        name = "unbounded"
        timeout_seconds = None

    tool = Unbounded()
    executor, _ = make(tool, deadline=0.05)

    outcome = run(executor.execute(call("unbounded")))

    assert outcome.code is ToolErrorCode.TIMEOUT
    assert tool.settled == 1


def test_cancellation_before_and_during_dispatch_are_distinct() -> None:
    class Long(Slow):
        name = "long"
        timeout_seconds = None

    tool = Long()
    executor, _ = make(tool)

    async def scenario() -> tuple[Any, Any]:
        cancel = asyncio.Event()
        task = asyncio.create_task(executor.execute(call("long"), cancel))
        await asyncio.sleep(0.01)
        cancel.set()
        during = await task
        before = await executor.execute(call("long"), cancel)
        return during, before

    during, before = run(scenario())

    assert during.code is ToolErrorCode.CANCELLED and during.dispatched
    assert before.code is ToolErrorCode.ABORTED_BEFORE_DISPATCH and not before.dispatched
    assert tool.started == tool.settled == 1


def test_invalid_output_and_render_errors_are_contained() -> None:
    executor, _ = make(BadOutput(), BadRender())

    bad_output = run(executor.execute(call("bad_output")))
    bad_render = run(executor.execute(call("bad_render")))

    assert bad_output.code is ToolErrorCode.INVALID_OUTPUT
    assert bad_render.code is ToolErrorCode.INVALID_OUTPUT
    assert bad_output.dispatched and bad_render.dispatched


def test_scheduler_returns_outcomes_in_request_order() -> None:
    search = Search(delay=0.02)
    executor, _ = make(search, Flaky(failures=0))
    scheduler = ToolScheduler(executor, max_parallel=2)
    calls = [
        call("knowledge.search", query="a"),
        call("knowledge.search", query="b"),
        call("knowledge.search", query="c"),
        call("flaky"),
        call("knowledge.search", query="d"),
    ]

    outcomes = run(scheduler.run_batch(calls))

    assert [o.call.call_id for o in outcomes] == [c.call_id for c in calls]
    assert all(isinstance(o, ToolSuccess) for o in outcomes)
    assert search.max_active == 2


def test_scheduler_is_serial_by_default() -> None:
    search = Search(delay=0.01)
    executor, _ = make(search)

    run(ToolScheduler(executor).run_batch([call("knowledge.search", query=q) for q in "abc"]))

    assert search.max_active == 1
    assert search.executed == ["a", "b", "c"]


def test_scheduler_records_synthetic_results_after_cancel() -> None:
    search = Search()
    executor, recorder = make(search)
    cancel = asyncio.Event()
    cancel.set()

    outcomes = run(
        ToolScheduler(executor).run_batch([call("knowledge.search", query="a")] * 2, cancel)
    )

    assert all(o.code is ToolErrorCode.ABORTED_BEFORE_DISPATCH for o in outcomes)
    assert search.executed == []
    assert sum(event.type == "tool_outcome" for event in recorder.events) == 2


def test_call_identity_is_frozen_and_hashed_canonically() -> None:
    first = ToolCall.create(run_id="r", tool_name="t", arguments={"b": 1, "a": [1, 2]})
    second = ToolCall.create(run_id="r", tool_name="t", arguments={"a": [1, 2], "b": 1})

    assert first.arguments_sha256 == second.arguments_sha256
    with pytest.raises(ValueError):
        first.tool_name = "other"  # type: ignore[misc]


def test_outcomes_round_trip_through_jsonl(tmp_path: Any) -> None:
    path = tmp_path / "run" / "events.jsonl"
    with JsonlRecorder(path) as recorder:
        meter = BudgetMeter(RunBudget(max_tool_calls=3, max_model_calls=1))
        executor = ToolExecutor(ToolRegistry([Search()]), meter, recorder)
        original = run(executor.execute(call("knowledge.search", query="flow")))

    events = read_events(path)
    restored = TOOL_OUTCOME_ADAPTER.validate_python(events[1].payload["outcome"])

    assert restored == original
    with pytest.raises(FileExistsError):
        JsonlRecorder(path)


def test_definitions_expose_only_model_facing_fields() -> None:
    registry = ToolRegistry([Search(), Slow()])

    definitions = registry.definitions(allowlist=["knowledge.search"])

    assert [d.name for d in definitions] == ["knowledge.search"]
    assert set(definitions[0].model_dump()) == {"name", "description", "parameters"}
    assert definitions[0].parameters["required"] == ["query"]
