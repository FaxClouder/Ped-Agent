"""Technical preflight and isolated document import orchestration."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError

from ped_knowledge.chunking import HierarchicalChunker
from ped_knowledge.contracts import ChunkingPolicy, IngestionManifest, OCRGateway
from ped_knowledge.parsing import parse_document, write_derived_assets
from ped_knowledge.storage import Catalog, ContentVault, sha256_file


class KnowledgeWorkspace(Protocol):
    memped_root: Path
    catalog_path: Path
    derived_dir: Path
    reports_dir: Path

    def ensure_local_dirs(self) -> None: ...

    def resource_files_dir(self, resource_type: str) -> Path: ...


@dataclass(frozen=True)
class TechnicalPreflightFailure:
    resource_id: str
    reason: str
    line_number: int


@dataclass(frozen=True)
class TechnicalPreflightBatch:
    records: tuple[IngestionManifest, ...]
    failures: tuple[TechnicalPreflightFailure, ...]

    @property
    def is_valid(self) -> bool:
        return not self.failures


class ManifestPreflightError(ValueError):
    pass


@dataclass(frozen=True)
class ImportFailure:
    resource_id: str
    reason: str


@dataclass(frozen=True)
class ImportReport:
    imported: int
    unchanged: int
    failures: tuple[ImportFailure, ...]


def preflight_manifest(path: Path) -> TechnicalPreflightBatch:
    records: list[IngestionManifest] = []
    failures: list[TechnicalPreflightFailure] = []
    seen_ids: set[str] = set()
    seen_dois: set[str] = set()
    seen_hashes: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        resource_id = f"line-{line_number}"
        try:
            payload = json.loads(line)
            if isinstance(payload, dict) and payload.get("resource_id"):
                resource_id = str(payload["resource_id"])
            record = IngestionManifest.model_validate(payload)
            record = _resolve_source_path(record, manifest_path=path)
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            failures.append(TechnicalPreflightFailure(resource_id, str(exc), line_number))
            continue
        errors = _technical_errors(
            record,
            seen_ids=seen_ids,
            seen_dois=seen_dois,
            seen_hashes=seen_hashes,
        )
        if errors:
            failures.extend(
                TechnicalPreflightFailure(record.resource_id, error, line_number)
                for error in errors
            )
            continue
        records.append(record)
    return TechnicalPreflightBatch(tuple(records), tuple(failures))


def load_technical_manifest(path: Path) -> list[IngestionManifest]:
    batch = preflight_manifest(path)
    if batch.failures:
        details = "; ".join(f"line {item.line_number}: {item.reason}" for item in batch.failures)
        raise ManifestPreflightError(details)
    return list(batch.records)


class ImportService:
    def __init__(
        self,
        paths: KnowledgeWorkspace,
        *,
        chunking_policy: ChunkingPolicy | None = None,
        ocr_gateway: OCRGateway | None = None,
    ) -> None:
        self.paths = paths
        self.chunker = HierarchicalChunker(chunking_policy)
        self.ocr_gateway = ocr_gateway

    def import_manifest(self, manifest_path: Path) -> ImportReport:
        batch = preflight_manifest(manifest_path)
        self.paths.ensure_local_dirs()
        catalog = Catalog(self.paths.catalog_path)
        catalog.initialize()
        imported = 0
        unchanged = 0
        failures = [ImportFailure(item.resource_id, item.reason) for item in batch.failures]
        for record in batch.records:
            version_id = record.sha256
            existing = catalog.get_resource(record.resource_id)
            if (
                existing
                and existing.get("active_version_id") == version_id
                and existing["canonical_metadata"].get("sha256") == record.sha256
            ):
                unchanged += 1
                continue
            staged = False
            try:
                vault = ContentVault(self.paths.resource_files_dir(record.resource_type.value))
                vault_path = vault.put(record.source_path, record.sha256)
                catalog.stage_resource(
                    record,
                    version_id=version_id,
                    vault_path=str(vault_path.relative_to(self.paths.memped_root)),
                )
                staged = True
                canonical, parse_report = parse_document(
                    vault_path,
                    resource_id=record.resource_id,
                    version_id=version_id,
                    detect_clauses=record.resource_type.value in {"regulation", "standard"},
                    ocr_gateway=self.ocr_gateway,
                )
                chunks = self.chunker.chunk(canonical)
                assets = write_derived_assets(
                    self.paths.derived_dir,
                    canonical,
                    parse_report,
                    chunks,
                    source_path=vault_path,
                )
                derived_path = self.paths.derived_dir / record.resource_id / version_id
                catalog.replace_chunks(version_id, chunks)
                catalog.set_version_derivation(
                    version_id,
                    derived_path=str(derived_path.relative_to(self.paths.memped_root)),
                    parser_version=canonical.parser_version,
                    chunk_policy_version=self.chunker.policy.policy_version,
                )
                catalog.register_derived_assets(
                    record.resource_id,
                    version_id,
                    assets,
                )
                catalog.activate_version(record.resource_id, version_id)
                imported += 1
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                if staged:
                    catalog.mark_version_failed(version_id)
                failures.append(ImportFailure(record.resource_id, str(exc)))
        return ImportReport(imported, unchanged, tuple(failures))


def _resolve_source_path(
    record: IngestionManifest,
    *,
    manifest_path: Path,
) -> IngestionManifest:
    if record.source_path.is_absolute():
        return record
    manifest_relative = (manifest_path.parent / record.source_path).resolve()
    cwd_relative = record.source_path.resolve()
    resolved = manifest_relative if manifest_relative.exists() else cwd_relative
    return record.model_copy(update={"source_path": resolved})


def _technical_errors(
    record: IngestionManifest,
    *,
    seen_ids: set[str],
    seen_dois: set[str],
    seen_hashes: set[str],
) -> list[str]:
    errors: list[str] = []
    if record.resource_id in seen_ids:
        errors.append(f"duplicate resource_id {record.resource_id}")
    else:
        seen_ids.add(record.resource_id)
    normalized_doi = _normalized_doi(record.doi)
    if normalized_doi:
        if normalized_doi in seen_dois:
            errors.append(f"duplicate DOI {normalized_doi}")
        else:
            seen_dois.add(normalized_doi)
    if record.sha256 in seen_hashes:
        errors.append(f"duplicate SHA-256 {record.sha256}")
    else:
        seen_hashes.add(record.sha256)
    if not record.source_path.is_file():
        errors.append(f"missing file {record.source_path}")
        return errors
    try:
        with record.source_path.open("rb") as source:
            signature = source.read(5)
        if signature != b"%PDF-":
            errors.append(f"invalid PDF signature for {record.source_path}")
        if sha256_file(record.source_path) != record.sha256:
            errors.append(f"SHA-256 mismatch for {record.source_path}")
        _inspect_pdf(record.source_path)
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(str(exc))
    return errors


def _inspect_pdf(path: Path) -> None:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF technical preflight") from exc
    try:
        with fitz.open(path) as document:
            if document.needs_pass:
                raise ValueError(f"encrypted PDF is not supported: {path}")
            if document.page_count < 1:
                raise ValueError(f"PDF has no pages: {path}")
            for page in document:
                page.get_text("text")
    except (RuntimeError, ValueError) as exc:
        raise ValueError(f"unreadable PDF {path}: {exc}") from exc


def _normalized_doi(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        normalized = normalized.removeprefix(prefix)
    return normalized or None


__all__ = [
    "ImportFailure",
    "ImportReport",
    "ImportService",
    "ManifestPreflightError",
    "TechnicalPreflightBatch",
    "TechnicalPreflightFailure",
    "load_technical_manifest",
    "preflight_manifest",
]
