"""Read-only inventory and hash manifest for a memPed workspace."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


def build_inventory(root: Path, output: Path) -> dict[str, Any]:
    """Scan runtime assets without changing the workspace.

    ``root`` is expected to be the ``memPed`` directory.  The report deliberately
    describes absent runtime assets instead of creating them, so it can be used
    before a migration or rebuild.
    """

    knowledge = root / "knowledge"
    source_files = []
    for directory in (knowledge / "literature" / "files", knowledge / "regulations" / "files"):
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                source_files.append(
                    {
                        "relative_path": path.relative_to(root).as_posix(),
                        "size": path.stat().st_size,
                        "sha256": _sha256(path),
                    }
                )

    derived = knowledge / "derived"
    report: dict[str, Any] = {
        "root": str(root.resolve()),
        "source_files": {"count": len(source_files), "files": source_files},
        "runtime_assets": {
            "catalog_exists": (knowledge / "knowledge.sqlite3").exists(),
            "fts_exists": (knowledge / "fts.sqlite3").exists(),
            "vector_index_exists": (knowledge / "indexes").exists(),
            "derived_file_count": sum(1 for path in derived.rglob("*") if path.is_file())
            if derived.exists()
            else 0,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def backup_sqlite(source: Path, target: Path) -> None:
    """Create a consistent SQLite backup without modifying ``source``."""

    target.parent.mkdir(parents=True, exist_ok=True)
    source_connection = sqlite3.connect(source)
    target_connection = sqlite3.connect(target)
    try:
        source_connection.backup(target_connection)
        target_connection.commit()
    finally:
        target_connection.close()
        source_connection.close()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


__all__ = ["backup_sqlite", "build_inventory"]
