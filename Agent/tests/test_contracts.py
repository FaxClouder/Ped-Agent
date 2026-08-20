from datetime import UTC, datetime

from ped_contracts.evidence import (
    AnswerDocument,
    CitationRef,
    EvidenceItem,
    EvidenceOrigin,
    InferenceItem,
    RunStatus,
    VerificationSummary,
)


def test_answer_document_preserves_evidence_and_inference_boundaries() -> None:
    evidence = EvidenceItem(
        evidence_id="local-1",
        origin=EvidenceOrigin.LOCAL_OFFICIAL,
        title="Pedestrian flow paper",
        quote="Density increases near the bottleneck.",
        locator="page 4",
        retrieved_at=datetime.now(UTC),
        content_hash="a" * 64,
        score=0.91,
    )

    document = AnswerDocument(
        answer_markdown="结论 [L1]",
        citations=[CitationRef(label="L1", evidence_id=evidence.evidence_id, claim_ids=["c1"])],
        inferences=[
            InferenceItem(text="建议增加现场复核。", basis_evidence_ids=[evidence.evidence_id])
        ],
        limitations=["当前只有一篇正式文献。"],
        verification=VerificationSummary(
            status="verified",
            rules_passed=True,
            semantic_passed=True,
        ),
    )

    assert RunStatus.INTERRUPTED.value == "interrupted"
    assert document.citations[0].label == "L1"
    assert document.inferences[0].text.startswith("建议")
