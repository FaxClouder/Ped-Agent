"""Run-level budgets; every attempt is charged, including failures and retries."""

from __future__ import annotations

import time
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict, Field


class RunBudget(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_tool_calls: int = Field(gt=0)
    max_model_calls: int = Field(gt=0)
    max_total_input_tokens: int | None = Field(default=None, gt=0)
    max_total_output_tokens: int | None = Field(default=None, gt=0)
    deadline_seconds: float | None = Field(default=None, gt=0)


class BudgetUsage(BaseModel):
    tool_calls: int = 0
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    unknown_token_calls: int = 0
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    reserved_input_tokens: int = 0
    reserved_output_tokens: int = 0
    elapsed_seconds: float = 0.0


class BudgetMeter:
    """Counts usage against one RunBudget. Not shared across runs."""

    def __init__(self, budget: RunBudget, *, clock: Callable[[], float] = time.monotonic) -> None:
        self.budget = budget
        self._clock = clock
        self._started = clock()
        self._tool_calls = 0
        self._model_calls = 0
        self._input_tokens = 0
        self._output_tokens = 0
        self._unknown_token_calls = 0
        self._estimated_input = 0
        self._estimated_output = 0
        self._reserved_input = 0
        self._reserved_output = 0

    def deadline_passed(self) -> bool:
        limit = self.budget.deadline_seconds
        return limit is not None and self._clock() - self._started >= limit

    def remaining_seconds(self) -> float | None:
        limit = self.budget.deadline_seconds
        if limit is None:
            return None
        return max(0.0, limit - (self._clock() - self._started))

    def tokens_exhausted(self) -> bool:
        max_in = self.budget.max_total_input_tokens
        max_out = self.budget.max_total_output_tokens
        return (max_in is not None and self._input_tokens + self._estimated_input >= max_in) or (
            max_out is not None and self._output_tokens + self._estimated_output >= max_out
        )

    def exhausted_reason(self, kind: str) -> str | None:
        if self.deadline_passed():
            return "deadline reached"
        if kind == "tool" and self._tool_calls >= self.budget.max_tool_calls:
            return f"tool call limit {self.budget.max_tool_calls} reached"
        if kind == "model":
            if self._model_calls >= self.budget.max_model_calls:
                return f"model call limit {self.budget.max_model_calls} reached"
            if self.tokens_exhausted():
                return "token limit reached"
        return None

    def try_reserve_tool_call(self) -> str | None:
        """Charge one tool attempt; returns the refusal reason when over budget."""
        reason = self.exhausted_reason("tool")
        if reason is None:
            self._tool_calls += 1
        return reason

    def try_reserve_model_call(self) -> str | None:
        reason = self.exhausted_reason("model")
        if reason is None:
            self._model_calls += 1
        return reason

    def record_model_usage(self, input_tokens: int | None, output_tokens: int | None) -> None:
        if input_tokens is None or output_tokens is None:
            self._unknown_token_calls += 1
        self._input_tokens += input_tokens or 0
        self._output_tokens += output_tokens or 0

    def reserve_model_attempt(self, input_estimate: int, output_cap: int) -> str | None:
        if input_estimate < 0 or output_cap <= 0:
            raise ValueError("invalid model token reservation")
        refusal = self.exhausted_reason("model")
        if refusal:
            return refusal
        for requested, used, estimated, reserved, maximum in (
            (
                input_estimate,
                self._input_tokens,
                self._estimated_input,
                self._reserved_input,
                self.budget.max_total_input_tokens,
            ),
            (
                output_cap,
                self._output_tokens,
                self._estimated_output,
                self._reserved_output,
                self.budget.max_total_output_tokens,
            ),
        ):
            if maximum is not None and used + estimated + reserved + requested > maximum:
                return "insufficient remaining token budget"
        self._model_calls += 1
        self._reserved_input += input_estimate
        self._reserved_output += output_cap
        return None

    def settle_model_attempt(
        self,
        input_estimate: int,
        output_cap: int,
        input_tokens: int | None,
        output_tokens: int | None,
    ) -> None:
        self._reserved_input -= input_estimate
        self._reserved_output -= output_cap
        self.record_model_usage(input_tokens, output_tokens)
        if input_tokens is None:
            self._estimated_input += input_estimate
        if output_tokens is None:
            self._estimated_output += output_cap

    def tokens_overrun(self) -> bool:
        return any(
            limit is not None and actual + estimated > limit
            for actual, estimated, limit in (
                (self._input_tokens, self._estimated_input, self.budget.max_total_input_tokens),
                (self._output_tokens, self._estimated_output, self.budget.max_total_output_tokens),
            )
        )

    def usage(self) -> BudgetUsage:
        return BudgetUsage(
            tool_calls=self._tool_calls,
            model_calls=self._model_calls,
            input_tokens=self._input_tokens,
            output_tokens=self._output_tokens,
            unknown_token_calls=self._unknown_token_calls,
            estimated_input_tokens=self._estimated_input,
            estimated_output_tokens=self._estimated_output,
            reserved_input_tokens=self._reserved_input,
            reserved_output_tokens=self._reserved_output,
            elapsed_seconds=self._clock() - self._started,
        )
