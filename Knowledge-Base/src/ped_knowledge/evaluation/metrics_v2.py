"""Metric-schema-v2 retrieval evaluation with answerability and evidence groups."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RetrievedEvidence(BaseModel):
    resource_id: str
    version_id: str | None = None
    page: int | None = Field(default=None, ge=1)
    element_id: str | None = None


class EvidenceGroup(BaseModel):
    """A required evidence slot; alternatives are interchangeable within a slot."""

    alternatives: list[RetrievedEvidence] = Field(min_length=1)


class GoldQuestionV2(BaseModel):
    question_id: str
    query: str
    answerable: bool = True
    evidence_groups: list[EvidenceGroup] = Field(default_factory=list)


class EvaluationReportV2(BaseModel):
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
    return all(
        value is None or getattr(actual, field) == value
        for field, value in (
            ("resource_id", expected.resource_id),
            ("version_id", expected.version_id),
            ("page", expected.page),
            ("element_id", expected.element_id),
        )
    )


def evaluate_rankings_v2(
    questions: list[GoldQuestionV2],
    rankings: dict[str, list[RetrievedEvidence]],
    *,
    k: int,
) -> EvaluationReportV2:
    if not questions:
        raise ValueError("evaluation requires at least one Gold Question")
    if k < 1:
        raise ValueError("evaluation k must be positive")

    answerable = [question for question in questions if question.answerable]
    unanswerable = [question for question in questions if not question.answerable]
    resource_hits: list[float] = []
    complete_hits: list[float] = []
    locator_hits: list[float] = []
    for question in answerable:
        ranked = rankings.get(question.question_id, [])[:k]
        groups = question.evidence_groups
        matched_groups = [
            any(_matches(expected, actual) for actual in ranked for expected in group.alternatives)
            for group in groups
        ]
        resource_hits.append(float(bool(matched_groups and any(matched_groups))))
        complete_hits.append(float(bool(matched_groups) and all(matched_groups)))
        locator_hits.append(float(bool(matched_groups) and all(matched_groups)))

    correct_refusals = sum(
        not rankings.get(question.question_id, [])[:k] for question in unanswerable
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
