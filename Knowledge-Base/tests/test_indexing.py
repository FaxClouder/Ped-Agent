from __future__ import annotations

from pathlib import Path

import pytest

from ped_knowledge.indexing import FTSIndex
from ped_knowledge.tokenization import JiebaLexicalAnalyzer


def _analyzer(tmp_path: Path, *, stopwords: str = "与\nand\n") -> JiebaLexicalAnalyzer:
    terms = tmp_path / "terms.txt"
    terms.write_text("社会力模型\n行人流基本图\nBGE-M3\n", encoding="utf-8")
    stopword_file = tmp_path / "stopwords.txt"
    stopword_file.write_text(stopwords, encoding="utf-8")
    return JiebaLexicalAnalyzer(
        domain_terms_path=terms,
        stopwords_path=stopword_file,
        version="jieba-lexical-v1",
    )


def _chunk(body: str) -> dict[str, object]:
    return {
        "chunk_id": "chunk-1",
        "resource_id": "resource-1",
        "version_id": "version-1",
        "title": "Pedestrian study",
        "heading_path": ["方法"],
        "text": body,
        "locator": "p.1",
    }


def test_domain_analyzer_preserves_terms_and_removes_stopwords(tmp_path: Path) -> None:
    analyzer = _analyzer(tmp_path)

    tokens = analyzer.analyze("社会力模型与行人流基本图 BGE-M3 2024")

    assert "社会力模型" in tokens
    assert "行人流基本图" in tokens
    assert "与" not in tokens
    assert "bge-m3" in tokens
    assert "2024" in tokens


def test_fts_or_query_recalls_when_only_one_term_matches(tmp_path: Path) -> None:
    analyzer = _analyzer(tmp_path)
    index = FTSIndex(tmp_path / "fts.sqlite3", analyzer=analyzer)
    index.rebuild([_chunk("社会力模型")], source_fingerprint="source-v1")

    hits = index.search("社会力模型 不存在的附加词")

    assert [hit.chunk_id for hit in hits] == ["chunk-1"]


def test_fts_rejects_a_different_lexical_fingerprint(tmp_path: Path) -> None:
    path = tmp_path / "fts.sqlite3"
    analyzer = _analyzer(tmp_path)
    FTSIndex(path, analyzer=analyzer).rebuild(
        [_chunk("社会力模型")], source_fingerprint="source-v1"
    )
    changed = _analyzer(tmp_path, stopwords="与\nand\nthe\n")

    with pytest.raises(ValueError, match="lexical analyzer fingerprint"):
        FTSIndex(path, analyzer=changed).search("社会力模型")
