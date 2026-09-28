"""
Test cases for Solution B scoring logic (dual-layer evidence structure).

Test scenarios:
1. Single-group, single-evidence (baseline, should match old behavior)
2. Single-group, multi-evidence (AND logic)
3. Multi-group, single-evidence (OR logic)
4. Multi-group, multi-evidence (complex: (A1 AND A2) OR (B1 AND B2))
"""

import pytest
from ped_knowledge.evaluation.metrics_v2_solution_b import (
    EvidenceGroup,
    GoldQuestionV2,
    RetrievedEvidence,
    evaluate_rankings_v2,
)


# --- Test Scenario 1: Single-group, single-evidence (baseline) ---

def test_single_group_single_evidence_full_match():
    """Baseline: single evidence required, retrieved."""
    questions = [
        GoldQuestionV2(
            question_id="q1",
            query="Test query",
            evidence_groups=[
                EvidenceGroup(
                    group_id="g1",
                    required_evidence=[
                        RetrievedEvidence(resource_id="doc1", page=1)
                    ]
                )
            ]
        )
    ]
    rankings = {
        "q1": [
            RetrievedEvidence(resource_id="doc1", page=1),
            RetrievedEvidence(resource_id="doc2", page=1),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 1.0
    assert report.resource_recall_at_k == 1.0


def test_single_group_single_evidence_no_match():
    """Baseline: single evidence required, not retrieved."""
    questions = [
        GoldQuestionV2(
            question_id="q1",
            query="Test query",
            evidence_groups=[
                EvidenceGroup(
                    group_id="g1",
                    required_evidence=[
                        RetrievedEvidence(resource_id="doc1", page=1)
                    ]
                )
            ]
        )
    ]
    rankings = {
        "q1": [
            RetrievedEvidence(resource_id="doc2", page=1),
            RetrievedEvidence(resource_id="doc3", page=2),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 0.0
    assert report.resource_recall_at_k == 0.0


# --- Test Scenario 2: Single-group, multi-evidence (AND logic) ---

def test_single_group_multi_evidence_both_present():
    """AND logic: both required, both retrieved → complete."""
    questions = [
        GoldQuestionV2(
            question_id="rgq-m01",
            query="Lyon vs ring-corridor",
            evidence_groups=[
                EvidenceGroup(
                    group_id="integrated-comparison",
                    required_evidence=[
                        RetrievedEvidence(resource_id="b3-09", page=1),
                        RetrievedEvidence(resource_id="lit-10-1016-j-trc-2019-10-013", page=1),
                    ]
                )
            ]
        )
    ]
    rankings = {
        "rgq-m01": [
            RetrievedEvidence(resource_id="b3-09", page=1),
            RetrievedEvidence(resource_id="lit-10-1016-j-trc-2019-10-013", page=1),
            RetrievedEvidence(resource_id="other-doc", page=5),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 1.0  # Both present
    assert report.resource_recall_at_k == 1.0


def test_single_group_multi_evidence_partial():
    """AND logic: both required, only one retrieved → incomplete."""
    questions = [
        GoldQuestionV2(
            question_id="rgq-m01",
            query="Lyon vs ring-corridor",
            evidence_groups=[
                EvidenceGroup(
                    group_id="integrated-comparison",
                    required_evidence=[
                        RetrievedEvidence(resource_id="b3-09", page=1),
                        RetrievedEvidence(resource_id="lit-10-1016-j-trc-2019-10-013", page=1),
                    ]
                )
            ]
        )
    ]
    rankings = {
        "rgq-m01": [
            RetrievedEvidence(resource_id="b3-09", page=1),
            RetrievedEvidence(resource_id="other-doc", page=5),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 0.0  # Only one of two
    assert report.resource_recall_at_k == 1.0     # Has at least one


def test_single_group_multi_evidence_none_present():
    """AND logic: both required, none retrieved → incomplete."""
    questions = [
        GoldQuestionV2(
            question_id="rgq-m01",
            query="Lyon vs ring-corridor",
            evidence_groups=[
                EvidenceGroup(
                    group_id="integrated-comparison",
                    required_evidence=[
                        RetrievedEvidence(resource_id="b3-09", page=1),
                        RetrievedEvidence(resource_id="lit-10-1016-j-trc-2019-10-013", page=1),
                    ]
                )
            ]
        )
    ]
    rankings = {
        "rgq-m01": [
            RetrievedEvidence(resource_id="other-doc", page=5),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 0.0
    assert report.resource_recall_at_k == 0.0


# --- Test Scenario 3: Multi-group, single-evidence (OR logic) ---

def test_multi_group_single_evidence_first_group():
    """OR logic: two groups, first group satisfied → complete."""
    questions = [
        GoldQuestionV2(
            question_id="rgq-073",
            query="Virtual environment herding mechanism",
            evidence_groups=[
                EvidenceGroup(
                    group_id="moussaid-2016",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1098-rsif-2016-0414", page=1)
                    ]
                ),
                EvidenceGroup(
                    group_id="haghani-2020",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1016-j-ssci-2020-104743", page=23)
                    ]
                )
            ]
        )
    ]
    rankings = {
        "rgq-073": [
            RetrievedEvidence(resource_id="lit-10-1098-rsif-2016-0414", page=1),
            RetrievedEvidence(resource_id="other-doc", page=5),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 1.0  # First group complete
    assert report.resource_recall_at_k == 1.0


def test_multi_group_single_evidence_second_group():
    """OR logic: two groups, second group satisfied → complete."""
    questions = [
        GoldQuestionV2(
            question_id="rgq-073",
            query="Virtual environment herding mechanism",
            evidence_groups=[
                EvidenceGroup(
                    group_id="moussaid-2016",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1098-rsif-2016-0414", page=1)
                    ]
                ),
                EvidenceGroup(
                    group_id="haghani-2020",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1016-j-ssci-2020-104743", page=23)
                    ]
                )
            ]
        )
    ]
    rankings = {
        "rgq-073": [
            RetrievedEvidence(resource_id="lit-10-1016-j-ssci-2020-104743", page=23),
            RetrievedEvidence(resource_id="other-doc", page=5),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 1.0  # Second group complete
    assert report.resource_recall_at_k == 1.0


def test_multi_group_single_evidence_both_groups():
    """OR logic: two groups, both satisfied → complete (still 1.0)."""
    questions = [
        GoldQuestionV2(
            question_id="rgq-073",
            query="Virtual environment herding mechanism",
            evidence_groups=[
                EvidenceGroup(
                    group_id="moussaid-2016",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1098-rsif-2016-0414", page=1)
                    ]
                ),
                EvidenceGroup(
                    group_id="haghani-2020",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1016-j-ssci-2020-104743", page=23)
                    ]
                )
            ]
        )
    ]
    rankings = {
        "rgq-073": [
            RetrievedEvidence(resource_id="lit-10-1098-rsif-2016-0414", page=1),
            RetrievedEvidence(resource_id="lit-10-1016-j-ssci-2020-104743", page=23),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 1.0  # Both groups complete
    assert report.resource_recall_at_k == 1.0


def test_multi_group_single_evidence_none():
    """OR logic: two groups, neither satisfied → incomplete."""
    questions = [
        GoldQuestionV2(
            question_id="rgq-073",
            query="Virtual environment herding mechanism",
            evidence_groups=[
                EvidenceGroup(
                    group_id="moussaid-2016",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1098-rsif-2016-0414", page=1)
                    ]
                ),
                EvidenceGroup(
                    group_id="haghani-2020",
                    required_evidence=[
                        RetrievedEvidence(resource_id="lit-10-1016-j-ssci-2020-104743", page=23)
                    ]
                )
            ]
        )
    ]
    rankings = {
        "rgq-073": [
            RetrievedEvidence(resource_id="other-doc", page=5),
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 0.0
    assert report.resource_recall_at_k == 0.0


# --- Test Scenario 4: Multi-group, multi-evidence (complex) ---

def test_multi_group_multi_evidence_first_complete():
    """Complex: (A1 AND A2) OR (B1 AND B2), first group complete → complete."""
    questions = [
        GoldQuestionV2(
            question_id="complex",
            query="Complex structure",
            evidence_groups=[
                EvidenceGroup(
                    group_id="groupA",
                    required_evidence=[
                        RetrievedEvidence(resource_id="A1", page=1),
                        RetrievedEvidence(resource_id="A2", page=2),
                    ]
                ),
                EvidenceGroup(
                    group_id="groupB",
                    required_evidence=[
                        RetrievedEvidence(resource_id="B1", page=1),
                        RetrievedEvidence(resource_id="B2", page=2),
                    ]
                )
            ]
        )
    ]
    rankings = {
        "complex": [
            RetrievedEvidence(resource_id="A1", page=1),
            RetrievedEvidence(resource_id="A2", page=2),
            RetrievedEvidence(resource_id="B1", page=1),  # Partial for groupB
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 1.0  # groupA complete
    assert report.resource_recall_at_k == 1.0


def test_multi_group_multi_evidence_partial_both():
    """Complex: (A1 AND A2) OR (B1 AND B2), both partial → incomplete."""
    questions = [
        GoldQuestionV2(
            question_id="complex",
            query="Complex structure",
            evidence_groups=[
                EvidenceGroup(
                    group_id="groupA",
                    required_evidence=[
                        RetrievedEvidence(resource_id="A1", page=1),
                        RetrievedEvidence(resource_id="A2", page=2),
                    ]
                ),
                EvidenceGroup(
                    group_id="groupB",
                    required_evidence=[
                        RetrievedEvidence(resource_id="B1", page=1),
                        RetrievedEvidence(resource_id="B2", page=2),
                    ]
                )
            ]
        )
    ]
    rankings = {
        "complex": [
            RetrievedEvidence(resource_id="A1", page=1),  # Partial for groupA
            RetrievedEvidence(resource_id="B1", page=1),  # Partial for groupB
        ]
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 0.0  # Neither group complete
    assert report.resource_recall_at_k == 1.0     # Has some evidence


# --- Edge cases ---

def test_empty_rankings():
    """Edge case: no rankings provided."""
    questions = [
        GoldQuestionV2(
            question_id="q1",
            query="Test",
            evidence_groups=[
                EvidenceGroup(
                    required_evidence=[RetrievedEvidence(resource_id="doc1", page=1)]
                )
            ]
        )
    ]
    rankings = {}
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 0.0
    assert report.resource_recall_at_k == 0.0


def test_unanswerable_question():
    """Edge case: unanswerable question with empty rankings → correct refusal."""
    questions = [
        GoldQuestionV2(
            question_id="unans",
            query="Unanswerable",
            answerable=False,
            evidence_groups=[]
        )
    ]
    rankings = {"unans": []}
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.unanswerable_question_count == 1
    assert report.correct_refusal_rate == 1.0


def test_multiple_questions_mixed():
    """Integration: multiple questions with different structures."""
    questions = [
        # Single-group AND
        GoldQuestionV2(
            question_id="q1",
            query="Test 1",
            evidence_groups=[
                EvidenceGroup(
                    required_evidence=[
                        RetrievedEvidence(resource_id="A", page=1),
                        RetrievedEvidence(resource_id="B", page=1),
                    ]
                )
            ]
        ),
        # Multi-group OR
        GoldQuestionV2(
            question_id="q2",
            query="Test 2",
            evidence_groups=[
                EvidenceGroup(required_evidence=[RetrievedEvidence(resource_id="C", page=1)]),
                EvidenceGroup(required_evidence=[RetrievedEvidence(resource_id="D", page=1)]),
            ]
        ),
    ]
    rankings = {
        "q1": [
            RetrievedEvidence(resource_id="A", page=1),
            RetrievedEvidence(resource_id="B", page=1),
        ],
        "q2": [
            RetrievedEvidence(resource_id="C", page=1),
        ],
    }
    report = evaluate_rankings_v2(questions, rankings, k=5)
    assert report.complete_evidence_at_k == 1.0  # Both complete (2/2)
    assert report.resource_recall_at_k == 1.0
