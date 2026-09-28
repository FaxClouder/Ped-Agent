"""
Solution B: Dual-layer evidence structure with group-internal AND / group-external OR.

Key changes from metrics_v2.py:
1. EvidenceGroup now has `required_evidence` (was `alternatives`)
2. Scoring logic: all(required_evidence) within group, any(group) across groups
3. This correctly handles:
   - Single-group multi-evidence (AND): e.g., rgq-m01 needs both b3-09 AND lit-10-1016
   - Multi-group single-evidence (OR): e.g., rgq-073 needs rsif OR ssci
   - Complex structures: (A1 AND A2) OR (B1 AND B2)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RetrievedEvidence(BaseModel):
    """A single evidence locator retrieved by the system."""
    resource_id: str
    version_id: str | None = None
    page: int | None = Field(default=None, ge=1)
    element_id: str | None = None


class EvidenceGroup(BaseModel):
    """
    A group of required evidence that must ALL be present (internal AND).
    Multiple groups are related by OR (any complete group satisfies the question).

    Example 1 (AND): rgq-m01 needs both sources
        evidence_groups: [
            {
                "group_id": "integrated-comparison",
                "required_evidence": [
                    {"resource_id": "b3-09", "page": 1},
                    {"resource_id": "lit-10-1016-j-trc-2019-10-013", "page": 1}
                ]
            }
        ]
        → Score 1.0 only if BOTH present

    Example 2 (OR): rgq-073 needs either source
        evidence_groups: [
            {"group_id": "moussaid-2016", "required_evidence": [{"resource_id": "rsif", "page": 1}]},
            {"group_id": "haghani-2020", "required_evidence": [{"resource_id": "ssci", "page": 23}]}
        ]
        → Score 1.0 if EITHER present
    """
    group_id: str | None = None
    group_description: str | None = None
    required_evidence: list[RetrievedEvidence] = Field(min_length=1)


class GoldQuestionV2(BaseModel):
    """Gold standard question with dual-layer evidence structure."""
    question_id: str
    query: str
    answerable: bool = True
    evidence_groups: list[EvidenceGroup] = Field(default_factory=list)


class EvaluationReportV2(BaseModel):
    """Evaluation report matching the original schema."""
    question_count: int
    answerable_question_count: int
    unanswerable_question_count: int
    k: int
    resource_recall_at_k: float | None
    complete_evidence_at_k: float | None
    locator_hit_rate: float | None
    correct_refusal_rate: float | None
    incorrect_refusal_rate: float | None


def _matches(expected: RetrievedEvidence, actual: RetrievedEvidence) -> bool:
    """Check if actual evidence matches expected evidence (None fields are wildcards)."""
    return all(
        value is None or getattr(actual, field) == value
        for field, value in (
            ("resource_id", expected.resource_id),
            ("version_id", expected.version_id),
            ("page", expected.page),
            ("element_id", expected.element_id),
        )
    )


def _evaluate_evidence_group(
    group: EvidenceGroup,
    retrieved: list[RetrievedEvidence]
) -> bool:
    """
    Check if a group is complete (internal AND logic).

    Returns True if ALL required_evidence in the group are present in retrieved.
    """
    return all(
        any(_matches(expected, actual) for actual in retrieved)
        for expected in group.required_evidence
    )


def evaluate_rankings_v2(
    questions: list[GoldQuestionV2],
    rankings: dict[str, list[RetrievedEvidence]],
    *,
    k: int,
) -> EvaluationReportV2:
    """
    Evaluate retrieval rankings with dual-layer evidence structure.

    Scoring logic:
    - Group-internal: ALL required_evidence must be present (AND)
    - Group-external: ANY complete group satisfies the question (OR)
    - complete_evidence_at_k = 1.0 if at least one group is complete, else 0.0

    Args:
        questions: Gold standard questions with evidence_groups
        rankings: Retrieved evidence per question_id, top-k used
        k: Cutoff for evaluation (top-k results)

    Returns:
        Evaluation report with recall, completeness, and refusal metrics
    """
    if not questions:
        raise ValueError("evaluation requires at least one Gold Question")
    if k < 1:
        raise ValueError("evaluation k must be positive")

    answerable = [q for q in questions if q.answerable]
    unanswerable = [q for q in questions if not q.answerable]

    resource_hits: list[float] = []
    complete_hits: list[float] = []
    locator_hits: list[float] = []

    for question in answerable:
        ranked = rankings.get(question.question_id, [])[:k]
        groups = question.evidence_groups

        # Check which groups are complete
        group_complete = [
            _evaluate_evidence_group(group, ranked)
            for group in groups
        ]

        # Resource recall: at least one evidence from any group
        has_any_evidence = any(
            any(_matches(expected, actual) for actual in ranked)
            for group in groups
            for expected in group.required_evidence
        )
        resource_hits.append(float(has_any_evidence))

        # Complete evidence: at least one group is fully satisfied (external OR)
        is_complete = any(group_complete)
        complete_hits.append(float(is_complete))

        # Locator hit: same as complete (all required locators present)
        locator_hits.append(float(is_complete))

    # Refusal handling for unanswerable questions
    correct_refusals = sum(
        not rankings.get(q.question_id, [])[:k]
        for q in unanswerable
    )
    incorrect_refusals = len(unanswerable) - correct_refusals

    return EvaluationReportV2(
        question_count=len(questions),
        answerable_question_count=len(answerable),
        unanswerable_question_count=len(unanswerable),
        k=k,
        resource_recall_at_k=(sum(resource_hits) / len(answerable) if answerable else None),
        complete_evidence_at_k=(sum(complete_hits) / len(answerable) if answerable else None),
        locator_hit_rate=(sum(locator_hits) / len(answerable) if answerable else None),
        correct_refusal_rate=(correct_refusals / len(unanswerable) if unanswerable else None),
        incorrect_refusal_rate=(incorrect_refusals / len(unanswerable) if unanswerable else None),
    )


__all__ = [
    "EvidenceGroup",
    "EvaluationReportV2",
    "GoldQuestionV2",
    "RetrievedEvidence",
    "evaluate_rankings_v2",
]
