import json
import math
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ped_agent_server.catalog import Catalog
from ped_agent_server.cli import app
from ped_agent_server.evaluation import (
    EvaluationAcceptanceConfig,
    EvaluationReport,
    GoldQuestion,
    audit_catalog,
    audit_evaluation,
    evaluate_rankings,
    load_gold,
)
from ped_agent_server.models import CanonicalChunk, ResourceManifest, ResourceType
from tests.manifest_samples import literature_manifest


def test_evaluation_computes_recall_mrr_and_locator_hit() -> None:
    questions = [
        GoldQuestion(
            question_id="q1",
            query="出口拥堵",
            expected_resource_ids=["reg-1"],
            expected_locators=["第5.2条"],
        ),
        GoldQuestion(
            question_id="q2",
            query="bottleneck flow",
            expected_resource_ids=["paper-1"],
            expected_locators=["p.4"],
        ),
    ]
    rankings = {
        "q1": [("reg-x", "第1条"), ("reg-1", "第5.2条")],
        "q2": [("paper-1", "p.4")],
    }

    report = evaluate_rankings(questions, rankings, k=5)

    assert report.recall_at_k == 1.0
    assert report.mrr == 0.75
    assert report.locator_hit_rate == 1.0
    assert report.ndcg_at_k == pytest.approx((1 / math.log2(3) + 1.0) / 2)


def test_evaluation_rejects_empty_questions_and_invalid_k() -> None:
    with pytest.raises(ValueError, match="at least one"):
        evaluate_rankings([], {}, k=5)
    with pytest.raises(ValueError, match="positive"):
        evaluate_rankings(
            [GoldQuestion(question_id="q1", query="density", expected_resource_ids=["p1"])],
            {},
            k=0,
        )


def test_load_gold_reads_jsonl_records(tmp_path: Path) -> None:
    path = tmp_path / "gold.jsonl"
    path.write_text(
        json.dumps(
            {
                "question_id": "q1",
                "query": "density",
                "expected_resource_ids": ["paper-1"],
                "expected_locators": ["p.3"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    questions = load_gold(path)

    assert questions[0].question_id == "q1"
    assert questions[0].expected_locators == ["p.3"]


def test_audit_catalog_reports_official_coverage_without_duplicates(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    official = literature_manifest(
        resource_id="paper-official-2026",
        title="Official paper",
        source_path=tmp_path / "official.pdf",
        sha256="b" * 64,
        doi="10.1000/official",
    )
    candidate = ResourceManifest(
        resource_id="paper-candidate-2026",
        resource_type=ResourceType.LITERATURE,
        title="Candidate paper",
        language="en",
        source_path=tmp_path / "candidate.pdf",
        sha256="a" * 64,
        doi="10.1000/candidate",
        include=False,
    )
    catalog.upsert_resource(official, version_id=official.sha256, vault_path="objects/aa/a.pdf")
    catalog.replace_chunks(
        official.sha256,
        [
            CanonicalChunk(
                chunk_id="paper-official-2026:a:00000",
                resource_id=official.resource_id,
                version_id=official.sha256,
                ordinal=0,
                text="Official evidence.",
                page_start=2,
                page_end=2,
                locator="p.2",
                parser_version="pedestrian-pdf-v1",
            )
        ],
    )
    catalog.upsert_resource(candidate, version_id=candidate.sha256, vault_path="objects/bb/b.pdf")

    report = audit_catalog(catalog)

    assert report.resource_count == 2
    assert report.official_resource_count == 1
    assert report.official_chunk_count == 1
    assert report.locator_coverage == 1.0
    assert report.duplicate_sha256_count == 0


def test_cli_lists_evaluation_and_audit_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "evaluate" in result.stdout
    assert "audit" in result.stdout


def test_library_cli_exposes_technical_preflight() -> None:
    result = CliRunner().invoke(app, ["library", "--help"])

    assert result.exit_code == 0
    assert "preflight" in result.stdout


def test_evaluate_cli_exposes_acceptance_config_option() -> None:
    result = CliRunner().invoke(app, ["evaluate", "--help"])

    assert result.exit_code == 0
    assert "--config" in result.stdout


def test_evaluation_acceptance_gate_reports_every_failed_threshold() -> None:
    config = EvaluationAcceptanceConfig(
        question_count=30,
        k=5,
        minimum_recall_at_k=0.8,
        minimum_mrr=0.7,
        minimum_locator_hit_rate=0.75,
        maximum_non_official_leakage=0.0,
    )
    report = EvaluationReport(
        question_count=29,
        k=5,
        recall_at_k=0.79,
        mrr=0.69,
        ndcg_at_k=0.8,
        locator_hit_rate=0.74,
    )

    acceptance = audit_evaluation(
        report,
        config,
        non_official_leakage=0.01,
    )

    assert acceptance.is_compliant is False
    assert acceptance.errors == (
        "Gold Question count must equal 30",
        "Recall@5 is below 0.8",
        "MRR is below 0.7",
        "locator hit rate is below 0.75",
        "non-official leakage exceeds 0.0",
    )
