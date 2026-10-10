"""Focused invariants for the frozen Adobe child retrieval comparison."""

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("pearl_compare_pilot", HERE / "compare_pilot.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_rrf_uses_one_based_ranks_deduplicates_and_ties_by_id():
    sparse = [{"chunk_id": "b"}, {"chunk_id": "a"}]
    dense = [{"chunk_id": "c"}, {"chunk_id": "a"}]
    result = MODULE.rrf_union(sparse, dense, 60)
    assert [row["chunk_id"] for row in result] == ["a", "b", "c"]
    assert result[0]["score"] == 2 / 62
    assert result[1]["score"] == result[2]["score"] == 1 / 61
    assert result[0]["r1_rank"] == result[0]["r2_rank"] == 2


def test_ranked_results_use_unchanged_child_text_and_hash():
    child = {"chunk_id": "c", "text": "width 2 m", "text_sha256": MODULE.text_sha("width 2 m")}
    ranked = MODULE.attach_children([{"chunk_id": "c", "score": 0.5}], {"c": child})
    assert ranked == [{"rank": 1, "score": 0.5, **child}]


def test_new_gold_preserves_eight_intents_and_binds_only_frozen_sources():
    pilot = HERE.parents[1] / "paper/pearl-framework/datasets/retrieval-pilot"
    previous = json.loads((pilot / "pilot-intents-agent-reviewed-v4.json").read_text(encoding="utf-8"))
    current = json.loads((pilot / "pearl-retrieval-dev-pilot-8-adobe106-gold.json").read_text(encoding="utf-8"))
    assert current["intents"] == previous["intents"]
    manifest_path = HERE.parents[1] / "paper/pearl-framework/datasets/retrieval-corpus/corpus-manifest-v02.jsonl"
    sources = {row["source_id"]: row for row in map(json.loads, manifest_path.read_text(encoding="utf-8").splitlines())}
    assert len(sources) == 106
    assert current["corpus_manifest_sha256"] == MODULE.sha(manifest_path)
    assert {row["source_id"] for row in current["source_bindings"]} == {
        atom["source_id"] for intent in current["intents"] for atom in intent["atoms"]
    }
    for binding in current["source_bindings"]:
        assert binding["source_sha256"] == sources[binding["source_id"]]["sha256"]
