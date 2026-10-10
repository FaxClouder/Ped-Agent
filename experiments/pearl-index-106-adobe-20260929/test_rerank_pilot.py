"""Invariants for the frozen-candidate reranker comparison."""

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).with_name('rerank_pilot.py')
SPEC = importlib.util.spec_from_file_location('rerank_pilot', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_reranking_preserves_candidates_and_uses_chunk_id_for_ties():
    original = [
        {'chunk_id': 'b', 'text': 'second', 'text_sha256': 'bhash', 'rank': 1, 'score': 0.1},
        {'chunk_id': 'a', 'text': 'first', 'text_sha256': 'ahash', 'rank': 2, 'score': 0.2},
        {'chunk_id': 'c', 'text': 'third', 'text_sha256': 'chash', 'rank': 3, 'score': 0.3},
    ]
    actual = MODULE.rerank_results(original, [2.0, 2.0, -1.0])
    assert [(r['chunk_id'], r['rank'], r['score'], r['r3_rank']) for r in actual] == [
        ('a', 1, 2.0, 2), ('b', 2, 2.0, 1), ('c', 3, -1.0, 3)
    ]
    assert {r['chunk_id']: r['text'] for r in actual} == {r['chunk_id']: r['text'] for r in original}


def test_reranking_rejects_missing_or_nonfinite_scores():
    original = [{'chunk_id': 'a', 'rank': 1}, {'chunk_id': 'b', 'rank': 2}]
    with pytest.raises(ValueError):
        MODULE.rerank_results(original, [0.5])
    with pytest.raises(ValueError):
        MODULE.rerank_results(original, [0.5, float('nan')])
