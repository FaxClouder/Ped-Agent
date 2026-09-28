from ped_knowledge.evaluation.metrics_v2 import (
    EvidenceGroup,
    GoldQuestionV2,
    RetrievedEvidence,
    evaluate_rankings_v2,
)


def test_resource_recall_requires_all_evidence_groups() -> None:
    questions = [
        GoldQuestionV2(
            question_id="q1",
            query="q",
            evidence_groups=[
                EvidenceGroup(alternatives=[{"resource_id": "r1", "page": 2}]),
                EvidenceGroup(alternatives=[{"resource_id": "r2", "page": 4}]),
            ],
        )
    ]
    report = evaluate_rankings_v2(
        questions,
        {"q1": [RetrievedEvidence(resource_id="r1", page=2)]},
        k=5,
    )
    assert report.resource_recall_at_k == 1.0
    assert report.complete_evidence_at_k == 0.0


def test_unanswerable_question_scores_refusal_separately() -> None:
    question = GoldQuestionV2(question_id="q1", query="q", answerable=False)
    report = evaluate_rankings_v2(
        [question], {"q1": []}, k=5
    )
    assert report.question_count == 1
    assert report.correct_refusal_rate == 1.0
    assert report.resource_recall_at_k is None


def test_locator_match_includes_resource_version_and_page() -> None:
    question = GoldQuestionV2(
        question_id="q1",
        query="q",
        evidence_groups=[
            EvidenceGroup(
                alternatives=[
                    {"resource_id": "r1", "version_id": "v1", "page": 2}
                ]
            )
        ],
    )
    report = evaluate_rankings_v2(
        [question],
        {"q1": [RetrievedEvidence(resource_id="r1", version_id="v2", page=2)]},
        k=5,
    )
    assert report.locator_hit_rate == 0.0
