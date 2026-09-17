from __future__ import annotations

from pathlib import Path

import pytest

from ped_knowledge.evaluation import (
    EvaluationAcceptanceConfig,
    EvaluationReport,
    GoldQuestion,
    audit_evaluation,
    load_gold,
    validate_gold_resources,
)


def _acceptance_config(*, minimum_question_count: int = 1) -> EvaluationAcceptanceConfig:
    return EvaluationAcceptanceConfig(
        minimum_question_count=minimum_question_count,
        k=5,
        minimum_recall_at_k=0.8,
        minimum_mrr=0.7,
        minimum_locator_hit_rate=0.75,
        maximum_non_official_leakage=0.0,
    )


def _report(*, question_count: int) -> EvaluationReport:
    return EvaluationReport(
        question_count=question_count,
        k=5,
        recall_at_k=1.0,
        mrr=1.0,
        ndcg_at_k=1.0,
        locator_hit_rate=1.0,
    )


def test_acceptance_uses_a_minimum_question_count() -> None:
    accepted = audit_evaluation(
        _report(question_count=2),
        _acceptance_config(minimum_question_count=1),
        non_official_leakage=0.0,
    )
    rejected = audit_evaluation(
        _report(question_count=1),
        _acceptance_config(minimum_question_count=2),
        non_official_leakage=0.0,
    )

    assert accepted.is_compliant
    assert rejected.errors == ("Gold Question count is below 2",)


def test_gold_resource_validation_reports_missing_ids() -> None:
    questions = [
        GoldQuestion(
            question_id="q1",
            query="query",
            expected_resource_ids=["missing"],
            expected_locators=["p.1"],
        )
    ]

    with pytest.raises(ValueError, match="missing"):
        validate_gold_resources(questions, {"present"})


def test_repository_pilot_gold_matches_the_runtime_contract() -> None:
    root = Path(__file__).resolve().parents[2]
    questions = load_gold(root / "memPed" / "knowledge" / "pilot_gold.jsonl")

    assert len(questions) == 31
    assert questions[0].expected_resource_ids == [
        "helbing-1995-social-force",
        "t1-06",
    ]
    assert questions[0].expected_locators == [
        "p.2",
        "p.3",
        "p.4",
        "p.5",
        "p.6",
        "p.7",
    ]
