from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import fitz
import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from ped_agent_server.cli import app
from ped_agent_server.paths import WorkspacePaths
from ped_agent_server.research_governance import (
    GovernanceValidationError,
    PrismaCounts,
    ResearchGovernanceService,
)
from ped_agent_server.research_governance.service import (
    CSV_TEMPLATES,
    GLOBAL_ARTIFACTS,
    REVIEW_DIRECTORIES,
)

REVIEW_ID = "ped-flow-pilot-2026"


def write_pdf(path: Path) -> str:
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "Pedestrian flow evidence for PRISMA release testing.")
        document.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv_row(path: Path, values: dict[str, str] | None = None) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle))
    defaults = {
        "review_id": REVIEW_ID,
        "search_id": "search-1",
        "record_id": "record-1",
        "canonical_record_id": "canonical-1",
        "report_id": "report-1",
        "study_id": "study-1",
        "resource_id": "paper-prisma-2026",
        "decision_id": "decision-1",
        "decision": "include",
        "status": "retrieved",
    }
    defaults.update(values or {})
    row = [defaults.get(column, "value") for column in header]
    with path.open("a", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(row)


def prepare_global_artifacts(paths: WorkspacePaths) -> None:
    headers = {
        "search_log.csv": ("search_id", "query"),
        "candidates.csv": ("resource_id", "title"),
        "exclusions.csv": ("resource_id", "reason_code"),
        "journal_metrics.csv": ("resource_id", "jci_value"),
        "citation_snapshots.csv": ("resource_id", "citation_count"),
        "screening.csv": ("resource_id", "decision"),
        "exceptions.csv": ("resource_id", "decision"),
    }
    paths.literature_records_dir.mkdir(parents=True, exist_ok=True)
    for relative_path in GLOBAL_ARTIFACTS:
        path = paths.knowledge_root / relative_path
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(headers[path.name])
        if path.name not in {"exclusions.csv", "exceptions.csv"}:
            write_csv_row(path)


def prepare_freezable_review(tmp_path: Path) -> tuple[WorkspacePaths, ResearchGovernanceService]:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    prepare_global_artifacts(paths)
    service = ResearchGovernanceService(paths)
    review_root = service.initialize_review(REVIEW_ID)

    protocol = review_root / "00-protocol/protocol.md"
    protocol.write_text(protocol.read_text(encoding="utf-8").replace("draft", "approved"), encoding="utf-8")
    for name in ("eligibility_criteria.yaml", "search_strategy.yaml"):
        path = review_root / "00-protocol" / name
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        payload["status"] = "approved"
        if name == "eligibility_criteria.yaml":
            payload["inclusion"] = ["pedestrian-flow evidence"]
            payload["exclusion"] = ["not a research report"]
        else:
            payload["sources"] = ["OpenAlex"]
            payload["queries"] = ["pedestrian flow"]
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    for relative_path in CSV_TEMPLATES:
        if relative_path.endswith(("amendments.csv", "automation_log.csv")):
            continue
        write_csv_row(review_root / relative_path)

    audit_path = review_root / "06-quality/corpus_audit.json"
    audit_path.write_text(
        json.dumps(
            {"review_id": REVIEW_ID, "status": "complete", "is_compliant": True},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    counts = {
        "records_identified": 2,
        "duplicates_removed": 1,
        "records_screened": 1,
        "records_excluded": 0,
        "reports_sought": 1,
        "reports_not_retrieved": 0,
        "reports_assessed": 1,
        "reports_excluded": 0,
        "reports_included": 1,
        "studies_included": 1,
    }
    (review_root / "07-selection-freeze/prisma_counts.json").write_text(
        json.dumps(counts, indent=2) + "\n",
        encoding="utf-8",
    )
    for name in ("prisma_flow.md", "prisma_checklist.md"):
        path = review_root / "07-selection-freeze" / name
        path.write_text(
            path.read_text(encoding="utf-8").replace("draft", "complete"),
            encoding="utf-8",
        )
    return paths, service


def create_literature_manifest(tmp_path: Path, *, resource_id: str = "paper-prisma-2026") -> Path:
    source = tmp_path / f"{resource_id}.pdf"
    digest = write_pdf(source)
    manifest = tmp_path / f"{resource_id}.jsonl"
    manifest.write_text(
        json.dumps(
            {
                "resource_id": resource_id,
                "resource_type": "literature",
                "title": "PRISMA governed pedestrian-flow paper",
                "language": "en",
                "source_path": str(source),
                "sha256": digest,
                "doi": "10.1000/prisma-governed",
                "include": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def test_initialize_review_creates_draft_templates(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    review_root = ResearchGovernanceService(paths).initialize_review(REVIEW_ID)

    assert {path.name for path in review_root.iterdir()} == set(REVIEW_DIRECTORIES)
    assert (review_root / "00-protocol/protocol.md").is_file()
    assert (review_root / "07-selection-freeze/included_studies.csv").is_file()
    assert "status: draft" in (review_root / "00-protocol/protocol.md").read_text()
    assert not (review_root / "07-selection-freeze/selection_freeze.json").exists()
    assert not (review_root / "08-manifest/manifest_release.json").exists()


def test_prisma_counts_rejects_broken_conservation() -> None:
    with pytest.raises(ValidationError, match="records_identified"):
        PrismaCounts(
            records_identified=10,
            duplicates_removed=1,
            records_screened=8,
            records_excluded=3,
            reports_sought=5,
            reports_not_retrieved=1,
            reports_assessed=4,
            reports_excluded=2,
            reports_included=2,
            studies_included=2,
        )


def test_unapproved_protocol_cannot_be_frozen(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    prepare_global_artifacts(paths)
    service = ResearchGovernanceService(paths)
    service.initialize_review(REVIEW_ID)

    with pytest.raises(GovernanceValidationError, match="must be approved"):
        service.create_selection_freeze(REVIEW_ID, approved_by="review-lead")


def test_create_and_verify_selection_freeze(tmp_path: Path) -> None:
    _, service = prepare_freezable_review(tmp_path)

    freeze = service.create_selection_freeze(REVIEW_ID, approved_by="review-lead")
    verified = service.verify_selection_freeze(service.selection_freeze_path(REVIEW_ID))

    assert freeze.review_id == REVIEW_ID
    assert freeze.approved_by == "review-lead"
    assert freeze.included_studies[0].resource_id == "paper-prisma-2026"
    assert verified == freeze


def test_selection_freeze_is_invalid_after_upstream_change(tmp_path: Path) -> None:
    paths, service = prepare_freezable_review(tmp_path)
    service.create_selection_freeze(REVIEW_ID, approved_by="review-lead")
    snapshot = paths.literature_reviews_dir / REVIEW_ID / "01-identification/search_snapshot.csv"
    snapshot.write_text(snapshot.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

    with pytest.raises(GovernanceValidationError, match="frozen artifact changed"):
        service.verify_selection_freeze(service.selection_freeze_path(REVIEW_ID))


def test_manifest_release_rejects_resource_set_mismatch(tmp_path: Path) -> None:
    _, service = prepare_freezable_review(tmp_path)
    service.create_selection_freeze(REVIEW_ID, approved_by="review-lead")
    manifest = create_literature_manifest(tmp_path, resource_id="another-paper-2026")

    with pytest.raises(GovernanceValidationError, match="do not match"):
        service.create_manifest_release(REVIEW_ID, manifest, approved_by="manifest-owner")


def test_create_and_verify_manifest_release(tmp_path: Path) -> None:
    _, service = prepare_freezable_review(tmp_path)
    service.create_selection_freeze(REVIEW_ID, approved_by="review-lead")
    manifest = create_literature_manifest(tmp_path)

    release = service.create_manifest_release(
        REVIEW_ID,
        manifest,
        approved_by="manifest-owner",
    )
    verified = service.verify_manifest_release(
        service.manifest_release_path(REVIEW_ID),
        manifest_path=manifest,
    )

    assert release.resource_ids == ("paper-prisma-2026",)
    assert verified == release


def test_literature_cli_import_requires_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    manifest = create_literature_manifest(tmp_path)
    monkeypatch.setattr("ped_agent_server.cli.repo_paths", lambda: paths)

    result = CliRunner().invoke(app, ["library", "import-manifest", str(manifest)])

    assert result.exit_code == 2
    assert "requires --release" in result.output
    assert not paths.catalog_path.exists()


def test_technical_only_keeps_controlled_import_smoke_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    manifest = create_literature_manifest(tmp_path)
    monkeypatch.setattr("ped_agent_server.cli.repo_paths", lambda: paths)

    result = CliRunner().invoke(
        app,
        ["library", "import-manifest", str(manifest), "--technical-only"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output[result.output.index("{") :])
    assert payload["imported"] == 1
    assert paths.catalog_path.exists()


def test_formal_literature_cli_import_accepts_matching_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths, service = prepare_freezable_review(tmp_path)
    service.create_selection_freeze(REVIEW_ID, approved_by="review-lead")
    manifest = create_literature_manifest(tmp_path)
    release = service.create_manifest_release(
        REVIEW_ID,
        manifest,
        approved_by="manifest-owner",
    )
    monkeypatch.setattr("ped_agent_server.cli.repo_paths", lambda: paths)

    result = CliRunner().invoke(
        app,
        [
            "library",
            "import-manifest",
            str(manifest),
            "--release",
            str(service.manifest_release_path(release.review_id)),
        ],
    )

    assert result.exit_code == 0, result.output
    assert '"imported": 1' in result.output


def test_release_and_technical_only_are_mutually_exclusive(tmp_path: Path) -> None:
    manifest = create_literature_manifest(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "library",
            "import-manifest",
            str(manifest),
            "--release",
            str(tmp_path / "release.json"),
            "--technical-only",
        ],
    )

    assert result.exit_code == 2
    assert "mutually exclusive" in result.output


def test_cli_help_exposes_research_workflow_and_release_options() -> None:
    runner = CliRunner()

    root_help = runner.invoke(app, ["--help"])
    research_help = runner.invoke(app, ["research", "--help"])
    import_help = runner.invoke(app, ["library", "import-manifest", "--help"])

    assert root_help.exit_code == 0
    assert "research" in root_help.output
    assert research_help.exit_code == 0
    assert "freeze-selection" in research_help.output
    assert "release-manifest" in research_help.output
    assert "validate-release" in research_help.output
    assert import_help.exit_code == 0
    assert "--release" in import_help.output
    assert "--technical-only" in import_help.output
