"""V2 evaluation must reject a mismatched candidate index before running models."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_v2_candidate import verify_report


def test_candidate_report_requires_matching_policy_and_fingerprints() -> None:
    report = {
        "status": "complete_candidate_index", "mode": "v2", "policy_version": "parent-child-v2",
        "manifest_sha256": "manifest", "tokenizer_fingerprint": "hf-tokenizer:abc",
        "lexical_analyzer_fingerprint": "jieba-lexical-v1:abc",
        "catalog_or_chunk_fingerprint": "chunks", "embedding_fingerprint": "model",
        "chroma_content_sha256": "vectors", "output_sha256": {"fts.sqlite3": "fts"},
    }
    verify_report(report, manifest_sha="manifest")
    with pytest.raises(ValueError, match="policy"):
        verify_report({**report, "policy_version": "parent-child-v1"}, manifest_sha="manifest")
    with pytest.raises(ValueError, match="corpus"):
        verify_report(report, manifest_sha="changed")
    with pytest.raises(ValueError, match="fingerprint"):
        verify_report({**report, "chroma_content_sha256": None}, manifest_sha="manifest")
