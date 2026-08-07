"""Compatibility adapter for the former quality-gated import entrypoint."""

from pathlib import Path

from ped_knowledge.ingestion import (
    ImportFailure,
    ImportReport,
)
from ped_knowledge.ingestion import (
    ImportService as KnowledgeImportService,
)

from ped_agent_server.manifest import load_and_preflight


class ImportService(KnowledgeImportService):
    """Preserve the old strict import contract for existing callers and tests.

    The active CLI imports :class:`ped_knowledge.ingestion.ImportService` directly and therefore
    uses technical preflight without JCI, CAS, citation, or content-score gates.
    """

    def import_manifest(self, manifest_path: Path) -> ImportReport:
        load_and_preflight(manifest_path)
        return super().import_manifest(manifest_path)


__all__ = ["ImportFailure", "ImportReport", "ImportService"]
