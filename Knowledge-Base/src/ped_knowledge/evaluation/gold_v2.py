"""Pure Gold v2 scoring for versioned, grouped evidence annotations.

This module calculates exploratory metrics. It does not approve candidate labels
or activate a retrieval configuration.
"""

from __future__ import annotations

import math
from collections import defaultdict
from functools import lru_cache


def _resource_matches(hit: dict, alternative: dict) -> bool:
    return hit["resource_id"] == alternative["resource_id"]


def _locator_matches(hit: dict, alternative: dict) -> bool:
    if not _resource_matches(hit, alternative):
        return False
    if hit["version_id"] != alternative["source_pdf_sha256"]:
        return False
    locator = alternative["locator"]
    page = locator["page_index"] + 1
    if not hit["page_start"] <= page <= hit["page_end"]:
        return False
    element = locator.get("element_id")
    return element is None or element in hit["element_ids"]


def score_answerable(evidence: dict, ranking: list[dict], *, k: int = 5) -> dict[str, float]:
    """Score one variant; groups are AND, alternatives within a group are OR.

    Resource recall is the fraction of required evidence groups represented by
    at least one ranked resource. Each group contributes at most one nDCG gain.
    The ranking is reduced to distinct resources before applying ``k``.
    """
    if k < 1:
        raise ValueError("k must be positive")
    groups = evidence.get("evidence_groups", [])
    if not groups or any(not group.get("alternatives") for group in groups):
        raise ValueError("answerable evidence requires nonempty groups")
    selected: list[dict] = []
    seen: set[str] = set()
    for hit in ranking:
        resource_id = hit["resource_id"]
        if resource_id in seen:
            continue
        seen.add(resource_id)
        selected.append(hit)
        if len(selected) == k:
            break

    selected_resources = {hit["resource_id"] for hit in selected}
    selected_chunks = [hit for hit in ranking if hit["resource_id"] in selected_resources]

    group_hits = [
        any(_resource_matches(hit, alt) for hit in selected for alt in group["alternatives"])
        for group in groups
    ]
    locator_hits = [
        any(_locator_matches(hit, alt) for hit in selected_chunks for alt in group["alternatives"])
        for group in groups
    ]
    first_rank = next(
        (
            rank
            for rank, hit in enumerate(selected, 1)
            if any(_resource_matches(hit, alt) for group in groups for alt in group["alternatives"])
        ),
        None,
    )
    covered = 0
    dcg = 0.0
    for rank, hit in enumerate(selected, 1):
        matching = sum(
            (1 << index)
            for index, group in enumerate(groups)
            if any(_resource_matches(hit, alt) for alt in group["alternatives"])
        )
        new = matching & ~covered
        dcg += new.bit_count() / math.log2(rank + 1)
        covered |= matching

    resources = {alt["resource_id"] for group in groups for alt in group["alternatives"]}
    coverage_masks = tuple(sorted({
        sum(
            (1 << index)
            for index, group in enumerate(groups)
            if any(alt["resource_id"] == resource for alt in group["alternatives"])
        )
        for resource in resources
    }))

    @lru_cache(maxsize=None)
    def ideal_from(rank: int, covered_mask: int) -> float:
        if rank > k or covered_mask.bit_count() == len(groups):
            return 0.0
        return max(
            (
                (mask & ~covered_mask).bit_count() / math.log2(rank + 1)
                + ideal_from(rank + 1, covered_mask | mask)
                for mask in coverage_masks
                if mask & ~covered_mask
            ),
            default=0.0,
        )

    ideal = ideal_from(1, 0)
    suffix = f"at_{k}"
    return {
        f"resource_hit_{suffix}": float(any(group_hits)),
        f"resource_recall_{suffix}": sum(group_hits) / len(groups),
        f"complete_evidence_{suffix}": float(all(group_hits)),
        f"exact_locator_group_recall_{suffix}": sum(locator_hits) / len(groups),
        f"complete_locator_{suffix}": float(all(locator_hits)),
        "mrr": 0.0 if first_rank is None else 1.0 / first_rank,
        f"ndcg_{suffix}": dcg / ideal,
    }


def score_refusal(*, label_status: str, refused: bool) -> dict[str, float]:
    """Score verified absence and known answerability in separate metric buckets."""
    if label_status == "verified_absent":
        return {"correct_refusal": float(refused)}
    if label_status == "verified_answerable":
        return {"false_refusal": float(refused)}
    raise ValueError("refusal scoring requires verified absence or answerability")


def summarize_paired(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Aggregate Chinese and English metrics by independent intent."""
    if not rows:
        raise ValueError("paired summary requires rows")
    pairs: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for row in rows:
        intent = row["intent_id"]
        language = row["language"]
        if language in pairs[intent]:
            raise ValueError(f"duplicate paired variant: {intent}/{language}")
        pairs[intent][language] = row["metrics"]
    if any(set(languages) != {"en", "zh"} for languages in pairs.values()):
        raise ValueError("paired summary requires en and zh for every intent")
    names = set(next(iter(pairs.values()))["en"])
    if any(set(metrics) != names for languages in pairs.values() for metrics in languages.values()):
        raise ValueError("paired variants have different metric names")
    count = len(pairs)
    return {
        "en": {name: sum(pair["en"][name] for pair in pairs.values()) / count for name in names},
        "zh": {name: sum(pair["zh"][name] for pair in pairs.values()) / count for name in names},
        "zh_minus_en": {
            name: sum(pair["zh"][name] - pair["en"][name] for pair in pairs.values()) / count
            for name in names
        },
    }
