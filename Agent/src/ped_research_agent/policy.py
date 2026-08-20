from __future__ import annotations

from ped_contracts.evidence import AnswerDraft, EvidenceItem, EvidenceOrigin, RuleValidation

ORIGIN_PREFIX = {
    EvidenceOrigin.LOCAL_OFFICIAL: "L",
    EvidenceOrigin.EXTERNAL_ACADEMIC: "A",
    EvidenceOrigin.EXTERNAL_WEB: "W",
}


def validate_draft(draft: AnswerDraft, evidence: list[EvidenceItem]) -> RuleValidation:
    errors: list[str] = []
    evidence_by_id = {item.evidence_id: item for item in evidence}
    claims_by_id = {claim.claim_id: claim for claim in draft.claims}
    citations_by_label = {citation.label: citation for citation in draft.citations}

    if not draft.claims:
        errors.append("answer draft must contain at least one claim")
    if not draft.citations:
        errors.append("answer draft must contain at least one citation")

    if len(citations_by_label) != len(draft.citations):
        errors.append("citation labels must be unique")

    for claim in draft.claims:
        if not claim.citation_labels:
            errors.append(f"claim {claim.claim_id} has no citation")
        for label in claim.citation_labels:
            citation = citations_by_label.get(label)
            if citation is None:
                errors.append(f"claim {claim.claim_id} references unknown citation {label}")
            elif claim.claim_id not in citation.claim_ids:
                errors.append(f"citation {label} does not bind claim {claim.claim_id}")

    for citation in draft.citations:
        item = evidence_by_id.get(citation.evidence_id)
        if item is None:
            errors.append(f"citation {citation.label} references unknown evidence")
            continue
        expected_prefix = ORIGIN_PREFIX[item.origin]
        if not citation.label.startswith(expected_prefix):
            errors.append(
                f"citation {citation.label} must use {expected_prefix} prefix "
                f"for {item.origin.value}"
            )
        if f"[{citation.label}]" not in draft.answer_markdown:
            errors.append(f"citation {citation.label} is missing from answer markdown")
        for claim_id in citation.claim_ids:
            claim = claims_by_id.get(claim_id)
            if claim is None:
                errors.append(f"citation {citation.label} references unknown claim {claim_id}")
            elif citation.label not in claim.citation_labels:
                errors.append(f"citation {citation.label} is not declared by claim {claim_id}")

    for inference in draft.inferences:
        for evidence_id in inference.basis_evidence_ids:
            if evidence_id not in evidence_by_id:
                errors.append(f"inference references unknown evidence {evidence_id}")

    return RuleValidation(passed=not errors, errors=errors)
