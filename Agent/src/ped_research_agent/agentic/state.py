"""Evidence requirements, rather than tool calls, form the domain dependency graph."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ped_contracts.evidence import AnswerDocument, EvidenceItem


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class RequirementStatus(StrEnum):
    OPEN = "open"
    SATISFIED = "satisfied"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    UNSATISFIABLE = "unsatisfiable"
    UNKNOWN = "unknown"


class StopReason(StrEnum):
    QUALITY_STOP = "quality_stop"
    NO_GAIN_STOP = "no_gain_stop"
    PLAN_INVALID = "plan_invalid"
    ALL_BLOCKED = "all_blocked"
    BUDGET_EXHAUSTED = "budget_exhausted"
    CANCELLED = "cancelled"


class Requirement(DomainModel):
    id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    depends_on: list[str] = Field(default_factory=list)
    status: RequirementStatus = RequirementStatus.OPEN
    support_evidence_ids: list[str] = Field(default_factory=list)
    queries_tried: list[str] = Field(default_factory=list)
    rationale: str | None = None
    contradictions: list[str] = Field(default_factory=list)


class RoundRecord(DomainModel):
    round: int = Field(ge=0)
    call_ids: list[str] = Field(default_factory=list)
    queries: list[str] = Field(default_factory=list)
    new_ids: list[str] = Field(default_factory=list)
    duplicate_ids: list[str] = Field(default_factory=list)
    dropped_ids: list[str] = Field(default_factory=list)
    changed_requirement_ids: list[str] = Field(default_factory=list)
    degradation_reasons: list[str] = Field(default_factory=list)


class DecisionState(DomainModel):
    question: str = Field(min_length=1)
    requirements: dict[str, Requirement] = Field(default_factory=dict)
    evidence: dict[str, EvidenceItem] = Field(default_factory=dict)
    first_seen_round: dict[str, int] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    round: int = Field(default=0, ge=0)
    replans_used: int = Field(default=0, ge=0)
    no_gain_rounds: int = Field(default=0, ge=0)
    rounds: list[RoundRecord] = Field(default_factory=list)
    stop_reason: StopReason | None = None

    def validate_plan(self, *, max_requirements: int) -> None:
        if not self.requirements or len(self.requirements) > max_requirements:
            raise ValueError("requirement count outside configured bounds")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(key: str) -> None:
            if key in visiting:
                raise ValueError("requirement dependency cycle")
            if key in visited:
                return
            node = self.requirements.get(key)
            if node is None or key != node.id:
                raise ValueError("missing dependency or mismatched requirement identity")
            if len(set(node.depends_on)) != len(node.depends_on):
                raise ValueError("duplicate requirement dependency")
            visiting.add(key)
            for dependency in node.depends_on:
                visit(dependency)
            visiting.remove(key)
            visited.add(key)

        for key in self.requirements:
            visit(key)

    def ready(self) -> list[Requirement]:
        self.validate_plan(max_requirements=100)
        return [
            node
            for node in self.requirements.values()
            if node.status in (RequirementStatus.OPEN, RequirementStatus.PARTIAL)
            and all(
                self.requirements[dep].status is RequirementStatus.SATISFIED
                for dep in node.depends_on
            )
        ]


class AgenticResult(DomainModel):
    state: DecisionState
    stop_reason: StopReason
    outcome: Literal["answered", "stopped", "failed"]
    answer: AnswerDocument | None = None

    @model_validator(mode="after")
    def consistent_stop(self) -> Self:
        if self.state.stop_reason != self.stop_reason:
            raise ValueError("result and state stop reasons differ")
        if self.answer is not None and self.stop_reason is not StopReason.QUALITY_STOP:
            raise ValueError("non-quality stops must return gaps without an answer")
        if (self.outcome == "answered") != (self.answer is not None):
            raise ValueError("answered outcome requires an answer")
        if self.stop_reason is StopReason.QUALITY_STOP:
            self.state.validate_plan(max_requirements=100)
            for node in self.state.requirements.values():
                if (
                    node.status is not RequirementStatus.SATISFIED
                    or not node.support_evidence_ids
                    or not node.rationale
                    or node.contradictions
                ):
                    raise ValueError("quality stop requires supported, uncontradicted requirements")
                for evidence_id in node.support_evidence_ids:
                    item = self.state.evidence.get(evidence_id)
                    if item is None or item.evidence_id != evidence_id:
                        raise ValueError("requirement references unknown evidence")
        return self
