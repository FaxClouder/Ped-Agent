"""Independently recompute saved E1 R1 and R4 retrieval outputs offline."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import sqlite3
import time

from runtime import ROOT, cache_identity, load_queries, model_assets, sha, verify_index


CONFIG_PATH = ROOT / "experiments/pearl-index-106-adobe-20260929/reranker-config.json"
CONFIGURATION_IDS = tuple(
    [f"{chunker}-L{length}-O0-M0" for chunker in ("C1", "C2", "C3", "C4") for length in (256, 384, 512)]
    + ["B0-regex320-overlap48-M0"]
)
QUERY_COUNT = 80
DEPTH = 100
R1_SCORE_ABS_TOLERANCE = 1e-12
R4_SCORE_ABS_TOLERANCE = 1e-6

PINNED_RERANKER_CONFIG = {
    "model_id": "BAAI/bge-reranker-v2-m3",
    "revision": "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e",
    "local_model_dir": "memPed/knowledge/models/bge-reranker-v2-m3",
    "verified_files_sha256": {
        "model.safetensors": "d9e3e081faff1eefb84019509b2f5558fd74c1a05a2c7db22f74174fcedb5286",
        "config.json": "13dcd6c31d9fec9d1d8e158702072f62d7fa7d312a64b9fe057bec9a08cfe41a",
        "tokenizer.json": "69564b696052886ed0ac63fa393e928384e0f8caada38c1f4864a9bfbf379c15",
        "tokenizer_config.json": "7e4c1cc848840aeccdd763458c18dd525eb0f795c992e00ebe9c28554e7db2d4",
        "special_tokens_map.json": "8c785abebea9ae3257b61681b4e6fd8365ceafde980c21970d001e834cf10835",
        "sentencepiece.bpe.model": "cfc8146abe2a0488e9e2a0c56de7952f7c11ab059eca145a0a727afce0db2865",
    },
    "device": "cuda:0",
    "use_fp16": True,
    "batch_size": 4,
    "query_max_length": 768,
    "max_length": 1024,
    "normalize": False,
    "query_instruction": None,
    "passage_instruction": None,
    "seed": 20260929,
    "score_order": "raw_logit_descending_then_chunk_id_ascending",
    "input_candidates": "frozen_R3_Top100_only",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf8"))


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines() if line.strip()]


def write_receipt(path: Path, value: dict) -> None:
    with Path(path).open("x", encoding="utf8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")


def validate_reranker_config(config: dict) -> None:
    if config != PINNED_RERANKER_CONFIG:
        raise ValueError("reranker configuration drift from the frozen E1 protocol")


def sparse_query(path: Path, query: str, limit: int = DEPTH) -> list[dict]:
    """Reopen SQLite read-only and reproduce the frozen build.py R1 query."""
    from ped_knowledge.tokenization import EnglishLexicalAnalyzer

    analyzer = EnglishLexicalAnalyzer()
    tokens = sorted(set(analyzer.analyze(query)))
    if not tokens:
        return []
    match = " OR ".join('"' + token + '"' for token in tokens)
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        fingerprint = connection.execute(
            "SELECT value FROM index_metadata WHERE key='lexical_analyzer_fingerprint'"
        ).fetchone()
        if fingerprint is None or fingerprint[0] != analyzer.fingerprint:
            raise ValueError("lexical analyzer fingerprint mismatch")
        rows = connection.execute(
            """SELECT chunk_id,
                      bm25(documents, 0, 0, 0, 0, 0, 1, 0) AS score_rank
                 FROM documents
                WHERE body MATCH ?
                ORDER BY score_rank ASC, chunk_id ASC
                LIMIT ?""",
            (match, limit),
        ).fetchall()
    return [
        {"chunk_id": chunk_id, "score": -float(score_rank), "rank": rank}
        for rank, (chunk_id, score_rank) in enumerate(rows, 1)
    ]


def compare_ranked_scores(
    label: str,
    saved: list[dict],
    fresh: list[dict],
    *,
    expected_count: int = DEPTH,
    abs_tolerance: float,
    exact_fields: tuple[str, ...] = (),
) -> None:
    if len(saved) != expected_count or len(fresh) != expected_count:
        raise ValueError(f"{label} result count drift")
    saved_ids = [row.get("chunk_id") for row in saved]
    fresh_ids = [row.get("chunk_id") for row in fresh]
    if len(set(saved_ids)) != expected_count or len(set(fresh_ids)) != expected_count:
        raise ValueError(f"{label} duplicate candidate")
    if saved_ids != fresh_ids:
        raise ValueError(f"{label} exact candidate order drift")
    expected_ranks = list(range(1, expected_count + 1))
    if [row.get("rank") for row in saved] != expected_ranks or [row.get("rank") for row in fresh] != expected_ranks:
        raise ValueError(f"{label} rank numbering drift")
    for field in exact_fields:
        if [row.get(field) for row in saved] != [row.get(field) for row in fresh]:
            raise ValueError(f"{label} exact {field} drift")
    for saved_row, fresh_row in zip(saved, fresh, strict=True):
        saved_score = float(saved_row.get("score", math.nan))
        fresh_score = float(fresh_row.get("score", math.nan))
        if not math.isfinite(saved_score) or not math.isfinite(fresh_score):
            raise ValueError(f"{label} nonfinite score")
        if not math.isclose(saved_score, fresh_score, rel_tol=0.0, abs_tol=abs_tolerance):
            raise ValueError(
                f"{label} score drift for {saved_row['chunk_id']}: "
                f"saved={saved_score!r}, fresh={fresh_score!r}, abs_tolerance={abs_tolerance}"
            )


def rerank_results(original: list[dict], scores: list[float]) -> list[dict]:
    if len(scores) != len(original) or any(not math.isfinite(float(score)) for score in scores):
        raise ValueError("R4 scores must be finite and one-to-one with R3 candidates")
    if len({row["chunk_id"] for row in original}) != len(original):
        raise ValueError("duplicate R3 candidate IDs")
    ranked = [
        dict(row, score=float(score), r3_rank=row["rank"])
        for row, score in zip(original, scores, strict=True)
    ]
    ranked.sort(key=lambda row: (-row["score"], row["chunk_id"]))
    for rank, row in enumerate(ranked, 1):
        row["rank"] = rank
    return ranked


@contextmanager
def capture_forward_inputs(model):
    class CapturedInputs(list):
        hook_seconds = 0.0

    actual = CapturedInputs()

    def hook(_model, args, kwargs):
        started = time.perf_counter()
        inputs = args[0] if args and hasattr(args[0], "keys") else kwargs
        token_rows = inputs["input_ids"].detach().cpu().tolist()
        mask_rows = inputs["attention_mask"].detach().cpu().tolist()
        actual.extend(
            [token for token, keep in zip(tokens, mask, strict=True) if keep]
            for tokens, mask in zip(token_rows, mask_rows, strict=True)
        )
        actual.hook_seconds += time.perf_counter() - started

    handle = model.register_forward_pre_hook(hook, with_kwargs=True)
    try:
        yield actual
    finally:
        handle.remove()


def assert_actual_inputs(expected: list[list[int]], actual: list[list[int]]) -> None:
    # FlagEmbedding performs an adaptive batch-size probe before the scoring pass.
    required = Counter(map(tuple, expected))
    seen = Counter(map(tuple, actual))
    if set(required) != set(seen) or any(seen[key] < count for key, count in required.items()):
        raise ValueError("actual model input differs from complete untruncated audited tokens")


def audit_inputs(tokenizer, query: str, rows: list[dict], config: dict) -> list[dict]:
    from FlagEmbedding.utils.tokenizer_compat import prepare_for_model_compat

    query_raw = tokenizer(query, add_special_tokens=False)["input_ids"]
    query_used = query_raw[: config["query_max_length"]]
    special_count = tokenizer.num_special_tokens_to_add(pair=True)
    audits = []
    for row in rows:
        passage_raw = tokenizer(row["text"], add_special_tokens=False)["input_ids"]
        passage_used = passage_raw[: config["max_length"]]
        pair = prepare_for_model_compat(
            tokenizer,
            query_used,
            passage_used,
            truncation="only_second",
            max_length=config["max_length"],
            padding=False,
        )
        audits.append(
            {
                "chunk_id": row["chunk_id"],
                "query_truncated": len(query_raw) > len(query_used),
                "child_truncated_initial": len(passage_raw) > len(passage_used),
                "child_truncated_pair": len(query_used) + len(passage_used) + special_count > config["max_length"],
                "model_input_ids": pair["input_ids"],
            }
        )
    return audits


def _validate_candidate_library(
    rows: list[dict],
    children: dict[str, dict],
    label: str,
    *,
    expected_count: int = DEPTH,
) -> None:
    if not 0 <= expected_count <= DEPTH:
        raise ValueError(f"{label} expected count outside retrieval depth")
    if len(rows) != expected_count or [row.get("rank") for row in rows] != list(range(1, expected_count + 1)):
        raise ValueError(f"{label} count/rank drift")
    if len({row.get("chunk_id") for row in rows}) != expected_count:
        raise ValueError(f"{label} duplicate candidate")
    for row in rows:
        child = children.get(row["chunk_id"])
        if child is None:
            raise ValueError(f"{label} candidate absent from child library")
        if row.get("text") != child.get("text") or row.get("text_sha256") != child.get("text_sha256"):
            raise ValueError(f"{label} candidate text/library drift")


def verify_r1_result(
    saved: list[dict],
    fresh: list[dict],
    children: dict[str, dict],
    label: str,
) -> int:
    """Verify a legal R1 result list whose cardinality may range from zero to depth."""
    if len(fresh) > DEPTH:
        raise ValueError(f"{label} fresh R1 result count exceeds retrieval depth")
    _validate_candidate_library(saved, children, label, expected_count=len(fresh))
    compare_ranked_scores(
        label,
        saved,
        fresh,
        expected_count=len(fresh),
        abs_tolerance=R1_SCORE_ABS_TOLERANCE,
    )
    return len(fresh)


def _load_configuration(output: Path, configuration_id: str, queries: list[dict], assets: dict) -> tuple[Path, dict, list[dict], dict[str, dict]]:
    from ped_knowledge.tokenization import EnglishLexicalAnalyzer

    directory = output / f"index-{configuration_id}"
    required = (
        "manifest.json",
        "child_chunks.jsonl",
        "fts.sqlite3",
        "rankings.jsonl",
        "retrieval-cost.json",
    )
    missing = [name for name in required if not (directory / name).is_file()]
    if missing:
        raise ValueError(f"{configuration_id} incomplete retrieval outputs: {missing}")
    verify_index(directory / "manifest.json")
    manifest = read_json(directory / "manifest.json")
    identity = manifest.get("configuration", {})
    if identity.get("policy") != configuration_id:
        raise ValueError(f"{configuration_id} manifest policy drift")
    if identity.get("lexical") != EnglishLexicalAnalyzer().fingerprint:
        raise ValueError(f"{configuration_id} manifest lexical analyzer drift")
    if identity.get("models") != assets:
        raise ValueError(f"{configuration_id} manifest model asset drift")
    expected_retrieval = {"depth": DEPTH, "RRF_k": 60, "dense": "exact_float32_dot", "seed": 20260929}
    if identity.get("retrieval") != expected_retrieval:
        raise ValueError(f"{configuration_id} manifest retrieval protocol drift")

    rankings = read_rows(directory / "rankings.jsonl")
    if len(rankings) != QUERY_COUNT or len({row.get("intent_id") for row in rankings}) != QUERY_COUNT:
        raise ValueError(f"{configuration_id} ranking intent cardinality drift")
    query_by_id = {row["intent_id"]: row for row in queries}
    if set(query_by_id) != {row["intent_id"] for row in rankings}:
        raise ValueError(f"{configuration_id} ranking/query identity drift")
    index_hash = sha(directory / "manifest.json")
    source_hash = sha(output / "source-views-prepared.json")
    parent_hash = sha(output / "public-parent-graph.json")
    for row in rankings:
        query = query_by_id[row["intent_id"]]
        expected_bindings = {
            "configuration_id": configuration_id,
            "index_sha256": index_hash,
            "query_sha256": cache_identity(query),
            "source_sha256": source_hash,
            "parent_sha256": parent_hash,
        }
        if row.get("status") != "success" or any(row.get(key) != value for key, value in expected_bindings.items()):
            raise ValueError(f"{configuration_id}/{row['intent_id']} failed or has provenance drift")
        if set(row.get("results", {})) != {"R1", "R2", "R3", "R4"}:
            raise ValueError(f"{configuration_id}/{row['intent_id']} method set drift")

    retrieval_cost = read_json(directory / "retrieval-cost.json")
    if retrieval_cost.get("rankings_sha256") != sha(directory / "rankings.jsonl"):
        raise ValueError(f"{configuration_id} rankings/retrieval-cost drift")
    if retrieval_cost.get("queries_sha256") != sha(output / "queries.jsonl"):
        raise ValueError(f"{configuration_id} queries/retrieval-cost drift")
    if retrieval_cost.get("failed_intents") or retrieval_cost.get("queries") != QUERY_COUNT:
        raise ValueError(f"{configuration_id} retrieval cost records failures or wrong query count")

    child_rows = read_rows(directory / "child_chunks.jsonl")
    children = {row["chunk_id"]: row for row in child_rows}
    if len(children) != len(child_rows):
        raise ValueError(f"{configuration_id} duplicate child IDs")
    for child in child_rows:
        if sha_text(child.get("text", "")) != child.get("text_sha256"):
            raise ValueError(f"{configuration_id} child text hash drift")
    return directory, manifest, rankings, children


def sha_text(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf8")).hexdigest()


def verify_sparse_configuration(output: Path, configuration_id: str, queries: list[dict], assets: dict) -> dict:
    started = time.perf_counter()
    directory, _manifest, rankings, children = _load_configuration(output, configuration_id, queries, assets)
    query_by_id = {row["intent_id"]: row["query"] for row in queries}
    comparisons = []
    results_compared = 0
    for row in rankings:
        intent_id = row["intent_id"]
        saved = row["results"]["R1"]
        fresh = sparse_query(directory / "fts.sqlite3", query_by_id[intent_id], DEPTH)
        results_compared += verify_r1_result(
            saved, fresh, children, f"{configuration_id}/{intent_id}/R1"
        )
        comparisons.append(
            {
                "intent_id": intent_id,
                "order_sha256": cache_identity([candidate["chunk_id"] for candidate in fresh]),
                "fresh_scores_sha256": cache_identity([candidate["score"] for candidate in fresh]),
            }
        )
    return {
        "status": "passed",
        "queries": len(rankings),
        "results_compared": results_compared,
        "seconds": time.perf_counter() - started,
        "comparison_sha256": cache_identity(comparisons),
        "fts_sqlite_sha256": sha(directory / "fts.sqlite3"),
        "rankings_sha256": sha(directory / "rankings.jsonl"),
        "manifest_sha256": sha(directory / "manifest.json"),
        "child_chunks_sha256": sha(directory / "child_chunks.jsonl"),
    }


def _load_reranker(config: dict):
    import numpy as np
    import torch
    from FlagEmbedding import FlagReranker

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; the pinned R4 verifier requires cuda:0")
    random.seed(config["seed"])
    np.random.seed(config["seed"])
    torch.manual_seed(config["seed"])
    torch.cuda.manual_seed_all(config["seed"])
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    started = time.perf_counter()
    model = FlagReranker(
        str(ROOT / config["local_model_dir"]),
        devices=config["device"],
        use_fp16=config["use_fp16"],
        batch_size=config["batch_size"],
        query_max_length=config["query_max_length"],
        max_length=config["max_length"],
        normalize=config["normalize"],
    )
    torch.cuda.synchronize()
    return model, torch, time.perf_counter() - started


def verify_reranker_configuration(
    output: Path,
    configuration_id: str,
    queries: list[dict],
    assets: dict,
    model,
    torch,
    config: dict,
) -> dict:
    started = time.perf_counter()
    directory, _manifest, rankings, children = _load_configuration(output, configuration_id, queries, assets)
    query_by_id = {row["intent_id"]: row["query"] for row in queries}
    input_audit_seconds = inference_seconds = inference_gross_seconds = 0.0
    capture_seconds = validation_seconds = 0.0
    comparisons = []
    for row in rankings:
        intent_id = row["intent_id"]
        r3 = row["results"]["R3"]
        saved_r4 = row["results"]["R4"]
        _validate_candidate_library(r3, children, f"{configuration_id}/{intent_id}/R3")
        _validate_candidate_library(saved_r4, children, f"{configuration_id}/{intent_id}/R4")
        if {candidate["chunk_id"] for candidate in r3} != {candidate["chunk_id"] for candidate in saved_r4}:
            raise ValueError(f"{configuration_id}/{intent_id} R3/R4 candidate set drift")

        audit_started = time.perf_counter()
        audited = audit_inputs(model.tokenizer, query_by_id[intent_id], r3, config)
        input_audit_seconds += time.perf_counter() - audit_started
        if any(
            item["query_truncated"] or item["child_truncated_initial"] or item["child_truncated_pair"]
            for item in audited
        ):
            raise ValueError(f"{configuration_id}/{intent_id} R4 input would be truncated")
        expected_inputs = [item["model_input_ids"] for item in audited]
        pairs = [[query_by_id[intent_id], candidate["text"]] for candidate in r3]

        torch.cuda.synchronize()
        inference_started = time.perf_counter()
        with capture_forward_inputs(model.model) as actual_inputs:
            scores = model.compute_score(
                pairs,
                batch_size=config["batch_size"],
                query_max_length=config["query_max_length"],
                max_length=config["max_length"],
                normalize=config["normalize"],
            )
        torch.cuda.synchronize()
        gross = time.perf_counter() - inference_started
        inference_gross_seconds += gross
        capture_seconds += actual_inputs.hook_seconds
        inference_seconds += max(0.0, gross - actual_inputs.hook_seconds)

        validation_started = time.perf_counter()
        assert_actual_inputs(expected_inputs, actual_inputs)
        fresh_scores_in_r3_order = [float(score) for score in scores]
        fresh_r4 = rerank_results(r3, fresh_scores_in_r3_order)
        compare_ranked_scores(
            f"{configuration_id}/{intent_id}/R4",
            saved_r4,
            fresh_r4,
            expected_count=DEPTH,
            abs_tolerance=R4_SCORE_ABS_TOLERANCE,
            exact_fields=("r3_rank",),
        )
        score_deltas = [
            abs(float(saved["score"]) - float(fresh["score"]))
            for saved, fresh in zip(saved_r4, fresh_r4, strict=True)
        ]
        validation_seconds += time.perf_counter() - validation_started
        audited_input_tokens = sum(len(item) for item in expected_inputs)
        actual_forward_tokens = sum(len(item) for item in actual_inputs)
        comparisons.append(
            {
                "intent_id": intent_id,
                "candidate_count": len(r3),
                "r3_candidate_ids_in_input_order": [candidate["chunk_id"] for candidate in r3],
                "fresh_r4_scores_in_r3_input_order": fresh_scores_in_r3_order,
                "expected_inputs_sha256": cache_identity(expected_inputs),
                "actual_forward_calls_tokens_sha256": cache_identity(actual_inputs),
                "actual_forward_call_count": len(actual_inputs),
                "audited_pair_input_tokens": audited_input_tokens,
                "actual_forward_tokens_including_probe_repetitions": actual_forward_tokens,
                "adaptive_probe_repeat_forward_calls": len(actual_inputs) - len(expected_inputs),
                "adaptive_probe_repeat_tokens": actual_forward_tokens - audited_input_tokens,
                "maximum_model_input_tokens": max(map(len, expected_inputs)),
                "maximum_absolute_score_delta": max(score_deltas),
                "fresh_order_sha256": cache_identity([candidate["chunk_id"] for candidate in fresh_r4]),
                "fresh_scores_sha256": cache_identity([candidate["score"] for candidate in fresh_r4]),
                "saved_scores_sha256": cache_identity([candidate["score"] for candidate in saved_r4]),
            }
        )
    return {
        "status": "passed",
        "queries": len(rankings),
        "pairs_compared": len(rankings) * DEPTH,
        "actual_forward_inputs": comparisons,
        "actual_forward_inputs_sha256": cache_identity(comparisons),
        "audited_pair_input_tokens": sum(item["audited_pair_input_tokens"] for item in comparisons),
        "actual_forward_call_count": sum(item["actual_forward_call_count"] for item in comparisons),
        "actual_forward_tokens_including_probe_repetitions": sum(
            item["actual_forward_tokens_including_probe_repetitions"] for item in comparisons
        ),
        "adaptive_probe_repeat_forward_calls": sum(
            item["adaptive_probe_repeat_forward_calls"] for item in comparisons
        ),
        "adaptive_probe_repeat_tokens": sum(item["adaptive_probe_repeat_tokens"] for item in comparisons),
        "maximum_absolute_score_delta": max(item["maximum_absolute_score_delta"] for item in comparisons),
        "cost": {
            "wall_seconds": time.perf_counter() - started,
            "input_audit_seconds": input_audit_seconds,
            "reranker_seconds": inference_seconds,
            "reranker_gross_seconds": inference_gross_seconds,
            "input_capture_seconds": capture_seconds,
            "validation_seconds": validation_seconds,
        },
    }


def run(output: Path, receipt: Path) -> dict:
    if not output.is_dir():
        raise ValueError("output must be an existing E1 output directory")
    if receipt.exists():
        raise FileExistsError(f"refusing to overwrite verification receipt: {receipt}")
    if not (output / "queries.jsonl").is_file():
        raise ValueError("missing receipt-bound E1 queries.jsonl")
    missing_configs = [configuration_id for configuration_id in CONFIGURATION_IDS if not (output / f"index-{configuration_id}").is_dir()]
    if missing_configs:
        raise ValueError(f"incomplete 13-configuration E1 matrix: {missing_configs}")

    started_wall = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    config = read_json(CONFIG_PATH)
    validate_reranker_config(config)
    assets = model_assets()
    queries = load_queries(output / "queries.jsonl", QUERY_COUNT)
    summaries = {configuration_id: {"configuration_id": configuration_id} for configuration_id in CONFIGURATION_IDS}

    for position, configuration_id in enumerate(CONFIGURATION_IDS, 1):
        print(f"[{position}/{len(CONFIGURATION_IDS)}] {configuration_id}: verifying R1", flush=True)
        summaries[configuration_id]["R1"] = verify_sparse_configuration(output, configuration_id, queries, assets)
        print(f"[{position}/{len(CONFIGURATION_IDS)}] {configuration_id}: R1 passed", flush=True)

    model, torch, model_load_seconds = _load_reranker(config)
    for position, configuration_id in enumerate(CONFIGURATION_IDS, 1):
        print(f"[{position}/{len(CONFIGURATION_IDS)}] {configuration_id}: recomputing R4", flush=True)
        summaries[configuration_id]["R4"] = verify_reranker_configuration(
            output, configuration_id, queries, assets, model, torch, config
        )
        print(f"[{position}/{len(CONFIGURATION_IDS)}] {configuration_id}: R4 passed", flush=True)

    finished_at = datetime.now(timezone.utc).isoformat()
    receipt_value = {
        "schema_version": "e1-independent-retrieval-verification-v1",
        "status": "passed",
        "created_at_utc": started_at,
        "finished_at_utc": finished_at,
        "output_directory": str(output),
        "scope": "Independent offline recomputation of saved R1 BM25 and R4 cross-encoder results for 13 configurations x 80 query-only intents; no Gold, historical scores, generation, remote calls, or dense model load.",
        "protocol": {
            "R1": {
                "analyzer": "EnglishLexicalAnalyzer",
                "query": "sorted unique analyzed tokens joined with OR",
                "sqlite": "read-only; body MATCH; bm25(documents,0,0,0,0,0,1,0)",
                "ordering": "score_rank ASC, chunk_id ASC",
                "score_absolute_tolerance": R1_SCORE_ABS_TOLERANCE,
                "exact_candidate_order_required": True,
            },
            "R4": {
                "input_candidates": "saved R3 Top100 only",
                "actual_forward_inputs_captured": True,
                "actual_forward_inputs_must_include_every_audited_untruncated_pair": True,
                "ordering": "raw score descending, chunk_id ascending",
                "score_absolute_tolerance": R4_SCORE_ABS_TOLERANCE,
                "exact_candidate_order_required": True,
                "config": config,
            },
        },
        "provenance": {
            "queries_sha256": sha(output / "queries.jsonl"),
            "source_views_sha256": sha(output / "source-views-prepared.json"),
            "public_parent_graph_sha256": sha(output / "public-parent-graph.json"),
            "reranker_config_sha256": sha(CONFIG_PATH),
            "model_assets": assets,
            "model_assets_sha256": cache_identity(assets),
            "verifier_code_sha256": sha(Path(__file__)),
            "historical_scores_loaded": False,
            "gold_loaded": False,
            "dense_model_loaded": False,
        },
        "environment": {
            "python": os.sys.version,
            "sqlite": sqlite3.sqlite_version,
            "torch": torch.__version__,
            "FlagEmbedding": importlib.metadata.version("FlagEmbedding"),
            "transformers": importlib.metadata.version("transformers"),
            "tokenizers": importlib.metadata.version("tokenizers"),
            "cuda_device": torch.cuda.get_device_name(0),
            "deterministic_algorithms": True,
            "tf32": False,
        },
        "configurations": [summaries[configuration_id] for configuration_id in CONFIGURATION_IDS],
        "totals": {
            "configurations": len(CONFIGURATION_IDS),
            "query_intents_per_configuration": QUERY_COUNT,
            "R1_results_compared": sum(summary["R1"]["results_compared"] for summary in summaries.values()),
            "R4_pairs_recomputed": sum(summary["R4"]["pairs_compared"] for summary in summaries.values()),
            "R4_actual_forward_tokens_including_probe_repetitions": sum(
                summary["R4"]["actual_forward_tokens_including_probe_repetitions"]
                for summary in summaries.values()
            ),
            "R4_adaptive_probe_repeat_forward_calls": sum(
                summary["R4"]["adaptive_probe_repeat_forward_calls"] for summary in summaries.values()
            ),
            "R4_adaptive_probe_repeat_tokens": sum(
                summary["R4"]["adaptive_probe_repeat_tokens"] for summary in summaries.values()
            ),
            "R4_maximum_absolute_score_delta": max(
                summary["R4"]["maximum_absolute_score_delta"] for summary in summaries.values()
            ),
        },
        "cost": {
            "wall_seconds": time.perf_counter() - started_wall,
            "reranker_model_load_seconds": model_load_seconds,
            "generation_calls": 0,
            "remote_calls": 0,
            "dense_model_loads": 0,
        },
    }
    write_receipt(receipt, receipt_value)
    return receipt_value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="existing complete E1 output directory")
    parser.add_argument("--receipt", type=Path, required=True, help="new receipt JSON path; overwrite is refused")
    args = parser.parse_args()
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_DATASETS_OFFLINE"):
        os.environ[name] = "1"
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    result = run(args.output.resolve(), args.receipt.resolve())
    print(json.dumps({"status": result["status"], "receipt": str(args.receipt.resolve())}), flush=True)


if __name__ == "__main__":
    main()
