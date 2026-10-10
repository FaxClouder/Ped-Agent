from p2_common import (
    bootstrap_mean_ci, chunk_fingerprint, exact_binomial_two_sided, group_text_rank, normalize,
    text_has_anchor,
)
from retrieval_eval import paired_tests, text_locator_metrics


def test_normalize_ignores_hyphenation_ligatures_and_spacing():
    assert normalize("ex-\necution  ﬁeld") == normalize("execution field")
    assert normalize("t-total 64.9%") == "ttotal64.9%"


def test_list_anchor_requires_all_parts():
    text = normalize("Table 3 Logistic ... 3.43* | (1.28–9.21)")
    assert text_has_anchor(text, ["table 3", "3.43", "1.28", "9.21"])
    assert not text_has_anchor(text, ["table 3", "4.40"])


def _row(chunk, resource, start, end, text, parent="p1"):
    return {"chunk_id": chunk, "resource_id": resource, "page_start": start, "page_end": end,
            "text": text, "parent_chunk_id": parent}


def test_group_text_rank_needs_gold_page_and_anchor():
    group = {"pdf_page_1based": 5, "required": ["odds ratio 3.43"]}
    ranking = [_row("a", "r", 1, 4, "odds ratio 3.43"), _row("b", "x", 5, 5, "odds ratio 3.43"),
               _row("c", "r", 5, 6, "Odds-ratio 3.43")]
    assert group_text_rank(group, ranking, resource_id="r") == 3


def test_text_locator_uses_k_resource_scope_and_parent_text():
    intent = {"resource_id": "r", "groups": [{"pdf_page_1based": 2, "required": ["needle"]}]}
    ranking = [_row(str(i), f"other{i}", 1, 1, "x") for i in range(5)] + [_row("h", "r", 2, 2, "needle")]
    outside = text_locator_metrics(intent, ranking, {"p1": "x"})
    assert outside["complete_text_locator_at_5"] == 0.0
    assert outside["first_text_evidence_chunk_rank"] == 6
    inside = text_locator_metrics(intent, [_row("h", "r", 2, 3, "x")], {"p1": "has needle"})
    assert inside["complete_text_locator_at_5"] == 0.0
    assert inside["complete_parent_text_locator_at_5"] == 1.0
    assert inside["page_hit_chunk_mean_page_span"] == 2
    two = {"resource_id": "r", "groups": [{"pdf_page_1based": 2, "required": ["alpha", "beta"]}]}
    split = text_locator_metrics(two, [_row("a", "r", 2, 2, "alpha"), _row("b", "r", 2, 2, "beta")], {"p1": ""})
    assert split["complete_text_locator_at_5"] == 0.0 and split["complete_split_text_locator_at_5"] == 1.0


def test_sign_test_and_bootstrap():
    assert exact_binomial_two_sided(0, 0) == 1.0
    assert round(exact_binomial_two_sided(0, 3), 4) == 0.25
    assert bootstrap_mean_ci([0.0, 0.0], seed=1) == (0.0, 0.0)


def test_chunk_fingerprint_is_order_independent():
    rows = [{"resource_id": "b", "ordinal": 0, "chunk_id": "b0", "text": "t"},
            {"resource_id": "a", "ordinal": 1, "chunk_id": "a1", "text": "u"}]
    assert chunk_fingerprint(rows) == chunk_fingerprint(list(reversed(rows)))


def test_paired_tests_pool_languages_by_intent():
    rows = []
    for arm, value in (("catalog_mixed", 1.0), ("pymupdf_all", 0.0), ("pymupdf_dev_targets", 1.0)):
        for method in ("bm25", "bge_m3", "rrf"):
            for language in ("en", "zh"):
                metrics = {name: value for name in ("complete_evidence_at_5", "complete_locator_at_5", "mrr", "ndcg_at_5")}
                text = {name: value for name in ("complete_text_locator_at_5", "complete_split_text_locator_at_5",
                                                 "complete_parent_text_locator_at_5")}
                rows.append({"arm": arm, "method": method, "intent_id": "i1", "language": language,
                             "question_id": f"i1-{language}", "metrics": metrics, "text_metrics": text})
    tests = {(t["arm"], t["method"], t["metric"], t["language"]): t for t in paired_tests(rows)}
    worse = tests[("pymupdf_all", "rrf", "mrr", "both")]
    assert worse["mean_delta_vs_catalog_mixed"] == -1.0 and worse["intents_worsened"] == 1
    assert tests[("pymupdf_dev_targets", "rrf", "mrr", "zh")]["intents_improved"] == 0
