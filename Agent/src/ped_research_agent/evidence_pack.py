from __future__ import annotations

import json
from collections.abc import Mapping

from ped_contracts.evidence import EvidenceItem, EvidenceOrigin
from ped_research_agent.policy import ORIGIN_PREFIX

DEFAULT_ORIGIN_LIMITS: Mapping[EvidenceOrigin, int] = {
    EvidenceOrigin.LOCAL_OFFICIAL: 8,
    EvidenceOrigin.EXTERNAL_ACADEMIC: 5,
    EvidenceOrigin.EXTERNAL_WEB: 5,
}


def select_evidence(
    items: list[EvidenceItem],
    limits: Mapping[EvidenceOrigin, int] = DEFAULT_ORIGIN_LIMITS,
) -> list[EvidenceItem]:
    """Deduplicate by evidence ID and keep the first items of each origin up to its limit."""
    result: list[EvidenceItem] = []
    counts: dict[EvidenceOrigin, int] = {}
    seen: set[str] = set()
    for item in items:
        if item.evidence_id in seen or counts.get(item.origin, 0) >= limits[item.origin]:
            continue
        seen.add(item.evidence_id)
        counts[item.origin] = counts.get(item.origin, 0) + 1
        result.append(item)
    return result


def origin_counts(evidence: list[EvidenceItem]) -> dict[str, int]:
    return {
        "local": sum(item.origin is EvidenceOrigin.LOCAL_OFFICIAL for item in evidence),
        "academic": sum(item.origin is EvidenceOrigin.EXTERNAL_ACADEMIC for item in evidence),
        "web": sum(item.origin is EvidenceOrigin.EXTERNAL_WEB for item in evidence),
    }


def pack_evidence(evidence: list[EvidenceItem]) -> str:
    """Serialize evidence for prompts, numbering labels per origin in list order."""
    counters = {origin: 0 for origin in EvidenceOrigin}
    payload: list[dict[str, object]] = []
    for item in evidence:
        counters[item.origin] += 1
        payload.append(
            {
                "label": f"{ORIGIN_PREFIX[item.origin]}{counters[item.origin]}",
                **item.model_dump(mode="json"),
            }
        )
    return json.dumps(payload, ensure_ascii=False)
