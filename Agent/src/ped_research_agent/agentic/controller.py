"""Bounded dependency-driven evidence collection; answer synthesis is a separate stage."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Literal

from ped_agent_harness.execution import ExecutionCancelled, ExecutionTimeout, run_cancellable
from ped_agent_harness.models import ModelErrorCode, ModelExecutionError
from ped_agent_harness.recorder import Recorder
from ped_contracts.evidence import EvidenceItem
from ped_research_agent.agentic.config import AgentPolicy
from ped_research_agent.agentic.decisions import (
    DecisionPolicy,
    EvidenceActions,
    Replan,
    ResearchPlan,
    SupportJudgment,
)
from ped_research_agent.agentic.state import (
    AgenticResult,
    DecisionState,
    Requirement,
    RoundRecord,
    StopReason,
)
from ped_research_agent.agentic.state import (
    RequirementStatus as Status,
)
from ped_research_agent.policy import ORIGIN_PREFIX


def merge_plan(state: DecisionState, patch: Replan, policy: AgentPolicy) -> DecisionState:
    """Validate a deep candidate first; rejected patches cannot partially modify live state."""
    patch = Replan.model_validate(patch.model_dump())
    if len(patch.additions) > policy.max_new_requirements_per_replan:
        raise ValueError("too many added requirements")
    candidate = state.model_copy(deep=True)
    for spec in patch.additions:
        if spec.id in candidate.requirements:
            raise ValueError("duplicate requirement ID")
        candidate.requirements[spec.id] = spec.requirement()
    for key, queries in patch.replace_queries.items():
        node = candidate.requirements.get(key)
        if node is None or node.status is Status.SATISFIED:
            raise ValueError("query replacement targets missing or satisfied requirement")
        if not queries or len(set(queries)) != len(queries):
            raise ValueError("replacement queries must be nonempty and unique")
        if not any(query not in node.queries_tried for query in queries):
            raise ValueError("replacement has no untried query")
        node.queries = list(queries)
        node.status = Status.PARTIAL if node.support_evidence_ids else Status.OPEN
    candidate.validate_plan(max_requirements=policy.max_requirements)
    return candidate


def _identity(item: EvidenceItem) -> tuple[object, ...]:
    # Retrieval time/rank may change, source identity and quoted content may not.
    return (
        item.origin,
        item.resource_id,
        item.version_id,
        item.chunk_id,
        item.content_hash,
        item.quote,
        item.locator,
        item.url,
        item.doi,
    )


def _block_dependents(state: DecisionState) -> None:
    for _ in state.requirements:
        changed = False
        for node in state.requirements.values():
            failed = any(
                state.requirements[dep].status in (Status.UNSATISFIABLE, Status.BLOCKED)
                or (
                    state.requirements[dep].status is not Status.SATISFIED
                    and not _untried(state.requirements[dep])
                )
                for dep in node.depends_on
            )
            if failed and node.status is not Status.BLOCKED:
                node.status = Status.BLOCKED
                changed = True
            elif not failed and node.status is Status.BLOCKED:
                node.status = Status.PARTIAL if node.support_evidence_ids else Status.OPEN
                changed = True
        if not changed:
            break


def _untried(node: Requirement) -> list[str]:
    return [query for query in node.queries if query not in node.queries_tried]


class EvidenceController:
    def __init__(
        self,
        policy: DecisionPolicy,
        actions: EvidenceActions,
        limits: AgentPolicy,
        recorder: Recorder,
        *,
        run_id: str,
        cancel_event: asyncio.Event,
        remaining_seconds: Callable[[], float | None],
    ) -> None:
        self.policy, self.actions, self.limits = policy, actions, limits
        self.recorder, self.run_id = recorder, run_id
        self.cancel = cancel_event
        self.remaining_seconds = remaining_seconds
        self._started = False

    def _finish(self, state: DecisionState, reason: StopReason) -> AgenticResult:
        state.stop_reason = reason
        result = AgenticResult(
            state=state,
            stop_reason=reason,
            outcome="failed"
            if reason in (StopReason.PLAN_INVALID, StopReason.EXECUTION_FAILED)
            else "stopped",
        )
        self.recorder.emit(self.run_id, "decision_end", result.model_dump(mode="json"))
        return result

    async def execute(self, question: str) -> AgenticResult:
        if self._started:
            raise ValueError("controller instances are single-run")
        self._started = True
        state = DecisionState(question=question)
        try:
            return await run_cancellable(
                lambda: self._collect(state), self.cancel, self.remaining_seconds()
            )
        except (ExecutionCancelled, asyncio.CancelledError) as exc:
            result = self._finish(state, StopReason.CANCELLED)
            if isinstance(exc, asyncio.CancelledError):
                raise
            return result
        except ExecutionTimeout:
            return self._finish(state, StopReason.BUDGET_EXHAUSTED)
        except ModelExecutionError as exc:
            reason = {
                ModelErrorCode.BUDGET_EXHAUSTED: StopReason.BUDGET_EXHAUSTED,
                ModelErrorCode.CANCELLED: StopReason.CANCELLED,
            }.get(exc.code, StopReason.EXECUTION_FAILED)
            return self._finish(state, reason)
        except Exception as exc:
            self.recorder.emit(self.run_id, "decision_failure", {"type": type(exc).__name__})
            return self._finish(state, StopReason.EXECUTION_FAILED)

    async def _collect(self, state: DecisionState) -> AgenticResult:
        try:
            plan = ResearchPlan.model_validate(
                (await self.policy.plan(state.question)).model_dump()
            )
            for spec in plan.requirements:
                if spec.id in state.requirements:
                    raise ValueError("duplicate requirement ID")
                state.requirements[spec.id] = spec.requirement()
            state.validate_plan(max_requirements=self.limits.max_requirements)
        except ValueError as exc:
            self.recorder.emit(self.run_id, "plan_invalid", {"reason": str(exc)})
            return self._finish(state, StopReason.PLAN_INVALID)
        self.recorder.emit(self.run_id, "plan", state.model_dump(mode="json"))
        while True:
            if self.cancel.is_set():
                return self._finish(state, StopReason.CANCELLED)
            if self.actions.exhausted():
                return self._finish(state, StopReason.BUDGET_EXHAUSTED)
            _block_dependents(state)
            if all(node.status is Status.SATISFIED for node in state.requirements.values()):
                return self._finish(state, StopReason.QUALITY_STOP)
            if state.round >= self.limits.max_rounds:
                return self._finish(state, StopReason.ROUND_LIMIT)
            ready = [node for node in state.ready() if _untried(node)]
            if not ready:
                return self._finish(state, StopReason.ALL_BLOCKED)
            state.round += 1
            record = RoundRecord(round=state.round)
            state.rounds.append(record)
            failed = False
            for node in ready:
                if self.cancel.is_set():
                    return self._finish(state, StopReason.CANCELLED)
                query = _untried(node)[0]
                node.queries_tried.append(query)
                record.queries.append(query)
                action = await self.actions.search(query, state.round)
                record.call_ids.extend(action.call_ids)
                record.degradation_reasons.extend(action.degradation_reasons)
                if action.stop:
                    return self._finish(state, StopReason(action.stop))
                if action.error:
                    failed = True
                    record.degradation_reasons.append(action.error)
                    node.status = Status.UNKNOWN if _untried(node) else Status.UNSATISFIABLE
                    node.rationale = action.error
                    continue
                for item in action.items:
                    old = state.evidence.get(item.evidence_id)
                    if old is not None:
                        if _identity(old) != _identity(item):
                            record.dropped_ids.append(item.evidence_id)
                            record.degradation_reasons.append("evidence_identity_conflict")
                            failed = True
                        else:
                            record.duplicate_ids.append(item.evidence_id)
                        continue
                    state.evidence[item.evidence_id] = item.model_copy(deep=True)
                    state.first_seen_round[item.evidence_id] = state.round
                    state.labels[item.evidence_id] = (
                        f"{ORIGIN_PREFIX[item.origin]}{len(state.labels) + 1}"
                    )
                    record.new_ids.append(item.evidence_id)
                try:
                    judgment = SupportJudgment.model_validate(
                        (await self.policy.judge(state.model_copy(deep=True), node.id)).model_dump()
                    )
                    if not set(judgment.support_evidence_ids) <= state.evidence.keys():
                        raise ValueError("judgment references unknown evidence")
                    before = node.model_copy(deep=True)
                    node.status = Status(judgment.status)
                    node.support_evidence_ids = list(judgment.support_evidence_ids)
                    node.contradictions = list(judgment.contradictions)
                    node.rationale = judgment.rationale
                    if node.status is Status.UNKNOWN and not _untried(node):
                        node.status = Status.UNSATISFIABLE
                    # More citations alone do not prove more facts. Count a stronger
                    # supported status or resolution of a previously recorded conflict.
                    gained = node.status is Status.PARTIAL and before.status not in (
                        Status.PARTIAL,
                        Status.SATISFIED,
                    )
                    gained |= (
                        node.status is Status.SATISFIED and before.status is not Status.SATISFIED
                    )
                    gained |= (
                        bool(before.contradictions)
                        and not node.contradictions
                        and node.status in (Status.PARTIAL, Status.SATISFIED)
                    )
                    if gained:
                        record.support_gain_ids.append(node.id)
                    if node != before:
                        record.changed_requirement_ids.append(node.id)
                    self.recorder.emit(
                        self.run_id,
                        "support_judgment",
                        {
                            "requirement_id": node.id,
                            "before": before.model_dump(mode="json"),
                            "after": node.model_dump(mode="json"),
                            "support_gain": gained,
                        },
                    )
                except ValueError as exc:
                    failed = True
                    node.status = Status.UNKNOWN if _untried(node) else Status.UNSATISFIABLE
                    node.rationale = "support_judgment_invalid"
                    record.degradation_reasons.append(str(exc))
            _block_dependents(state)
            gained = bool(record.new_ids or record.support_gain_ids)
            state.no_gain_rounds = 0 if gained else state.no_gain_rounds + 1
            trigger: Literal["round_done", "action_failed", "no_gain"] = (
                "action_failed" if failed else "round_done" if gained else "no_gain"
            )
            if not all(node.status is Status.SATISFIED for node in state.requirements.values()):
                if state.no_gain_rounds >= self.limits.no_gain_limit:
                    return self._finish(state, StopReason.NO_GAIN_STOP)
                if state.round >= self.limits.max_rounds:
                    return self._finish(state, StopReason.ROUND_LIMIT)
                if state.replans_used < self.limits.max_replans:
                    state.replans_used += 1  # Invalid/empty attempts also consume the bounded slot.
                    try:
                        patch = await self.policy.replan(state.model_copy(deep=True), trigger)
                        candidate = merge_plan(state, patch, self.limits)
                        state.requirements = candidate.requirements
                        self.recorder.emit(
                            self.run_id,
                            "replan",
                            {
                                "trigger": trigger,
                                "patch": patch.model_dump(mode="json"),
                                "replans_used": state.replans_used,
                            },
                        )
                    except ValueError as exc:
                        record.replan_error = str(exc)
                        state.no_gain_rounds += int(gained)
                        self.recorder.emit(
                            self.run_id,
                            "replan_parse_failed",
                            {
                                "trigger": trigger,
                                "reason": str(exc),
                            },
                        )
                elif not any(_untried(n) for n in state.ready()):
                    return self._finish(state, StopReason.REPLAN_LIMIT)
            self.recorder.emit(
                self.run_id,
                "round_end",
                {
                    "record": record.model_dump(mode="json"),
                    "no_gain_rounds": state.no_gain_rounds,
                    "state": state.model_dump(mode="json"),
                },
            )
            if state.no_gain_rounds >= self.limits.no_gain_limit:
                return self._finish(state, StopReason.NO_GAIN_STOP)
