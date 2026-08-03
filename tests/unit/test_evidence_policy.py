from datetime import UTC, datetime

from ped_agent.agent.contracts import (
    AnswerClaim,
    AnswerDraft,
    CitationRef,
    EvidenceItem,
    EvidenceOrigin,
)
from ped_agent.agent.policy import validate_draft


def evidence() -> EvidenceItem:
    return EvidenceItem(
        evidence_id="local-1",
        origin=EvidenceOrigin.LOCAL_OFFICIAL,
        title="Paper",
        quote="Verified quote",
        locator="p.1",
        retrieved_at=datetime.now(UTC),
        content_hash="a" * 64,
    )


def test_rule_validation_accepts_claim_bound_to_existing_evidence() -> None:
    draft = AnswerDraft(
        answer_markdown="Verified statement [L1]",
        claims=[AnswerClaim(claim_id="c1", text="Verified statement", citation_labels=["L1"])],
        citations=[CitationRef(label="L1", evidence_id="local-1", claim_ids=["c1"])],
    )

    report = validate_draft(draft, [evidence()])

    assert report.passed is True
    assert report.errors == []


def test_rule_validation_rejects_uncited_claim_and_unknown_evidence() -> None:
    draft = AnswerDraft(
        answer_markdown="Unsupported statement",
        claims=[AnswerClaim(claim_id="c1", text="Unsupported statement")],
        citations=[CitationRef(label="L9", evidence_id="missing", claim_ids=["c1"])],
    )

    report = validate_draft(draft, [evidence()])

    assert report.passed is False
    assert "claim c1 has no citation" in report.errors
    assert "citation L9 references unknown evidence" in report.errors


def test_rule_validation_rejects_citation_without_reciprocal_claim_label() -> None:
    draft = AnswerDraft(
        answer_markdown="Verified statement [L1] [L2]",
        claims=[AnswerClaim(claim_id="c1", text="Verified statement", citation_labels=["L1"])],
        citations=[
            CitationRef(label="L1", evidence_id="local-1", claim_ids=["c1"]),
            CitationRef(label="L2", evidence_id="local-1", claim_ids=["c1"]),
        ],
    )

    report = validate_draft(draft, [evidence()])

    assert report.passed is False
    assert "citation L2 is not declared by claim c1" in report.errors
