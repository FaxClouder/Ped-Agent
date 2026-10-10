"""Candidate index preflight must not silently accept corpus drift."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_candidates import verify_manifest_members, guard_output, chroma_content_sha256


def test_manifest_preflight_rejects_source_or_membership_change() -> None:
    records = [{"resource_id": "a", "sha256": "abc", "include": True}]
    verify_manifest_members(records, {"a": "abc"}, expected_count=1)
    with pytest.raises(ValueError, match="members"):
        verify_manifest_members(records, {"a": "changed"}, expected_count=1)
    with pytest.raises(ValueError, match="members"):
        verify_manifest_members(records, {"a": "abc"}, expected_count=104)


def test_candidate_index_refuses_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "index"
    output.mkdir()
    (output / "keep").write_text("preserve", encoding="utf-8")
    with pytest.raises(FileExistsError):
        guard_output(output)
    assert (output / "keep").read_text(encoding="utf-8") == "preserve"


def test_chroma_content_fingerprint_changes_with_vector() -> None:
    class Collection:
        def __init__(self, vector: list[float]) -> None:
            self.vector = vector

        def get(self, *, include: list[str]) -> dict:
            assert include == ["embeddings", "documents", "metadatas"]
            return {"ids": ["child"], "embeddings": [self.vector],
                    "documents": ["source text"], "metadatas": [{"resource_id": "r1"}]}

    assert chroma_content_sha256(Collection([0.1, 0.2])) != chroma_content_sha256(Collection([0.1, 0.3]))
