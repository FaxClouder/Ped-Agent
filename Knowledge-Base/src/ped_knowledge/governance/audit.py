from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime

from ped_knowledge.governance.contracts import (
    FORMAL_PUBLICATION_STATUSES,
    QualityTier,
    ResourceManifest,
)
from ped_knowledge.governance.manifest import age_in_months, is_high_impact


@dataclass(frozen=True)
class CorpusRequirements:
    resource_count: int
    minimum_a_tier: int
    minimum_a_b_tiers: int
    maximum_x_tier: int
    minimum_high_impact: int
    maximum_recent_excellence: int
    maximum_up_to_18_months: int
    topic_quotas: dict[str, int]
    maximum_through_2015: int | None = None
    minimum_2022_onward: int | None = None
    minimum_chinese_language: int | None = None
    maximum_chinese_language: int | None = None


@dataclass(frozen=True)
class CorpusAuditReport:
    phase: str
    resource_count: int
    tier_counts: dict[str, int]
    topic_counts: dict[str, int]
    high_impact_count: int
    recent_excellence_count: int
    up_to_18_months_count: int
    formal_publication_count: int
    year_band_counts: dict[str, int]
    chinese_language_count: int
    errors: tuple[str, ...]

    @property
    def is_compliant(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class RegulationCorpusAuditReport:
    phase: str
    resource_count: int
    topic_counts: dict[str, int]
    current_official_count: int
    errors: tuple[str, ...]

    @property
    def is_compliant(self) -> bool:
        return not self.errors


PILOT_REQUIREMENTS = CorpusRequirements(
    resource_count=20,
    minimum_a_tier=8,
    minimum_a_b_tiers=18,
    maximum_x_tier=2,
    minimum_high_impact=14,
    maximum_recent_excellence=4,
    maximum_up_to_18_months=2,
    topic_quotas={
        "flow_fundamentals": 4,
        "experiment_measurement": 4,
        "facility_scenario_flow": 4,
        "evacuation_behavior_modeling": 5,
        "safety_risk_intervention": 3,
    },
)

CORE_REQUIREMENTS = CorpusRequirements(
    resource_count=120,
    minimum_a_tier=48,
    minimum_a_b_tiers=108,
    maximum_x_tier=12,
    minimum_high_impact=84,
    maximum_recent_excellence=24,
    maximum_up_to_18_months=12,
    topic_quotas={
        "flow_fundamentals": 24,
        "experiment_measurement": 24,
        "facility_scenario_flow": 24,
        "evacuation_behavior_modeling": 30,
        "safety_risk_intervention": 18,
    },
    maximum_through_2015=24,
    minimum_2022_onward=54,
    minimum_chinese_language=12,
    maximum_chinese_language=24,
)

PHASE_REQUIREMENTS = {
    "pilot": PILOT_REQUIREMENTS,
    "core": CORE_REQUIREMENTS,
}

REGULATION_PHASE_REQUIREMENTS = {
    "pilot": (
        8,
        {
            "building_fire_evacuation": 3,
            "transport_public_space": 2,
            "emergency_large_events": 1,
            "accessibility_pedestrian_facilities": 1,
            "international_comparison": 1,
        },
    ),
    "core": (
        40,
        {
            "building_fire_evacuation": 14,
            "transport_public_space": 10,
            "emergency_large_events": 6,
            "accessibility_pedestrian_facilities": 6,
            "international_comparison": 4,
        },
    ),
}


def audit_literature_corpus(
    records: list[ResourceManifest],
    *,
    phase: str,
    as_of: date | None = None,
) -> CorpusAuditReport:
    try:
        requirements = PHASE_REQUIREMENTS[phase]
    except KeyError as exc:
        raise ValueError(f"unknown literature corpus phase: {phase}") from exc
    reference_date = as_of or datetime.now(UTC).date()
    tier_counts = Counter(
        record.quality_tier.value
        for record in records
        if record.quality_tier is not None
    )
    topic_counts = Counter(
        record.primary_topic
        for record in records
        if record.primary_topic is not None
    )
    high_impact_count = sum(
        is_high_impact(record, as_of=reference_date) for record in records
    )
    recent_excellence_count = sum(
        _is_recent_excellence(record, as_of=reference_date) for record in records
    )
    up_to_18_months_count = sum(
        _is_up_to_18_months(record, as_of=reference_date) for record in records
    )
    formal_publication_count = sum(
        record.publication_status in FORMAL_PUBLICATION_STATUSES for record in records
    )
    year_band_counts = _year_band_counts(records)
    chinese_language_count = sum(record.language.lower().startswith("zh") for record in records)
    errors = _corpus_errors(
        requirements,
        resource_count=len(records),
        tier_counts=tier_counts,
        topic_counts=topic_counts,
        high_impact_count=high_impact_count,
        recent_excellence_count=recent_excellence_count,
        up_to_18_months_count=up_to_18_months_count,
        formal_publication_count=formal_publication_count,
        year_band_counts=year_band_counts,
        chinese_language_count=chinese_language_count,
    )
    return CorpusAuditReport(
        phase=phase,
        resource_count=len(records),
        tier_counts=dict(tier_counts),
        topic_counts=dict(topic_counts),
        high_impact_count=high_impact_count,
        recent_excellence_count=recent_excellence_count,
        up_to_18_months_count=up_to_18_months_count,
        formal_publication_count=formal_publication_count,
        year_band_counts=year_band_counts,
        chinese_language_count=chinese_language_count,
        errors=tuple(errors),
    )


def audit_regulation_corpus(
    records: list[ResourceManifest],
    *,
    phase: str,
) -> RegulationCorpusAuditReport:
    try:
        expected_count, topic_quotas = REGULATION_PHASE_REQUIREMENTS[phase]
    except KeyError as exc:
        raise ValueError(f"unknown regulation corpus phase: {phase}") from exc
    topic_counts = Counter(
        record.primary_topic
        for record in records
        if record.primary_topic is not None
    )
    current_official_count = sum(
        record.include and record.effective_status == "current" for record in records
    )
    errors: list[str] = []
    if len(records) != expected_count:
        errors.append(f"regulation count must equal {expected_count}")
    if current_official_count != len(records):
        errors.append("all quota-counted regulations must be current and official")
    for topic, expected in topic_quotas.items():
        if topic_counts[topic] != expected:
            errors.append(f"topic {topic} must equal {expected}")
    return RegulationCorpusAuditReport(
        phase=phase,
        resource_count=len(records),
        topic_counts=dict(topic_counts),
        current_official_count=current_official_count,
        errors=tuple(errors),
    )


def _is_recent_excellence(record: ResourceManifest, *, as_of: date) -> bool:
    age_months = age_in_months(record.published_date, as_of)
    return (
        record.quality_tier is QualityTier.B
        and age_months is not None
        and 18 < age_months <= 36
        and not is_high_impact(record, as_of=as_of)
    )


def _is_up_to_18_months(record: ResourceManifest, *, as_of: date) -> bool:
    age_months = age_in_months(record.published_date, as_of)
    return age_months is not None and age_months <= 18


def _year_band_counts(records: list[ResourceManifest]) -> dict[str, int]:
    counts = {
        "through_2015": 0,
        "2016_2021": 0,
        "2022_onward": 0,
    }
    for record in records:
        if record.published_date is None:
            continue
        if record.published_date.year <= 2015:
            counts["through_2015"] += 1
        elif record.published_date.year <= 2021:
            counts["2016_2021"] += 1
        else:
            counts["2022_onward"] += 1
    return counts


def _corpus_errors(
    requirements: CorpusRequirements,
    *,
    resource_count: int,
    tier_counts: Counter[str],
    topic_counts: Counter[str],
    high_impact_count: int,
    recent_excellence_count: int,
    up_to_18_months_count: int,
    formal_publication_count: int,
    year_band_counts: dict[str, int],
    chinese_language_count: int,
) -> list[str]:
    errors: list[str] = []
    if resource_count != requirements.resource_count:
        errors.append(f"literature count must equal {requirements.resource_count}")
    a_tier = tier_counts[QualityTier.A.value]
    a_b_tiers = a_tier + tier_counts[QualityTier.B.value]
    x_tier = tier_counts[QualityTier.EXCEPTION.value]
    if a_tier < requirements.minimum_a_tier:
        errors.append(f"A-tier literature is below {requirements.minimum_a_tier}")
    if a_b_tiers < requirements.minimum_a_b_tiers:
        errors.append(f"A/B-tier literature is below {requirements.minimum_a_b_tiers}")
    if x_tier > requirements.maximum_x_tier:
        errors.append(f"X-tier literature exceeds {requirements.maximum_x_tier}")
    if high_impact_count < requirements.minimum_high_impact:
        errors.append(f"high-impact literature is below {requirements.minimum_high_impact}")
    if recent_excellence_count > requirements.maximum_recent_excellence:
        errors.append(
            f"recent-excellence literature exceeds {requirements.maximum_recent_excellence}"
        )
    if up_to_18_months_count > requirements.maximum_up_to_18_months:
        errors.append(
            "literature up to 18 months old exceeds "
            f"{requirements.maximum_up_to_18_months}"
        )
    if formal_publication_count != resource_count:
        errors.append("all official literature must use a formal publication version")
    if (
        requirements.maximum_through_2015 is not None
        and year_band_counts["through_2015"] > requirements.maximum_through_2015
    ):
        errors.append(
            f"literature published through 2015 exceeds {requirements.maximum_through_2015}"
        )
    if (
        requirements.minimum_2022_onward is not None
        and year_band_counts["2022_onward"] < requirements.minimum_2022_onward
    ):
        errors.append(
            "literature published from 2022 onward is below "
            f"{requirements.minimum_2022_onward}"
        )
    if (
        requirements.minimum_chinese_language is not None
        and requirements.maximum_chinese_language is not None
        and not (
            requirements.minimum_chinese_language
            <= chinese_language_count
            <= requirements.maximum_chinese_language
        )
    ):
        errors.append(
            "Chinese-language literature must be between "
            f"{requirements.minimum_chinese_language} and "
            f"{requirements.maximum_chinese_language}"
        )
    for topic, expected in requirements.topic_quotas.items():
        if topic_counts[topic] != expected:
            errors.append(f"topic {topic} must equal {expected}")
    return errors
