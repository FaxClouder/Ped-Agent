"""Review initialization, selection freezing, and Manifest release validation."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from ped_knowledge.contracts import ResourceType
from ped_knowledge.ingestion import preflight_manifest
from pydantic import ValidationError

from ped_agent_server.paths import WorkspacePaths
from ped_agent_server.research_governance.contracts import (
    ArtifactDigest,
    GovernanceValidationError,
    IncludedStudyRecord,
    ManifestRelease,
    PrismaCounts,
    SelectionFreeze,
)

REVIEW_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]+$")

REVIEW_DIRECTORIES = (
    "00-protocol",
    "01-identification",
    "02-deduplication",
    "03-title-abstract",
    "04-fulltext-retrieval",
    "05-fulltext-eligibility",
    "06-quality",
    "07-selection-freeze",
    "08-manifest",
    "09-ingestion-indexing",
    "10-release",
)

CSV_TEMPLATES: dict[str, tuple[str, ...]] = {
    "00-protocol/amendments.csv": (
        "review_id",
        "amendment_id",
        "changed_at",
        "changed_by",
        "reason",
        "approved_by",
    ),
    "01-identification/search_snapshot.csv": (
        "review_id",
        "search_id",
        "record_id",
        "source_record_id",
        "database",
        "title",
        "doi",
        "identified_at",
    ),
    "02-deduplication/deduplication.csv": (
        "review_id",
        "record_id",
        "canonical_record_id",
        "decision",
        "reason",
        "decided_at",
        "decided_by",
    ),
    "02-deduplication/record_aliases.csv": (
        "review_id",
        "record_id",
        "canonical_record_id",
        "alias_type",
    ),
    "02-deduplication/canonical_records.csv": (
        "review_id",
        "canonical_record_id",
        "title",
        "abstract",
        "doi",
        "authors",
        "year",
    ),
    "03-title-abstract/screening_decisions.csv": (
        "review_id",
        "decision_id",
        "canonical_record_id",
        "stage",
        "decision",
        "reason_code",
        "reason_detail",
        "decided_at",
        "decided_by",
        "reviewer_role",
        "automation_used",
        "tool_name",
        "tool_version",
        "ruleset_or_prompt_hash",
        "supersedes_decision_id",
        "adjudicated_by",
    ),
    "03-title-abstract/screening_consensus.csv": (
        "review_id",
        "canonical_record_id",
        "report_id",
        "decision",
        "reason_code",
        "decided_at",
        "decided_by",
        "adjudicated_by",
    ),
    "03-title-abstract/automation_log.csv": (
        "review_id",
        "event_id",
        "target_id",
        "tool_name",
        "tool_version",
        "ruleset_or_prompt_hash",
        "recommendation",
        "overridden_by",
        "created_at",
    ),
    "04-fulltext-retrieval/fulltext_retrieval.csv": (
        "review_id",
        "report_id",
        "status",
        "reason_code",
        "attempted_at",
        "attempted_by",
    ),
    "04-fulltext-retrieval/fulltext_inventory.csv": (
        "review_id",
        "report_id",
        "resource_id",
        "source_url",
        "source_path",
        "sha256",
        "license_status",
        "retrieved_at",
        "retrieved_by",
    ),
    "05-fulltext-eligibility/screening_decisions.csv": (
        "review_id",
        "decision_id",
        "report_id",
        "stage",
        "decision",
        "reason_code",
        "reason_detail",
        "decided_at",
        "decided_by",
        "reviewer_role",
        "automation_used",
        "tool_name",
        "tool_version",
        "ruleset_or_prompt_hash",
        "supersedes_decision_id",
        "adjudicated_by",
    ),
    "05-fulltext-eligibility/study_report_map.csv": (
        "review_id",
        "study_id",
        "report_id",
        "resource_id",
    ),
    "05-fulltext-eligibility/eligibility_snapshot.csv": (
        "review_id",
        "study_id",
        "report_id",
        "resource_id",
        "decision",
        "decided_at",
        "decided_by",
    ),
    "06-quality/integrity_checks.csv": (
        "review_id",
        "resource_id",
        "integrity_status",
        "source",
        "checked_at",
        "checked_by",
        "notes",
    ),
    "07-selection-freeze/included_studies.csv": (
        "review_id",
        "study_id",
        "report_id",
        "resource_id",
    ),
}

NON_EMPTY_REVIEW_CSVS = frozenset(
    path for path in CSV_TEMPLATES if not path.endswith(("amendments.csv", "automation_log.csv"))
)

GLOBAL_ARTIFACTS = (
    "literature/records/search_log.csv",
    "literature/records/candidates.csv",
    "literature/records/exclusions.csv",
    "literature/records/journal_metrics.csv",
    "literature/records/citation_snapshots.csv",
    "literature/records/screening.csv",
    "literature/records/exceptions.csv",
)

REVIEW_ARTIFACTS = (
    "00-protocol/protocol.md",
    "00-protocol/eligibility_criteria.yaml",
    "00-protocol/search_strategy.yaml",
    *CSV_TEMPLATES,
    "06-quality/corpus_audit.json",
    "07-selection-freeze/prisma_counts.json",
    "07-selection-freeze/prisma_flow.md",
    "07-selection-freeze/prisma_checklist.md",
)


class ResearchGovernanceService:
    def __init__(self, paths: WorkspacePaths) -> None:
        self.paths = paths

    def initialize_review(self, review_id: str) -> Path:
        review_root = self._review_root(review_id)
        if review_root.exists() and any(review_root.iterdir()):
            raise GovernanceValidationError(f"review already exists: {review_id}")
        for directory in REVIEW_DIRECTORIES:
            (review_root / directory).mkdir(parents=True, exist_ok=True)
        self._write_initial_documents(review_root, review_id)
        for relative_path, header in CSV_TEMPLATES.items():
            self._write_csv_template(review_root / relative_path, header)
        return review_root

    def create_selection_freeze(
        self,
        review_id: str,
        *,
        approved_by: str,
    ) -> SelectionFreeze:
        if not approved_by.strip():
            raise GovernanceValidationError("approved_by must not be empty")
        review_root = self._existing_review_root(review_id)
        self._validate_review_ready(review_root, review_id)
        counts = self._load_prisma_counts(review_root)
        included_studies = self._load_included_studies(review_root, review_id)
        self._validate_included_counts(counts, included_studies)
        artifacts = self._build_artifact_digests(review_root)
        freeze = SelectionFreeze(
            review_id=review_id,
            status="approved",
            approved_by=approved_by.strip(),
            created_at=datetime.now(UTC),
            prisma_counts=counts,
            included_studies=included_studies,
            artifacts=artifacts,
        )
        self._write_json(self.selection_freeze_path(review_id), freeze.model_dump(mode="json"))
        return freeze

    def verify_selection_freeze(self, path: Path) -> SelectionFreeze:
        freeze_path = path.resolve()
        try:
            freeze = SelectionFreeze.model_validate_json(freeze_path.read_text(encoding="utf-8"))
        except (OSError, ValidationError) as exc:
            raise GovernanceValidationError(f"invalid selection freeze: {exc}") from exc
        expected_path = self.selection_freeze_path(freeze.review_id).resolve()
        if freeze_path != expected_path:
            raise GovernanceValidationError(
                f"selection freeze must use the governed review path: {expected_path}"
            )
        review_root = self._existing_review_root(freeze.review_id)
        expected_artifacts = {
            self._portable_path(artifact_path) for artifact_path in self._artifact_paths(review_root)
        }
        frozen_artifacts = {artifact.path for artifact in freeze.artifacts}
        if len(frozen_artifacts) != len(freeze.artifacts) or frozen_artifacts != expected_artifacts:
            raise GovernanceValidationError("selection freeze does not bind the complete artifact set")
        for artifact in freeze.artifacts:
            artifact_path = self._resolve_bound_path(artifact.path)
            if not artifact_path.is_file():
                raise GovernanceValidationError(f"frozen artifact is missing: {artifact.path}")
            if self._sha256(artifact_path) != artifact.sha256:
                raise GovernanceValidationError(f"frozen artifact changed: {artifact.path}")
        self._validate_review_ready(review_root, freeze.review_id)
        current_counts = self._load_prisma_counts(review_root)
        current_included = self._load_included_studies(review_root, freeze.review_id)
        self._validate_included_counts(current_counts, current_included)
        if freeze.prisma_counts != current_counts or freeze.included_studies != current_included:
            raise GovernanceValidationError(
                "selection freeze contents do not match the frozen source artifacts"
            )
        return freeze

    def create_manifest_release(
        self,
        review_id: str,
        manifest_path: Path,
        *,
        approved_by: str,
    ) -> ManifestRelease:
        if not approved_by.strip():
            raise GovernanceValidationError("approved_by must not be empty")
        freeze_path = self.selection_freeze_path(review_id)
        freeze = self.verify_selection_freeze(freeze_path)
        records = self._validated_literature_manifest(manifest_path)
        resource_ids = tuple(sorted(record.resource_id for record in records))
        frozen_ids = tuple(sorted(item.resource_id for item in freeze.included_studies))
        if resource_ids != frozen_ids:
            raise GovernanceValidationError(
                "Manifest resource_ids do not match the approved selection freeze"
            )
        release = ManifestRelease(
            review_id=review_id,
            status="approved",
            approved_by=approved_by.strip(),
            created_at=datetime.now(UTC),
            selection_freeze_path=self._portable_path(freeze_path),
            selection_freeze_sha256=self._sha256(freeze_path),
            manifest_path=self._portable_path(manifest_path.resolve()),
            manifest_sha256=self._sha256(manifest_path),
            resource_ids=resource_ids,
        )
        self._write_json(self.manifest_release_path(review_id), release.model_dump(mode="json"))
        return release

    def verify_manifest_release(
        self,
        release_path: Path,
        *,
        manifest_path: Path | None = None,
    ) -> ManifestRelease:
        try:
            release = ManifestRelease.model_validate_json(
                release_path.resolve().read_text(encoding="utf-8")
            )
        except (OSError, ValidationError) as exc:
            raise GovernanceValidationError(f"invalid Manifest release: {exc}") from exc
        expected_path = self.manifest_release_path(release.review_id).resolve()
        if release_path.resolve() != expected_path:
            raise GovernanceValidationError(
                f"Manifest release must use the governed review path: {expected_path}"
            )
        freeze_path = self._resolve_bound_path(release.selection_freeze_path)
        if self._sha256_existing(freeze_path, "selection freeze") != release.selection_freeze_sha256:
            raise GovernanceValidationError("selection freeze hash does not match Manifest release")
        freeze = self.verify_selection_freeze(freeze_path)
        bound_manifest = self._resolve_bound_path(release.manifest_path)
        requested_manifest = manifest_path.resolve() if manifest_path is not None else bound_manifest
        if requested_manifest != bound_manifest:
            raise GovernanceValidationError("requested Manifest is not bound to this release")
        if self._sha256_existing(bound_manifest, "Manifest") != release.manifest_sha256:
            raise GovernanceValidationError("Manifest hash does not match Manifest release")
        records = self._validated_literature_manifest(bound_manifest)
        resource_ids = tuple(sorted(record.resource_id for record in records))
        frozen_ids = tuple(sorted(item.resource_id for item in freeze.included_studies))
        if resource_ids != release.resource_ids or resource_ids != frozen_ids:
            raise GovernanceValidationError("Manifest resource set no longer matches its release")
        return release

    def selection_freeze_path(self, review_id: str) -> Path:
        return self._review_root(review_id) / "07-selection-freeze" / "selection_freeze.json"

    def manifest_release_path(self, review_id: str) -> Path:
        return self._review_root(review_id) / "08-manifest" / "manifest_release.json"

    def _review_root(self, review_id: str) -> Path:
        if not REVIEW_ID_PATTERN.fullmatch(review_id):
            raise GovernanceValidationError(
                "review_id must contain lowercase letters, digits, dots, underscores, or hyphens"
            )
        return self.paths.literature_reviews_dir / review_id

    def _existing_review_root(self, review_id: str) -> Path:
        review_root = self._review_root(review_id)
        if not review_root.is_dir():
            raise GovernanceValidationError(f"review does not exist: {review_id}")
        return review_root

    def _write_initial_documents(self, review_root: Path, review_id: str) -> None:
        documents: dict[str, str] = {
            "00-protocol/protocol.md": (
                f"---\nreview_id: {review_id}\nstatus: draft\n---\n\n"
                "# Review protocol\n\nComplete and approve before identification.\n"
            ),
            "00-protocol/eligibility_criteria.yaml": (
                f"review_id: {review_id}\nstatus: draft\ninclusion: []\nexclusion: []\n"
            ),
            "00-protocol/search_strategy.yaml": (
                f"review_id: {review_id}\nstatus: draft\nsources: []\nqueries: []\n"
            ),
            "06-quality/corpus_audit.json": json.dumps(
                {"review_id": review_id, "status": "draft", "is_compliant": False},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            "07-selection-freeze/prisma_counts.json": json.dumps(
                {
                    "records_identified": 0,
                    "duplicates_removed": 0,
                    "records_screened": 0,
                    "records_excluded": 0,
                    "reports_sought": 0,
                    "reports_not_retrieved": 0,
                    "reports_assessed": 0,
                    "reports_excluded": 0,
                    "reports_included": 0,
                    "studies_included": 0,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            "07-selection-freeze/prisma_flow.md": (
                f"---\nreview_id: {review_id}\nstatus: draft\n---\n\n# PRISMA flow\n"
            ),
            "07-selection-freeze/prisma_checklist.md": (
                f"---\nreview_id: {review_id}\nstatus: draft\n---\n\n# PRISMA checklist\n"
            ),
            "10-release/retrieval_release.md": (
                f"---\nreview_id: {review_id}\nstatus: draft\n---\n\n# Retrieval release\n"
            ),
        }
        for relative_path, content in documents.items():
            path = review_root / relative_path
            path.write_text(content, encoding="utf-8")

    @staticmethod
    def _write_csv_template(path: Path, header: tuple[str, ...]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(header)

    def _validate_review_ready(self, review_root: Path, review_id: str) -> None:
        missing = [path for path in self._artifact_paths(review_root) if not path.is_file()]
        if missing:
            joined = ", ".join(self._portable_path(path) for path in missing)
            raise GovernanceValidationError(f"required review artifacts are missing: {joined}")
        protocol_status = self._markdown_status(review_root / "00-protocol/protocol.md")
        eligibility = self._load_yaml(review_root / "00-protocol/eligibility_criteria.yaml")
        strategy = self._load_yaml(review_root / "00-protocol/search_strategy.yaml")
        statuses = {
            "protocol.md": protocol_status,
            "eligibility_criteria.yaml": eligibility.get("status"),
            "search_strategy.yaml": strategy.get("status"),
        }
        unapproved = [name for name, status in statuses.items() if status != "approved"]
        if unapproved:
            raise GovernanceValidationError(
                "protocol artifacts must be approved before freezing: " + ", ".join(unapproved)
            )
        for relative_path in NON_EMPTY_REVIEW_CSVS:
            self._require_csv_rows(review_root / relative_path, review_id=review_id)
        self._require_global_evidence_rows()
        audit = self._load_json(review_root / "06-quality/corpus_audit.json")
        if audit.get("status") != "complete" or audit.get("is_compliant") is not True:
            raise GovernanceValidationError("corpus_audit.json must be complete and compliant")
        for relative_path in (
            "07-selection-freeze/prisma_flow.md",
            "07-selection-freeze/prisma_checklist.md",
        ):
            if self._markdown_status(review_root / relative_path) != "complete":
                raise GovernanceValidationError(f"{relative_path} must have status: complete")

    def _require_global_evidence_rows(self) -> None:
        required = (
            "literature/records/search_log.csv",
            "literature/records/candidates.csv",
            "literature/records/journal_metrics.csv",
            "literature/records/citation_snapshots.csv",
            "literature/records/screening.csv",
        )
        for relative_path in required:
            self._require_csv_rows(self.paths.knowledge_root / relative_path)

    @staticmethod
    def _require_csv_rows(path: Path, *, review_id: str | None = None) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise GovernanceValidationError(f"required CSV has no data rows: {path}")
        if review_id is not None:
            mismatches = [row.get("review_id") for row in rows if row.get("review_id") != review_id]
            if mismatches:
                raise GovernanceValidationError(f"CSV contains rows for another review: {path}")
        return rows

    def _load_prisma_counts(self, review_root: Path) -> PrismaCounts:
        path = review_root / "07-selection-freeze/prisma_counts.json"
        try:
            return PrismaCounts.model_validate(self._load_json(path))
        except ValidationError as exc:
            raise GovernanceValidationError(str(exc)) from exc

    def _load_included_studies(
        self,
        review_root: Path,
        review_id: str,
    ) -> tuple[IncludedStudyRecord, ...]:
        path = review_root / "07-selection-freeze/included_studies.csv"
        rows = self._require_csv_rows(path, review_id=review_id)
        try:
            records = tuple(
                IncludedStudyRecord.model_validate(
                    {
                        "study_id": row.get("study_id"),
                        "report_id": row.get("report_id"),
                        "resource_id": row.get("resource_id"),
                    }
                )
                for row in rows
            )
        except ValidationError as exc:
            raise GovernanceValidationError(f"invalid included_studies.csv: {exc}") from exc
        report_ids = [record.report_id for record in records]
        resource_ids = [record.resource_id for record in records]
        if len(report_ids) != len(set(report_ids)):
            raise GovernanceValidationError("included report_id values must be unique")
        if len(resource_ids) != len(set(resource_ids)):
            raise GovernanceValidationError("included resource_id values must be unique")
        return records

    @staticmethod
    def _validate_included_counts(
        counts: PrismaCounts,
        included_studies: tuple[IncludedStudyRecord, ...],
    ) -> None:
        report_count = len({record.report_id for record in included_studies})
        study_count = len({record.study_id for record in included_studies})
        if counts.reports_included != report_count:
            raise GovernanceValidationError(
                "reports_included does not match unique report_id count"
            )
        if counts.studies_included != study_count:
            raise GovernanceValidationError(
                "studies_included does not match unique study_id count"
            )

    def _build_artifact_digests(self, review_root: Path) -> tuple[ArtifactDigest, ...]:
        return tuple(
            ArtifactDigest(path=self._portable_path(path), sha256=self._sha256(path))
            for path in self._artifact_paths(review_root)
        )

    def _artifact_paths(self, review_root: Path) -> tuple[Path, ...]:
        global_paths = tuple(self.paths.knowledge_root / path for path in GLOBAL_ARTIFACTS)
        review_paths = tuple(review_root / path for path in REVIEW_ARTIFACTS)
        return global_paths + review_paths

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise GovernanceValidationError(f"invalid JSON artifact {path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise GovernanceValidationError(f"JSON artifact must contain an object: {path}")
        return payload

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise GovernanceValidationError(f"invalid YAML artifact {path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise GovernanceValidationError(f"YAML artifact must contain a mapping: {path}")
        return payload

    @staticmethod
    def _markdown_status(path: Path) -> str | None:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise GovernanceValidationError(f"cannot read Markdown artifact {path}: {exc}") from exc
        match = re.search(r"(?m)^status:\s*([a-z_]+)\s*$", text)
        return match.group(1) if match else None

    @staticmethod
    def _validated_literature_manifest(manifest_path: Path):
        batch = preflight_manifest(manifest_path)
        if batch.failures:
            details = "; ".join(
                f"line {failure.line_number}: {failure.reason}" for failure in batch.failures
            )
            raise GovernanceValidationError(f"Manifest technical preflight failed: {details}")
        if not batch.records:
            raise GovernanceValidationError("Manifest contains no valid records")
        resource_types = {record.resource_type for record in batch.records}
        if resource_types != {ResourceType.LITERATURE}:
            raise GovernanceValidationError("Manifest release accepts literature records only")
        if any(not record.include for record in batch.records):
            raise GovernanceValidationError("released literature records require include=true")
        return batch.records

    def _portable_path(self, path: Path) -> str:
        resolved = path.resolve()
        try:
            return resolved.relative_to(self.paths.repo_root.resolve()).as_posix()
        except ValueError:
            return resolved.as_posix()

    def _resolve_bound_path(self, value: str) -> Path:
        path = Path(value)
        return path.resolve() if path.is_absolute() else (self.paths.repo_root / path).resolve()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _sha256_existing(self, path: Path, label: str) -> str:
        if not path.is_file():
            raise GovernanceValidationError(f"bound {label} is missing: {path}")
        return self._sha256(path)

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
