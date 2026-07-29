import hashlib
import json
from pathlib import Path

import pytest

from ped_agent.manifest import ManifestPreflightError, load_and_preflight
from ped_agent.vault import ContentVault, sha256_file


def write_manifest(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")


def test_preflight_rejects_hash_mismatch_without_creating_storage(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            {
                "resource_id": "paper-preflight-2026",
                "resource_type": "literature",
                "title": "Preflight paper",
                "language": "en",
                "source_path": str(source),
                "sha256": "0" * 64,
                "doi": "10.1000/preflight",
                "include": True,
            }
        ],
    )

    with pytest.raises(ManifestPreflightError, match="SHA-256 mismatch"):
        load_and_preflight(manifest)

    assert not (tmp_path / "storage").exists()


def test_preflight_accepts_matching_hash(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            {
                "resource_id": "paper-preflight-2026",
                "resource_type": "literature",
                "title": "Preflight paper",
                "language": "en",
                "source_path": str(source),
                "sha256": digest,
                "doi": "10.1000/preflight",
                "include": True,
            }
        ],
    )

    assert load_and_preflight(manifest)[0].resource_id == "paper-preflight-2026"


def test_preflight_reports_duplicate_ids_and_missing_files(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    digest = sha256_file(source)
    base = {
        "resource_id": "paper-duplicate-2026",
        "resource_type": "literature",
        "title": "Duplicate paper",
        "language": "en",
        "sha256": digest,
        "doi": "10.1000/duplicate",
        "include": True,
    }
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            {**base, "source_path": str(source)},
            {**base, "source_path": str(source)},
            {
                **base,
                "resource_id": "paper-missing-2026",
                "source_path": str(tmp_path / "missing.pdf"),
            },
        ],
    )

    with pytest.raises(ManifestPreflightError) as error:
        load_and_preflight(manifest)

    assert "duplicate resource_id paper-duplicate-2026" in str(error.value)
    assert "missing file" in str(error.value)


def test_content_vault_is_content_addressed_and_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "paper.PDF"
    source.write_bytes(b"%PDF-vault")
    digest = sha256_file(source)
    vault = ContentVault(tmp_path / "objects")

    first = vault.put(source, digest)
    second = vault.put(source, digest)

    assert first == tmp_path / "objects" / digest[:2] / f"{digest}.pdf"
    assert second == first
    assert first.read_bytes() == source.read_bytes()
