"""Draft → citation rules → semantic verification → bounded revision.

Shared by the fixed EvidenceGraph and future evidence controllers so that ablations change
only how evidence is gathered, not how answers are verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ped_contracts.evidence import (
    AnswerDocument,
    AnswerDraft,
    EvidenceItem,
    RuleValidation,
    SemanticReview,
    VerificationSummary,
)
from ped_research_agent.policy import validate_draft
from ped_research_agent.ports import ModelGateway
from ped_research_agent.prompts import draft_prompt, revision_prompt, verify_prompt
from ped_research_agent.structured import structured_generate, structured_verify

AfterRules = Literal["semantic_verify", "revise_once", "fail_closed"]
AfterSemantic = Literal["final_persist", "revise_once", "fail_closed"]


class VerificationFailed(RuntimeError):
    pass


@dataclass(frozen=True)
class SemanticOutcome:
    passed: bool
    review: SemanticReview
    model: str | None = None
    """Verifier model name; None when no verifier call was made."""


class AnswerChain:
    def __init__(
        self,
        gateway: ModelGateway,
        *,
        allow_rules_only: bool = False,
        revision_limit: int = 1,
    ) -> None:
        self.gateway = gateway
        self.allow_rules_only = allow_rules_only
        self.revision_limit = revision_limit

    async def draft(self, query: str, evidence_pack: str) -> tuple[AnswerDraft, str]:
        return await structured_generate(
            self.gateway, draft_prompt(query, evidence_pack), AnswerDraft
        )

    def validate(self, draft: AnswerDraft, evidence: list[EvidenceItem]) -> RuleValidation:
        return validate_draft(draft, evidence)

    async def semantic_verify(self, draft: AnswerDraft, evidence_pack: str) -> SemanticOutcome:
        if not self.gateway.verification_enabled:
            if not self.allow_rules_only:
                raise VerificationFailed("semantic verification is required")
            return SemanticOutcome(passed=True, review=SemanticReview())
        if not draft.claims:
            return SemanticOutcome(passed=True, review=SemanticReview())
        review, model = await structured_verify(
            self.gateway, verify_prompt(draft, evidence_pack), SemanticReview
        )
        statuses = {item.claim_id: item.status for item in review.claims}
        passed = bool(draft.claims) and all(
            statuses.get(claim.claim_id) == "supported" for claim in draft.claims
        )
        return SemanticOutcome(passed=passed, review=review, model=model)

    async def revise(
        self,
        draft: AnswerDraft,
        rules: RuleValidation,
        review: SemanticReview | None,
        evidence_pack: str,
    ) -> tuple[AnswerDraft, str]:
        return await structured_generate(
            self.gateway, revision_prompt(draft, rules, review, evidence_pack), AnswerDraft
        )

    def after_rules(self, rules: RuleValidation, revision_count: int) -> AfterRules:
        if rules.passed:
            return "semantic_verify"
        return "revise_once" if revision_count < self.revision_limit else "fail_closed"

    def after_semantic(self, semantic_passed: bool, revision_count: int) -> AfterSemantic:
        if semantic_passed:
            return "final_persist"
        return "revise_once" if revision_count < self.revision_limit else "fail_closed"

    @staticmethod
    def failure(rules: RuleValidation) -> VerificationFailed:
        if not rules.passed:
            return VerificationFailed("citation validation failed after revision")
        return VerificationFailed("semantic verification failed after revision")

    def final_answer(self, draft: AnswerDraft, revision_count: int) -> AnswerDocument:
        rules_only = not self.gateway.verification_enabled
        return AnswerDocument(
            answer_markdown=draft.answer_markdown,
            citations=draft.citations,
            inferences=draft.inferences,
            limitations=draft.limitations,
            verification=VerificationSummary(
                status="rules_only" if rules_only else "verified",
                rules_passed=True,
                semantic_passed=None if rules_only else True,
                repaired=revision_count > 0,
            ),
        )
