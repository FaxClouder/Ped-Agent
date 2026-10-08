from __future__ import annotations

import pytest
from pydantic import ValidationError

from ped_agent_harness import BudgetMeter, RunBudget


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


def test_budget_rejects_non_positive_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        RunBudget(max_tool_calls=0, max_model_calls=1)
    with pytest.raises(ValidationError):
        RunBudget(max_tool_calls=1, max_model_calls=1, max_rounds=3)  # type: ignore[call-arg]


def test_model_calls_and_tokens_are_metered() -> None:
    meter = BudgetMeter(RunBudget(max_tool_calls=1, max_model_calls=3, max_total_input_tokens=100))

    assert meter.try_reserve_model_call() is None
    meter.record_model_usage(80, 10)
    assert meter.try_reserve_model_call() is None
    meter.record_model_usage(None, None)
    meter.record_model_usage(30, 5)

    assert meter.try_reserve_model_call() == "token limit reached"
    usage = meter.usage()
    assert (usage.model_calls, usage.input_tokens, usage.unknown_token_calls) == (2, 110, 1)


def test_deadline_blocks_all_reservations() -> None:
    clock = FakeClock()
    meter = BudgetMeter(
        RunBudget(max_tool_calls=5, max_model_calls=5, deadline_seconds=10), clock=clock
    )

    assert meter.remaining_seconds() == 10
    clock.now += 10

    assert meter.try_reserve_tool_call() == "deadline reached"
    assert meter.try_reserve_model_call() == "deadline reached"
    assert meter.usage().tool_calls == 0
