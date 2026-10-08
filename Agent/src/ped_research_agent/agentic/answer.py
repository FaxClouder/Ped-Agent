"""Dynamic evidence selection and orchestration of the unchanged shared AnswerChain."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

from ped_agent_harness.execution import ExecutionCancelled, ExecutionTimeout, run_cancellable
from ped_agent_harness.models import ModelErrorCode, ModelExecutionError, ModelExecutor
from ped_agent_harness.recorder import Recorder
from ped_contracts.evidence import EvidenceItem, RuleValidation, SemanticReview
from ped_research_agent.agentic.config import AgentPolicy
from ped_research_agent.agentic.decisions import DecisionPolicy, SupportJudgment
from ped_research_agent.agentic.state import (
    AgenticResult,
    DecisionState,
    RequirementGap,
    StopReason,
)
from ped_research_agent.agentic.state import (
    RequirementStatus as Status,
)
from ped_research_agent.answer_chain import AnswerChain, VerificationFailed
from ped_research_agent.integrations.models import MeteredModelGateway
from ped_research_agent.policy import ORIGIN_PREFIX


@dataclass(frozen=True)
class DynamicContext:
    items: list[EvidenceItem]
    text: str
    dropped_ids: list[str]
    estimate: int
    missing_support_ids: list[str]


def select_context(state: DecisionState, policy: AgentPolicy) -> DynamicContext:
    """Keep complete canonical quotes and required supports before optional context."""
    required = {key for node in state.requirements.values() for key in node.support_evidence_ids}
    ordered = sorted(state.evidence, key=lambda key: key not in required)
    selected: list[EvidenceItem] = []
    payload: list[dict[str, object]] = []
    for key in ordered:
        item = state.evidence[key]
        label = state.labels.get(key)
        if not label or not label.startswith(ORIGIN_PREFIX[item.origin]):
            raise ValueError("missing or incompatible stable evidence label")
        candidate = [*payload, {"label": label, **item.model_dump(mode="json")}]
        text = json.dumps(candidate, ensure_ascii=False)
        # Conservative UTF-8 byte occupancy, explicitly not a provider tokenizer.
        if (
            len(selected) < policy.max_context_items
            and len(text.encode()) <= policy.max_context_tokens
        ):
            selected.append(item)
            payload = candidate
    selected_ids = {item.evidence_id for item in selected}
    text = json.dumps(payload, ensure_ascii=False)
    return DynamicContext(
        selected,
        text,
        [key for key in state.evidence if key not in selected_ids],
        len(text.encode()),
        sorted(required - selected_ids),
    )


def stopped_result(
    state: DecisionState, reason: StopReason, *, failed: bool = False
) -> AgenticResult:
    state.stop_reason = reason
    gaps = [
        RequirementGap(
            id=node.id,
            statement=node.statement,
            status=node.status,
            reason=node.rationale or reason.value,
        )
        for node in state.requirements.values()
        if node.status is not Status.SATISFIED
    ]
    if not gaps:
        gaps = [
            RequirementGap(
                id="final_answer",
                statement="Verified research answer",
                status=Status.UNKNOWN,
                reason=reason.value,
            )
        ]
    return AgenticResult(
        state=state, stop_reason=reason, outcome="failed" if failed else "stopped", gaps=gaps
    )


class DynamicAnswerChain:
    def __init__(
        self,
        models: ModelExecutor,
        decisions: DecisionPolicy,
        limits: AgentPolicy,
        recorder: Recorder,
        *,
        run_id: str,
        cancel_event: asyncio.Event,
        max_output_tokens: int,
    ) -> None:
        self.models, self.decisions, self.limits = models, decisions, limits
        self.recorder, self.run_id, self.cancel = recorder, run_id, cancel_event
        self.chain = AnswerChain(
            MeteredModelGateway(
                models,
                run_id=run_id,
                cancel_event=cancel_event,
                max_output_tokens=max_output_tokens,
            )
        )

    async def execute(self, collected: AgenticResult) -> AgenticResult:
        collected = AgenticResult.model_validate(collected.model_dump())
        state = collected.state.model_copy(deep=True)
        if collected.stop_reason is not StopReason.QUALITY_STOP:
            return stopped_result(
                state, collected.stop_reason, failed=collected.outcome == "failed"
            )
        try:
            result = await run_cancellable(
                lambda: self._answer(state), self.cancel, self.models.meter.remaining_seconds()
            )
        except (ExecutionCancelled, asyncio.CancelledError) as exc:
            result = stopped_result(state, StopReason.CANCELLED)
            self.recorder.emit(self.run_id, "answer_end", result.model_dump(mode="json"))
            if isinstance(exc, asyncio.CancelledError):
                raise
            return result
        except ExecutionTimeout:
            result = stopped_result(state, StopReason.BUDGET_EXHAUSTED)
        except ModelExecutionError as exc:
            reason = {
                ModelErrorCode.BUDGET_EXHAUSTED: StopReason.BUDGET_EXHAUSTED,
                ModelErrorCode.CANCELLED: StopReason.CANCELLED,
            }.get(exc.code, StopReason.EXECUTION_FAILED)
            result = stopped_result(state, reason, failed=reason is StopReason.EXECUTION_FAILED)
        except VerificationFailed:
            result = stopped_result(state, StopReason.VERIFICATION_FAILED)
        except ValueError:
            result = stopped_result(state, StopReason.EXECUTION_FAILED, failed=True)
        except Exception:
            result = stopped_result(state, StopReason.EXECUTION_FAILED, failed=True)
        self.recorder.emit(self.run_id, "answer_end", result.model_dump(mode="json"))
        return result

    async def _answer(self, state: DecisionState) -> AgenticResult:
        context = select_context(state, self.limits)
        self.recorder.emit(
            self.run_id,
            "context_selection",
            {
                "retained_ids": [item.evidence_id for item in context.items],
                "dropped_ids": [key for key in context.dropped_ids],
                "input_estimate": context.estimate,
                "labels": dict(state.labels),
                "estimate_kind": "utf8_bytes",
                "missing_support_ids": [key for key in context.missing_support_ids],
            },
        )
        if context.missing_support_ids:
            return stopped_result(state, StopReason.CONTEXT_LIMIT)
        if context.dropped_ids:
            retained = state.model_copy(deep=True)
            retained.evidence = {item.evidence_id: item for item in context.items}
            retained.labels = {key: retained.labels[key] for key in retained.evidence}
            retained.first_seen_round = {
                key: retained.first_seen_round[key] for key in retained.evidence
            }
            for node in retained.requirements.values():
                judgment = SupportJudgment.model_validate(
                    (
                        await self.decisions.judge(retained.model_copy(deep=True), node.id)
                    ).model_dump()
                )
                if (
                    judgment.status != "satisfied"
                    or not set(judgment.support_evidence_ids) <= retained.evidence.keys()
                ):
                    node.status = Status(judgment.status)
                    node.rationale = "support lost after context selection"
                    state.requirements = retained.requirements
                    return stopped_result(state, StopReason.SUPPORT_LOST)
                node.support_evidence_ids = judgment.support_evidence_ids
                node.rationale, node.contradictions = judgment.rationale, judgment.contradictions
            state.requirements = retained.requirements
            self.recorder.emit(
                self.run_id,
                "context_support_confirmed",
                {
                    "requirements": {
                        key: node.model_dump(mode="json")
                        for key, node in state.requirements.items()
                    }
                },
            )
        draft, model = await self.chain.draft(state.question, context.text)
        revision_count = 0
        review: SemanticReview | None = None
        while True:
            rules = self.chain.validate(draft, context.items)
            # The shared rules validate origin prefixes; dynamic bindings additionally stay exact.
            errors = [
                f"citation {c.label} changes stable evidence binding"
                for c in draft.citations
                if state.labels.get(c.evidence_id) != c.label
            ]
            if errors:
                rules = RuleValidation(passed=False, errors=[*rules.errors, *errors])
            next_step: str = self.chain.after_rules(rules, revision_count)
            if next_step == "semantic_verify":
                semantic = await self.chain.semantic_verify(draft, context.text)
                review = semantic.review
                next_step = self.chain.after_semantic(semantic.passed, revision_count)
            self.recorder.emit(
                self.run_id,
                "answer_validation",
                {
                    "draft": draft.model_dump(mode="json"),
                    "model": model,
                    "rules": rules.model_dump(mode="json"),
                    "review": review.model_dump(mode="json") if review else None,
                    "revision_count": revision_count,
                    "next_step": next_step,
                },
            )
            if next_step == "final_persist":
                if self.models.meter.deadline_passed() or self.cancel.is_set():
                    return stopped_result(
                        state,
                        StopReason.CANCELLED
                        if self.cancel.is_set()
                        else StopReason.BUDGET_EXHAUSTED,
                    )
                answer = self.chain.final_answer(draft, revision_count)
                if answer.verification.status != "verified":
                    raise VerificationFailed("dynamic answers require semantic verification")
                return AgenticResult(
                    state=state,
                    stop_reason=StopReason.QUALITY_STOP,
                    outcome="answered",
                    answer=answer,
                )
            if next_step == "fail_closed":
                raise self.chain.failure(rules)
            draft, model = await self.chain.revise(draft, rules, review, context.text)
            revision_count += 1
