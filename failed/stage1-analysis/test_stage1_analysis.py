"""Regression checks for the offline Stage 1 re-analysis."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location(
    "stage1_analysis", Path(__file__).with_name("analyze_stage1.py")
)
assert SPEC and SPEC.loader
stage1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage1)
DASHBOARD_SPEC = importlib.util.spec_from_file_location(
    "stage1_dashboard", Path(__file__).with_name("generate_dashboard.py")
)
assert DASHBOARD_SPEC and DASHBOARD_SPEC.loader
dashboard = importlib.util.module_from_spec(DASHBOARD_SPEC)
DASHBOARD_SPEC.loader.exec_module(dashboard)


def test_resource_recall_uses_distinct_resources_and_and_or_groups() -> None:
    ranking = [
        {"resource_id": "wrong"},
        {"resource_id": "wrong"},
        {"resource_id": "source-a"},
        {"resource_id": "source-b"},
    ]
    evidence = {"evidence_groups": [
        {"alternatives": [{"resource_id": "source-a"}, {"resource_id": "other"}]},
        {"alternatives": [{"resource_id": "source-b"}]},
    ]}
    assert stage1.resource_recall_at_k(ranking, evidence, k=2) == 0.5
    assert stage1.resource_recall_at_k(ranking, evidence, k=3) == 1.0


def test_report_does_not_assert_an_optimal_k(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stage1, "OUTPUT_DIR", tmp_path)
    stage1.generate_markdown_report(
        stage1.analyze_retriever_ablation(stage1.load_summary()),
        stage1.analyze_top_k_sensitivity(stage1.load_per_query(), stage1.load_evidence()),
        stage1.analyze_difficulty_stratification(stage1.load_per_query(), stage1.load_questions()),
        stage1.analyze_topic_performance(stage1.load_per_query(), stage1.load_questions()),
        stage1.load_summary(),
    )
    report = (tmp_path / "stage1_analysis_report.md").read_text(encoding="utf-8")
    assert "k=5 optimal" not in report
    assert "Best Performer" not in report
    assert "difficulty_stratification.csv" not in report
    assert "Analysis Date: 2026-09-25" not in report
    assert "20 Chinese queries" in report
    assert "1 additional English query" in report


def test_output_directory_must_be_new(tmp_path: Path) -> None:
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        stage1.prepare_output_dir(existing)


def test_dashboard_refuses_to_replace_image(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dashboard, "REPORT_DIR", tmp_path)
    image = tmp_path / "stage1_dashboard.png"
    image.write_bytes(b"original image")
    with pytest.raises(FileExistsError):
        dashboard.make_dashboard()
    assert image.read_bytes() == b"original image"
