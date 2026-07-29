from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"


EXPECTED_CSV_HEADERS = {
    "sources/literature/search_log.csv": [
        "search_id",
        "searched_at",
        "database",
        "topic",
        "query",
        "date_start",
        "date_end",
        "result_count",
        "operator",
        "notes",
    ],
    "sources/literature/candidates.csv": [
        "candidate_id",
        "resource_id",
        "doi",
        "title",
        "authors",
        "year",
        "venue",
        "language",
        "primary_topic",
        "topics",
        "discovery_source",
        "source_url",
        "publication_status",
        "screening_status",
        "notes",
    ],
    "sources/literature/journal_metrics.csv": [
        "venue",
        "issn",
        "jci_value",
        "jci_quartile",
        "jci_year",
        "jci_source",
        "cas_zone",
        "cas_category",
        "cas_year",
        "cas_source",
        "verified_at",
        "verified_by",
    ],
    "sources/literature/citation_snapshots.csv": [
        "resource_id",
        "doi",
        "citation_count",
        "citation_source",
        "citation_checked_at",
        "meets_age_threshold",
        "notes",
    ],
    "sources/literature/exclusions.csv": [
        "resource_id",
        "doi",
        "screening_stage",
        "reason_code",
        "reason_detail",
        "decided_at",
        "decided_by",
    ],
    "sources/regulations/source_checks.csv": [
        "resource_id",
        "document_number",
        "title",
        "issuing_body",
        "jurisdiction",
        "source_url",
        "effective_status",
        "published_date",
        "effective_date",
        "accessed_date",
        "verified_by",
    ],
    "sources/regulations/version_history.csv": [
        "resource_id",
        "document_number",
        "version_id",
        "supersedes_resource_id",
        "superseded_by_resource_id",
        "effective_date",
        "withdrawn_date",
        "status",
        "notes",
    ],
    "sources/regulations/exclusions.csv": [
        "resource_id",
        "document_number",
        "screening_stage",
        "reason_code",
        "reason_detail",
        "decided_at",
        "decided_by",
    ],
    "screening/literature_screening.csv": [
        "resource_id",
        "doi",
        "title_screen",
        "abstract_screen",
        "fulltext_screen",
        "relevance_score",
        "method_score",
        "rag_evidence_score",
        "coverage_score",
        "traceability_score",
        "total_score",
        "quality_tier",
        "decision",
        "reviewed_at",
        "reviewed_by",
    ],
    "screening/literature_exceptions.csv": [
        "resource_id",
        "doi",
        "failed_rule",
        "exception_reason",
        "irreplaceability_evidence",
        "approved_by",
        "approved_at",
        "decision",
    ],
    "screening/regulation_screening.csv": [
        "resource_id",
        "document_number",
        "official_source_verified",
        "identity_verified",
        "current_status_verified",
        "fulltext_verified",
        "hash_verified",
        "topic",
        "decision",
        "reviewed_at",
        "reviewed_by",
    ],
}


def test_research_policies_and_empty_manifests_exist() -> None:
    expected = [
        "README.md",
        "policies/collection_standard.md",
        "policies/taxonomy.yaml",
        "policies/quotas.yaml",
        "policies/literature_quality_rules.yaml",
        "manifests/README.md",
        "manifests/literature/pilot.jsonl",
        "manifests/literature/core.jsonl",
        "manifests/regulations/pilot.jsonl",
        "manifests/regulations/core.jsonl",
        "experiments/README.md",
        "experiments/pilot_config.json",
        "experiments/core_config.json",
        "experiments/pilot_gold.jsonl",
        "experiments/core_gold.jsonl",
    ]

    for relative_path in expected:
        assert (RESEARCH / relative_path).is_file(), relative_path
    for relative_path in expected[6:10]:
        assert not (RESEARCH / relative_path).read_text(encoding="utf-8").strip()
    for relative_path in expected[-2:]:
        assert not (RESEARCH / relative_path).read_text(encoding="utf-8").strip()


def test_research_csv_templates_have_stable_headers() -> None:
    for relative_path, expected_header in EXPECTED_CSV_HEADERS.items():
        with (RESEARCH / relative_path).open(encoding="utf-8-sig", newline="") as handle:
            actual_header = next(csv.reader(handle))
        assert actual_header == expected_header, relative_path


def test_quality_policy_contains_machine_enforced_thresholds() -> None:
    quality_rules = (RESEARCH / "policies/literature_quality_rules.yaml").read_text(
        encoding="utf-8"
    )
    quotas = (RESEARCH / "policies/quotas.yaml").read_text(encoding="utf-8")

    assert "minimum_jci: 1.0" in quality_rules
    assert "maximum_cas_zone: 2" in quality_rules
    assert "maximum_exception_ratio: 0.10" in quality_rules
    assert "minimum_high_impact_ratio: 0.70" in quality_rules
    assert "maximum_up_to_18_months_ratio: 0.10" in quality_rules
    assert "minimum: 60" in quotas
    assert "maximum: 400" in quotas
    assert "import_batch_size: 5" in quotas
    assert "import_batch_size: 2" in quotas
    assert "flow_fundamentals: 24" in quotas
    assert "evacuation_behavior_modeling: 30" in quotas


def test_retrieval_evaluation_configs_preserve_acceptance_thresholds() -> None:
    pilot = json.loads(
        (RESEARCH / "experiments/pilot_config.json").read_text(encoding="utf-8")
    )
    core = json.loads(
        (RESEARCH / "experiments/core_config.json").read_text(encoding="utf-8")
    )

    assert pilot == {
        "question_count": 30,
        "k": 5,
        "minimum_recall_at_k": 0.8,
        "minimum_mrr": 0.7,
        "minimum_locator_hit_rate": 0.75,
        "maximum_non_official_leakage": 0.0,
    }
    assert core["question_count"] == 100
    assert core["minimum_recall_at_k"] == 0.8
    assert core["maximum_non_official_leakage"] == 0.0
