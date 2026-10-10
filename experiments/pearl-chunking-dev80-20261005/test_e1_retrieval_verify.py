import json
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from e1_retrieval_verify import (
    CONFIG_PATH,
    PINNED_RERANKER_CONFIG,
    assert_actual_inputs,
    capture_forward_inputs,
    compare_ranked_scores,
    rerank_results,
    sparse_query,
    validate_reranker_config,
    verify_r1_result,
    write_receipt,
)


def _build_fts(path: Path) -> None:
    from ped_knowledge.indexing import FTSIndex
    from ped_knowledge.tokenization import EnglishLexicalAnalyzer

    rows = [
        dict(chunk_id="b", resource_id="d", version_id="v", title="", heading_path=[], text="alpha", locator="b"),
        dict(chunk_id="a", resource_id="d", version_id="v", title="", heading_path=[], text="alpha", locator="a"),
        dict(chunk_id="c", resource_id="d", version_id="v", title="", heading_path=[], text="gamma", locator="c"),
    ]
    FTSIndex(path, analyzer=EnglishLexicalAnalyzer()).rebuild(
        rows,
        source_fingerprint="fixture",
        policy_version="fixture",
        tokenizer_fingerprint="fixture",
        code_revision="fixture",
    )


def test_sparse_query_reopens_sqlite_with_frozen_analyzer_and_tie_break(tmp_path):
    index = tmp_path / "fts.sqlite3"
    _build_fts(index)

    result = sparse_query(index, "ＡＬＰＨＡ alpha", limit=100)

    assert [row["chunk_id"] for row in result] == ["a", "b"]
    assert [row["rank"] for row in result] == [1, 2]
    assert all(row["score"] > 0 for row in result)


def test_r1_verification_accepts_legal_short_and_empty_result_lists(tmp_path):
    index = tmp_path / "fts.sqlite3"
    _build_fts(index)
    children = {
        key: {"chunk_id": key, "text": "alpha", "text_sha256": "text-hash"}
        for key in ("a", "b")
    }
    fresh_short = sparse_query(index, "alpha", limit=100)
    saved_short = [
        dict(row, text="alpha", text_sha256="text-hash")
        for row in fresh_short
    ]
    assert verify_r1_result(saved_short, fresh_short, children, "short") == 2

    fresh_empty = sparse_query(index, "missingterm", limit=100)
    assert fresh_empty == []
    assert verify_r1_result([], fresh_empty, children, "empty") == 0


def test_compare_ranked_scores_requires_exact_order_and_explicit_tolerance():
    saved = [dict(chunk_id="a", rank=1, score=1.0), dict(chunk_id="b", rank=2, score=0.5)]
    within = [dict(chunk_id="a", rank=1, score=1.0 + 5e-7), dict(chunk_id="b", rank=2, score=0.5)]
    compare_ranked_scores("R4", saved, within, expected_count=2, abs_tolerance=1e-6)

    with pytest.raises(ValueError, match="order"):
        compare_ranked_scores("R4", saved, list(reversed(within)), expected_count=2, abs_tolerance=1e-6)
    with pytest.raises(ValueError, match="score"):
        compare_ranked_scores(
            "R4", saved,
            [dict(chunk_id="a", rank=1, score=1.0 + 2e-6), dict(chunk_id="b", rank=2, score=0.5)],
            expected_count=2,
            abs_tolerance=1e-6,
        )

    saved_r4 = [dict(chunk_id="a", rank=1, r3_rank=2, score=1.0)]
    fresh_r4 = [dict(chunk_id="a", rank=1, r3_rank=1, score=1.0)]
    with pytest.raises(ValueError, match="r3_rank"):
        compare_ranked_scores(
            "R4", saved_r4, fresh_r4,
            expected_count=1,
            abs_tolerance=1e-6,
            exact_fields=("r3_rank",),
        )


def test_rerank_results_uses_raw_score_then_chunk_id_and_retains_r3_rank():
    original = [dict(chunk_id="b", rank=1, text="B"), dict(chunk_id="a", rank=2, text="A")]
    ranked = rerank_results(original, [0.25, 0.25])
    assert [(row["chunk_id"], row["rank"], row["r3_rank"]) for row in ranked] == [
        ("a", 1, 2),
        ("b", 2, 1),
    ]
    with pytest.raises(ValueError, match="finite"):
        rerank_results(original, [0.25, float("nan")])


class _Array:
    def __init__(self, value):
        self.value = value

    def detach(self):
        return self

    def cpu(self):
        return self

    def tolist(self):
        return self.value


class _Handle:
    def __init__(self, model):
        self.model = model

    def remove(self):
        self.model.hook = None


class _Model:
    def __init__(self):
        self.hook = None

    def register_forward_pre_hook(self, hook, with_kwargs):
        assert with_kwargs is True
        self.hook = hook
        return _Handle(self)

    def forward(self, payload):
        self.hook(self, (payload,), {})


def test_forward_hook_captures_attention_mask_trimmed_actual_inputs():
    model = _Model()
    with capture_forward_inputs(model) as actual:
        model.forward({
            "input_ids": _Array([[10, 11, 0], [20, 21, 22]]),
            "attention_mask": _Array([[1, 1, 0], [1, 1, 1]]),
        })
    assert actual == [[10, 11], [20, 21, 22]]
    assert actual.hook_seconds >= 0
    assert_actual_inputs([[10, 11], [20, 21, 22]], actual)
    with pytest.raises(ValueError, match="actual model input"):
        assert_actual_inputs([[99]], actual)


def test_reranker_config_is_fully_pinned():
    validate_reranker_config(json.loads(CONFIG_PATH.read_text(encoding="utf8")))
    validate_reranker_config(dict(PINNED_RERANKER_CONFIG))
    changed = dict(PINNED_RERANKER_CONFIG, batch_size=8)
    with pytest.raises(ValueError, match="configuration drift"):
        validate_reranker_config(changed)


def test_receipt_creation_is_exclusive(tmp_path):
    path = tmp_path / "receipt.json"
    write_receipt(path, {"status": "passed"})
    assert json.loads(path.read_text("utf8"))["status"] == "passed"
    with pytest.raises(FileExistsError):
        write_receipt(path, {"status": "passed"})
