from pathlib import Path

import pytest

from ped_agent_server.index import FTSIndex
from ped_agent_server.tokenization import tokenize_for_search


def test_tokenizer_preserves_searchable_chinese_and_english_terms() -> None:
    tokens = tokenize_for_search(" 人群密度 Pedestrian FLOW ")

    assert "人群" in tokens.split()
    assert "密度" in tokens.split()
    assert "pedestrian" in tokens.split()
    assert "flow" in tokens.split()


def test_fts_index_retrieves_chinese_and_english_queries(tmp_path: Path) -> None:
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(
        [
            {
                "chunk_id": "zh-1",
                "resource_id": "reg-1",
                "title": "疏散规范",
                "text": "安全出口附近的人群密度需要受到控制",
                "locator": "第5.2条",
            },
            {
                "chunk_id": "en-1",
                "resource_id": "paper-1",
                "title": "Bottleneck experiment",
                "text": "Pedestrian bottleneck flow decreases under severe congestion",
                "locator": "p.4",
            },
        ],
        source_fingerprint="v1",
    )

    assert index.search("人群密度", limit=3)[0].chunk_id == "zh-1"
    assert index.search("bottleneck congestion", limit=3)[0].chunk_id == "en-1"
    assert index.search("   ", limit=3) == []
    assert index.source_fingerprint() == "v1"


def test_failed_rebuild_keeps_last_valid_index(tmp_path: Path) -> None:
    index = FTSIndex(tmp_path / "fts.sqlite3")
    assert index.source_fingerprint() == ""
    index.rebuild(
        [
            {
                "chunk_id": "old",
                "resource_id": "r1",
                "title": "density",
                "text": "density evidence",
                "locator": "p.1",
            }
        ],
        source_fingerprint="v1",
    )

    with pytest.raises(KeyError):
        index.rebuild([{"chunk_id": "broken"}], source_fingerprint="v2")

    assert index.search("density", limit=3)[0].chunk_id == "old"
    assert index.source_fingerprint() == "v1"
