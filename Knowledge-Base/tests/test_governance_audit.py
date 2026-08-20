from datetime import date
from pathlib import Path

from ped_knowledge.governance.audit import audit_literature_corpus, audit_regulation_corpus
from ped_knowledge.governance.contracts import ResourceManifest, ResourceType

PILOT_TOPICS = {
    "flow_fundamentals": 4,
    "experiment_measurement": 4,
    "facility_scenario_flow": 4,
    "evacuation_behavior_modeling": 5,
    "safety_risk_intervention": 3,
}

PILOT_REGULATION_TOPICS = {
    "building_fire_evacuation": 3,
    "transport_public_space": 2,
    "emergency_large_events": 1,
    "accessibility_pedestrian_facilities": 1,
    "international_comparison": 1,
}


def literature(
    index: int,
    *,
    topic: str,
    tier: str,
    published_date: str = "2016-01-01",
    language: str = "en",
) -> ResourceManifest:
    cas_zone = 1 if tier == "A" else 2
    jci_value = 1.8 if tier == "A" else 1.2
    overrides: dict[str, object] = {}
    if tier == "X":
        cas_zone = 3
        jci_value = 0.8
        overrides = {
            "exception_reason": "Irreplaceable foundational evidence",
            "approved_by": "literature-review-board",
        }
    return ResourceManifest(
        resource_id=f"lit-2016-quality-{index:03d}",
        resource_type=ResourceType.LITERATURE,
        title=f"Quality literature {index}",
        language=language,
        source_path=Path(f"paper-{index}.pdf"),
        sha256=f"{index:064x}",
        doi=f"10.1000/quality-{index}",
        authors=["Demo Author"],
        venue="Safety Science",
        published_date=published_date,
        publication_status="version_of_record",
        integrity_status="clear",
        citation_count=600,
        citation_source="web_of_science",
        citation_checked_at="2026-07-01",
        jci_value=jci_value,
        jci_quartile="Q1" if tier == "A" else "Q2",
        jci_year=2025,
        jci_source="clarivate_jcr",
        cas_zone=cas_zone,
        cas_category="Engineering",
        cas_year=2025,
        cas_source="cas_journal_partition",
        metrics_checked_at="2026-07-01",
        quality_tier=tier,
        content_quality_score=90,
        primary_topic=topic,
        topics=[topic],
        include=True,
        **overrides,
    )


def pilot_records() -> list[ResourceManifest]:
    tiers = ["A"] * 8 + ["B"] * 10 + ["X"] * 2
    topics = [topic for topic, count in PILOT_TOPICS.items() for _ in range(count)]
    return [
        literature(index, topic=topic, tier=tier)
        for index, (topic, tier) in enumerate(zip(topics, tiers, strict=True), start=1)
    ]


def regulation(index: int, *, topic: str) -> ResourceManifest:
    return ResourceManifest(
        resource_id=f"reg-cn-quality-{index:03d}",
        resource_type=ResourceType.REGULATION,
        title=f"Official regulation {index}",
        language="zh-CN",
        source_path=Path(f"regulation-{index}.pdf"),
        sha256=f"{index + 1000:064x}",
        source_url=f"https://example.org/regulation/{index}",
        document_number=f"GB-DEMO-{index:03d}",
        jurisdiction="CN",
        issuing_body="Demo authority",
        effective_status="current",
        published_date="2026-01-01",
        effective_date="2026-07-01",
        legal_level="national_standard",
        accessed_date="2026-07-29",
        source_verified_by="regulation-reviewer",
        primary_topic=topic,
        topics=[topic],
        include=True,
    )


def pilot_regulations() -> list[ResourceManifest]:
    topics = [
        topic
        for topic, count in PILOT_REGULATION_TOPICS.items()
        for _ in range(count)
    ]
    return [regulation(index, topic=topic) for index, topic in enumerate(topics, start=1)]


def core_records() -> list[ResourceManifest]:
    topic_quotas = {
        "flow_fundamentals": 24,
        "experiment_measurement": 24,
        "facility_scenario_flow": 24,
        "evacuation_behavior_modeling": 30,
        "safety_risk_intervention": 18,
    }
    topics = [topic for topic, count in topic_quotas.items() for _ in range(count)]
    tiers = ["A"] * 48 + ["B"] * 60 + ["X"] * 12
    years = ["2010-01-01"] * 24 + ["2018-01-01"] * 42 + ["2024-01-01"] * 54
    languages = ["zh-CN"] * 18 + ["en"] * 102
    return [
        literature(
            index,
            topic=topic,
            tier=tier,
            published_date=published_date,
            language=language,
        )
        for index, (topic, tier, published_date, language) in enumerate(
            zip(topics, tiers, years, languages, strict=True),
            start=1,
        )
    ]


def test_pilot_corpus_passes_all_quality_and_topic_quotas() -> None:
    report = audit_literature_corpus(
        pilot_records(),
        phase="pilot",
        as_of=date(2026, 7, 29),
    )

    assert report.is_compliant is True
    assert report.resource_count == 20
    assert report.tier_counts == {"A": 8, "B": 10, "X": 2}
    assert report.topic_counts == PILOT_TOPICS


def test_pilot_corpus_reports_excess_exception_ratio() -> None:
    records = pilot_records()
    records[7] = literature(
        8,
        topic=records[7].primary_topic,
        tier="X",
    )

    report = audit_literature_corpus(
        records,
        phase="pilot",
        as_of=date(2026, 7, 29),
    )

    assert report.is_compliant is False
    assert "X-tier literature exceeds 2" in report.errors
    assert "A-tier literature is below 8" in report.errors


def test_pilot_corpus_limits_literature_published_within_18_months() -> None:
    records = pilot_records()
    for index in range(3):
        records[index] = literature(
            index + 1,
            topic=records[index].primary_topic,
            tier="A",
            published_date="2026-01-01",
        )

    report = audit_literature_corpus(
        records,
        phase="pilot",
        as_of=date(2026, 7, 29),
    )

    assert report.is_compliant is False
    assert report.up_to_18_months_count == 3
    assert "literature up to 18 months old exceeds 2" in report.errors


def test_core_corpus_enforces_year_and_language_structure() -> None:
    report = audit_literature_corpus(
        core_records(),
        phase="core",
        as_of=date(2026, 7, 29),
    )

    assert report.is_compliant is True
    assert report.year_band_counts == {
        "through_2015": 24,
        "2016_2021": 42,
        "2022_onward": 54,
    }
    assert report.chinese_language_count == 18


def test_core_corpus_reports_year_and_language_violations() -> None:
    records = core_records()
    records[24] = literature(
        25,
        topic=records[24].primary_topic,
        tier=records[24].quality_tier.value,
        published_date="2010-01-01",
        language="en",
    )
    records[66] = literature(
        67,
        topic=records[66].primary_topic,
        tier=records[66].quality_tier.value,
        published_date="2018-01-01",
        language=records[66].language,
    )
    for index in range(11, 18):
        records[index].language = "en"

    report = audit_literature_corpus(
        records,
        phase="core",
        as_of=date(2026, 7, 29),
    )

    assert report.is_compliant is False
    assert "literature published through 2015 exceeds 24" in report.errors
    assert "literature published from 2022 onward is below 54" in report.errors
    assert "Chinese-language literature must be between 12 and 24" in report.errors


def test_pilot_regulations_pass_count_and_topic_quotas() -> None:
    report = audit_regulation_corpus(pilot_regulations(), phase="pilot")

    assert report.is_compliant is True
    assert report.resource_count == 8
    assert report.topic_counts == PILOT_REGULATION_TOPICS


def test_pilot_regulations_report_topic_imbalance() -> None:
    records = pilot_regulations()
    records[-1] = regulation(8, topic="building_fire_evacuation")

    report = audit_regulation_corpus(records, phase="pilot")

    assert report.is_compliant is False
    assert "topic international_comparison must equal 1" in report.errors
