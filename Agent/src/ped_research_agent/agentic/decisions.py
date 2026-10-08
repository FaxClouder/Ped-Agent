"""Domain policy contracts: plans are requirements, never executable tool programs."""

from __future__ import annotations

from typing import Annotated, Literal, Protocol, Self

from pydantic import Field, model_validator

from ped_contracts.evidence import EvidenceItem
from ped_research_agent.agentic.state import DecisionState, DomainModel, Requirement

Query = Annotated[str, Field(min_length=1, pattern=r"\S")]


class RequirementSpec(DomainModel):
    id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    depends_on: list[str] = Field(default_factory=list)
    queries: list[Query] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_queries(self) -> Self:
        if len(set(self.queries)) != len(self.queries):
            raise ValueError("duplicate planned query")
        return self

    def requirement(self) -> Requirement:
        return Requirement(**self.model_dump())


class ResearchPlan(DomainModel):
    requirements: list[RequirementSpec] = Field(min_length=1)


class Replan(DomainModel):
    additions: list[RequirementSpec] = Field(default_factory=list)
    replace_queries: dict[str, list[Query]] = Field(default_factory=dict)
    rationale: str = Field(min_length=1)


class SupportJudgment(DomainModel):
    status: Literal["satisfied", "partial", "unknown", "unsatisfiable"]
    support_evidence_ids: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def supported_status(self) -> Self:
        if len(set(self.support_evidence_ids)) != len(self.support_evidence_ids):
            raise ValueError("duplicate support identity")
        if self.status in ("satisfied", "partial") and not self.support_evidence_ids:
            raise ValueError("supported status requires evidence")
        if self.status == "satisfied" and self.contradictions:
            raise ValueError("contradictory evidence cannot satisfy a requirement")
        return self


class DecisionPolicy(Protocol):
    async def plan(self, question: str) -> ResearchPlan: ...
    async def judge(self, state: DecisionState, requirement_id: str) -> SupportJudgment: ...
    async def replan(
        self, state: DecisionState, trigger: Literal["round_done", "action_failed", "no_gain"]
    ) -> Replan: ...


class ActionResult(DomainModel):
    call_ids: list[str] = Field(default_factory=list)
    items: list[EvidenceItem] = Field(default_factory=list)
    error: str | None = None
    stop: Literal["budget_exhausted", "cancelled"] | None = None
    degradation_reasons: list[str] = Field(default_factory=list)


class EvidenceActions(Protocol):
    """Production implementation must dispatch through the shared Harness executor."""

    async def search(self, query: str, round: int) -> ActionResult: ...
    def exhausted(self) -> bool: ...
