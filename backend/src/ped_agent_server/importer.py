from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ped_agent_server.catalog import Catalog
from ped_agent_server.manifest import load_and_preflight
from ped_agent_server.parsing import parse_pdf
from ped_agent_server.paths import WorkspacePaths
from ped_agent_server.vault import ContentVault


@dataclass(frozen=True)
class ImportFailure:
    resource_id: str
    reason: str


@dataclass(frozen=True)
class ImportReport:
    imported: int
    unchanged: int
    failures: tuple[ImportFailure, ...]


class ImportService:
    def __init__(self, paths: WorkspacePaths) -> None:
        self.paths = paths

    def import_manifest(self, manifest_path: Path) -> ImportReport:
        records = load_and_preflight(manifest_path)
        self.paths.ensure_local_dirs()
        catalog = Catalog(self.paths.catalog_path)
        catalog.initialize()
        vault = ContentVault(self.paths.objects_dir)
        imported = 0
        unchanged = 0
        failures: list[ImportFailure] = []
        for record in records:
            version_id = record.sha256
            existing = catalog.get_resource(record.resource_id)
            if existing and existing["canonical_metadata"]["sha256"] == record.sha256:
                unchanged += 1
                continue
            try:
                vault_path = vault.put(record.source_path, record.sha256)
                chunks = parse_pdf(
                    vault_path,
                    resource_id=record.resource_id,
                    version_id=version_id,
                    detect_clauses=record.resource_type.value in {"regulation", "standard"},
                )
                catalog.upsert_resource(
                    record,
                    version_id=version_id,
                    vault_path=str(vault_path.relative_to(self.paths.library_root)),
                )
                catalog.replace_chunks(version_id, chunks)
                imported += 1
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                # A batch item is the isolation boundary: record its dependency or parsing
                # failure, while allowing independently valid resources to finish importing.
                failures.append(ImportFailure(record.resource_id, str(exc)))
        return ImportReport(
            imported=imported,
            unchanged=unchanged,
            failures=tuple(failures),
        )
