from __future__ import annotations

from pathlib import Path

import pytest

from ped_knowledge.indexing import FTSIndex
from ped_knowledge.tokenization import EnglishLexicalAnalyzer


def _chunk(body: str) -> dict[str, object]:
    return {
        "chunk_id": "chunk-1",
        "resource_id": "resource-1",
        "version_id": "version-1",
        "title": "Pedestrian study",
        "heading_path": ["Methods"],
        "text": body,
        "locator": "p.1",
    }


def test_fts_defaults_to_english_analyzer(tmp_path: Path) -> None:
    index = FTSIndex(tmp_path / "fts.sqlite3")

    assert index.analyzer.fingerprint == EnglishLexicalAnalyzer().fingerprint


def test_fts_or_query_recalls_when_only_one_term_matches(tmp_path: Path) -> None:
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild([_chunk("Social force model of evacuation")], source_fingerprint="source-v1")

    hits = index.search("evacuation nonexistentterm")

    assert [hit.chunk_id for hit in hits] == ["chunk-1"]
    assert index.lexical_analyzer_fingerprint() == EnglishLexicalAnalyzer().fingerprint


def test_fts_rejects_a_different_lexical_fingerprint(tmp_path: Path) -> None:
    path = tmp_path / "fts.sqlite3"
    FTSIndex(path).rebuild([_chunk("Social force model")], source_fingerprint="source-v1")
    changed = EnglishLexicalAnalyzer(version="english-lexical-v2")

    with pytest.raises(ValueError, match="lexical analyzer fingerprint"):
        FTSIndex(path, analyzer=changed).search("social force")
