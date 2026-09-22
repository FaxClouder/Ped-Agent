from __future__ import annotations

import json
from pathlib import Path

from ped_knowledge.storage.inventory import backup_sqlite, build_inventory


def test_build_inventory_is_read_only_and_reports_missing_runtime_assets(tmp_path: Path) -> None:
    root = tmp_path / "memped"
    (root / "knowledge" / "literature" / "files").mkdir(parents=True)
    (root / "knowledge" / "knowledge.sqlite3").write_bytes(b"sqlite-placeholder")
    (root / "knowledge" / "literature" / "files" / "paper.pdf").write_bytes(b"pdf")
    output = tmp_path / "report.json"

    report = build_inventory(root, output)

    assert report["runtime_assets"]["catalog_exists"] is True
    assert report["runtime_assets"]["fts_exists"] is False
    assert report["runtime_assets"]["derived_file_count"] == 0
    assert report["source_files"]["count"] == 1
    assert json.loads(output.read_text(encoding="utf-8")) == report
    assert (root / "knowledge" / "knowledge.sqlite3").read_bytes() == b"sqlite-placeholder"


def test_build_inventory_records_sha256_for_source_files(tmp_path: Path) -> None:
    root = tmp_path / "memped"
    source = root / "knowledge" / "regulations" / "files" / "rule.pdf"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"known-content")

    report = build_inventory(root, tmp_path / "report.json")

    assert (
        report["source_files"]["files"][0]["relative_path"]
        == "knowledge/regulations/files/rule.pdf"
    )
    assert len(report["source_files"]["files"][0]["sha256"]) == 64


def test_backup_sqlite_creates_a_consistent_copy(tmp_path: Path) -> None:
    import sqlite3

    source = tmp_path / "source.sqlite3"
    connection = sqlite3.connect(source)
    connection.execute("create table sample (value text)")
    connection.execute("insert into sample values ('kept')")
    connection.commit()
    connection.close()

    target = tmp_path / "backup.sqlite3"
    backup_sqlite(source, target)

    restored = sqlite3.connect(target)
    assert restored.execute("select value from sample").fetchone() == ("kept",)
    restored.close()
