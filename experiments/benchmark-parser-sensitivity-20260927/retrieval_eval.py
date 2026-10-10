"""P2 step 4: isolated parser-swap indexes and development retrieval comparison.

Arms (104-resource corpus, parent-child-v1, regex-token-v1, base jieba, BGE-M3):
  catalog_mixed        102 Adobe (saved real responses) + 2 PyMuPDF; must equal the V1 Catalog
  pymupdf_all          PyMuPDF for all 104 resources
  pymupdf_dev_targets  PyMuPDF only for the dev evidence resources that have an Adobe parse

Only the parser changes. Every unique chunk text is embedded once, so shared chunks get
bit-identical vectors in all arms. Writes only to a new output directory; no Adobe call.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

from ped_knowledge.evaluation.gold_v2 import score_answerable
from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex, embedding_fingerprint

from p2_common import (
    ADJUDICATED, ANCHORS, MANIFEST, MODEL_DIR, POLICY, ROOT, TOKENIZER, V1_DEV_RUN, V1_REPORT,
    active_versions, bootstrap_mean_ci, child_rows, chunk_fingerprint, code_provenance,
    exact_binomial_two_sided, group_text_rank, guard_output, library_versions, load_anchors,
    parse_catalog_backend, parse_pymupdf, read_jsonl, saved_adobe_zip, sha256, verify_corpus,
)

sys.path.insert(0, str(ROOT / "experiments/benchmark-gold-20260923"))
from compare_lexical_candidate import fuse_rrf  # noqa: E402
from dev_scope import load_dev_scope  # noqa: E402

K = 5
RECALL_LIMIT = 40
RRF_K = 60
METHODS = ("bm25", "bge_m3", "rrf")
ARMS = ("catalog_mixed", "pymupdf_all", "pymupdf_dev_targets")
BASELINE = "catalog_mixed"
MODEL_ID = "BAAI/bge-m3"
BOOTSTRAP_SEED = 20260927


class CachedGateway:
    """Serves precomputed vectors; unknown texts are a hard error, never silently embedded."""

    def __init__(self, vectors: dict[str, list[float]]) -> None:
        self.vectors = vectors

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self.vectors[_text_key(text)] for text in texts]


def _text_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embed_unique(texts: list[str]) -> tuple[dict[str, list[float]], float]:
    from FlagEmbedding import BGEM3FlagModel

    keys = sorted({_text_key(text): text for text in texts}.items())
    model = BGEM3FlagModel(str(MODEL_DIR), devices="cuda:0", use_fp16=True)
    start = time.perf_counter()
    vectors = model.encode([text for _, text in keys], batch_size=8, max_length=1024,
                           return_dense=True, return_sparse=False, return_colbert_vecs=False)["dense_vecs"]
    elapsed = time.perf_counter() - start
    return {key: vector.tolist() for (key, _), vector in zip(keys, vectors, strict=True)}, elapsed


def parse_corpus(versions: dict[str, dict], targets: set[str]) -> tuple[dict, dict[str, str], list[dict]]:
    """Return per-arm child rows, parent texts for every parse, and parse provenance."""
    per_resource: dict[str, dict] = {}
    parents: dict[str, str] = {}
    log = []
    for resource, version in versions.items():
        start = time.perf_counter()
        catalog_doc, _ = parse_catalog_backend(version)
        catalog_ms = (time.perf_counter() - start) * 1000
        if version["catalog_parser_version"].startswith("pymupdf-"):
            local_doc, local_ms = catalog_doc, catalog_ms
        else:
            start = time.perf_counter()
            local_doc, _ = parse_pymupdf(version)
            local_ms = (time.perf_counter() - start) * 1000
        per_resource[resource] = {}
        for name, document in (("catalog", catalog_doc), ("pymupdf", local_doc)):
            children, parent_rows = child_rows(document, version["title"])
            per_resource[resource][name] = children
            parents.update({key: row["text"] for key, row in parent_rows.items()})
        zip_path = saved_adobe_zip(version)
        log.append({
            "resource_id": resource, "source_pdf_sha256": version["version_id"],
            "catalog_parser_version": version["catalog_parser_version"],
            "adobe_response_sha256": sha256(zip_path) if zip_path else None,
            "dev_target_swapped": resource in targets,
            "catalog_parse_ms": round(catalog_ms, 1), "pymupdf_parse_ms": round(local_ms, 1),
            "catalog_child_chunks": len(per_resource[resource]["catalog"]),
            "pymupdf_child_chunks": len(per_resource[resource]["pymupdf"]),
        })
        print(f"parsed {resource}", flush=True)
    arms = {
        "catalog_mixed": [row for item in per_resource.values() for row in item["catalog"]],
        "pymupdf_all": [row for item in per_resource.values() for row in item["pymupdf"]],
        "pymupdf_dev_targets": [
            row for resource, item in per_resource.items()
            for row in item["pymupdf" if resource in targets else "catalog"]],
    }
    return arms, parents, log


def text_locator_metrics(anchor_intent: dict, ranking: list[dict], parents: dict[str, str]) -> dict:
    """Parser-neutral locator: Gold page plus verbatim anchor text, scored in the k-resource scope."""
    selected: list[str] = []
    for row in ranking:
        if row["resource_id"] not in selected:
            selected.append(row["resource_id"])
            if len(selected) == K:
                break
    scope = [row for row in ranking if row["resource_id"] in selected]
    resource = anchor_intent["resource_id"]
    child_hits = [group_text_rank(group, scope, resource_id=resource) for group in anchor_intent["groups"]]
    parent_hits = [group_text_rank(group, scope, resource_id=resource,
                                   text_of=lambda row: parents[row["parent_chunk_id"]])
                   for group in anchor_intent["groups"]]
    evidence_ranks = [group_text_rank(group, ranking, resource_id=resource) for group in anchor_intent["groups"]]
    page_hits = [next((row for row in scope if row["resource_id"] == resource
                       and row["page_start"] <= group["pdf_page_1based"] <= row["page_end"]), None)
                 for group in anchor_intent["groups"]]
    spans = [row["page_end"] - row["page_start"] + 1 for row in page_hits if row is not None]
    split_ok = [all(any(group_text_rank({**group, "required": [anchor]}, [row], resource_id=resource)
                        for row in scope) for anchor in group["required"])
                for group in anchor_intent["groups"]]
    return {
        "text_locator_group_recall_at_5": sum(rank is not None for rank in child_hits) / len(child_hits),
        "complete_text_locator_at_5": float(all(rank is not None for rank in child_hits)),
        "complete_parent_text_locator_at_5": float(all(rank is not None for rank in parent_hits)),
        "complete_split_text_locator_at_5": float(all(split_ok)),
        "first_text_evidence_chunk_rank": max(evidence_ranks) if all(evidence_ranks) else None,
        "page_hit_chunk_mean_page_span": sum(spans) / len(spans) if spans else None,
    }


def aggregate(rows: list[dict]) -> dict:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[f"{row['arm']}/{row['method']}/{row['language']}"].append(row)
    output = {}
    for key, items in sorted(buckets.items()):
        metrics = {name: sum(item["metrics"][name] for item in items) / len(items)
                   for name in items[0]["metrics"]}
        for name in ("complete_text_locator_at_5", "complete_split_text_locator_at_5",
                     "complete_parent_text_locator_at_5", "text_locator_group_recall_at_5"):
            metrics[name] = sum(item["text_metrics"][name] for item in items) / len(items)
        ranks = [item["text_metrics"]["first_text_evidence_chunk_rank"] for item in items]
        metrics["text_evidence_mrr_top40"] = sum(1 / rank for rank in ranks if rank) / len(items)
        spans = [item["text_metrics"]["page_hit_chunk_mean_page_span"] for item in items
                 if item["text_metrics"]["page_hit_chunk_mean_page_span"] is not None]
        metrics["mean_page_span_of_page_hit_chunks"] = sum(spans) / len(spans) if spans else None
        output[key] = metrics
    return output


PAIRED_METRICS = ("complete_evidence_at_5", "complete_locator_at_5", "mrr", "ndcg_at_5",
                  "complete_text_locator_at_5", "complete_split_text_locator_at_5",
                  "complete_parent_text_locator_at_5")


def metric_value(row: dict, name: str) -> float:
    return row["metrics"][name] if name in row["metrics"] else row["text_metrics"][name]


def paired_tests(rows: list[dict]) -> list[dict]:
    """Arm minus baseline, with intent as the unit; languages reported separately and pooled."""
    index = {(row["arm"], row["method"], row["question_id"]): row for row in rows}
    intents = sorted({row["intent_id"] for row in rows})
    output = []
    for arm in ARMS[1:]:
        for method in METHODS:
            for metric in PAIRED_METRICS:
                for language in ("en", "zh", "both"):
                    languages = ("en", "zh") if language == "both" else (language,)
                    deltas, wins, losses = [], 0, 0
                    for intent in intents:
                        delta = sum(
                            metric_value(index[(arm, method, f"{intent}-{lang}")], metric)
                            - metric_value(index[(BASELINE, method, f"{intent}-{lang}")], metric)
                            for lang in languages) / len(languages)
                        deltas.append(delta)
                        wins += delta > 0
                        losses += delta < 0
                    low, high = bootstrap_mean_ci(deltas, seed=BOOTSTRAP_SEED)
                    output.append({
                        "arm": arm, "method": method, "metric": metric, "language": language,
                        "intents": len(intents), "mean_delta_vs_catalog_mixed": sum(deltas) / len(deltas),
                        "bootstrap95_low": low, "bootstrap95_high": high,
                        "intents_improved": wins, "intents_worsened": losses,
                        "sign_test_p_two_sided": exact_binomial_two_sided(wins, losses),
                    })
    return output


def reproduction_check(rows: list[dict]) -> dict:
    """Compare the rebuilt catalog_mixed arm with the saved 2026-09-24 V1 development run."""
    saved = {(row["method"], row["question_id"]): row for row in read_jsonl(V1_DEV_RUN / "per_query.jsonl")}
    result = {}
    for method in METHODS:
        mine = [row for row in rows if row["arm"] == BASELINE and row["method"] == method]
        same_list = sum([item["chunk_id"] for item in saved[(method, row["question_id"])]["chunk_ranking"]]
                        == [item["chunk_id"] for item in row["chunk_ranking"]] for row in mine)
        same_top5 = sum([item["resource_id"] for item in saved[(method, row["question_id"])]["ranking"]]
                        == row["selected_resources"] for row in mine)
        same_metrics = sum(saved[(method, row["question_id"])]["metrics"] == row["metrics"] for row in mine)
        result[method] = {"queries": len(mine), "identical_top40_chunk_lists": same_list,
                          "identical_top5_resources": same_top5, "identical_metrics": same_metrics}
    return result


async def run(output_dir: Path) -> dict:
    guard_output(output_dir)
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for configured BGE-M3 runs")
    versions = active_versions()
    verify_corpus(versions)
    v1 = json.loads(V1_REPORT.read_text(encoding="utf-8"))
    model_manifest = json.loads((MODEL_DIR / "model_manifest.json").read_text(encoding="utf-8"))
    weights_sha = sha256(MODEL_DIR / "pytorch_model.bin")
    if weights_sha != model_manifest["weights"]["pytorch_model.bin"]["sha256"] or weights_sha != v1["model_weights_sha256"]:
        raise ValueError("BGE-M3 weights differ from pinned manifest or V1 build")
    embedding_fp = embedding_fingerprint(model=MODEL_ID, base_url=None, dimensions=1024)
    if embedding_fp != v1["embedding_fingerprint"]:
        raise ValueError("embedding configuration differs from V1")
    questions, evidence = load_dev_scope()
    anchors = {item["intent_id"]: item for item in load_anchors()["intents"]}
    if len(questions) != 40 or set(evidence) != set(anchors):
        raise ValueError("development-only scope mismatch")
    targets = {item["resource_id"] for item in anchors.values() if saved_adobe_zip(versions[item["resource_id"]])}
    arms, parents, parse_log = parse_corpus(versions, targets)
    if chunk_fingerprint(arms[BASELINE]) != v1["catalog_fingerprint"]:
        raise ValueError("catalog_mixed arm does not reproduce the V1 Catalog chunks")
    all_texts = [row["text"] for rows in arms.values() for row in rows] + [q["query"] for q in questions]
    vectors, embed_seconds = embed_unique(all_texts)
    gateway = CachedGateway(vectors)
    output_dir.mkdir(parents=True)
    build = {}
    indexes = {}
    code = code_provenance()
    for arm, rows in arms.items():
        fingerprint = chunk_fingerprint(rows)
        arm_dir = output_dir / "indexes" / arm
        arm_dir.mkdir(parents=True)
        with (arm_dir / "child_chunks.jsonl").open("x", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        fts = FTSIndex(arm_dir / "fts.sqlite3")
        fts.rebuild(rows, source_fingerprint=fingerprint, policy_version=POLICY,
                    tokenizer_fingerprint=TOKENIZER, code_revision=code["git_head"])
        vector = ChromaVectorIndex(arm_dir / "chroma", gateway)
        await vector.rebuild(rows, catalog_fingerprint=fingerprint, embedding_fingerprint=embedding_fp,
                             policy_version=POLICY, tokenizer_fingerprint=TOKENIZER, embedding_max_length=1024,
                             lexical_analyzer_fingerprint=fts.lexical_analyzer_fingerprint(),
                             code_revision=code["git_head"])
        with sqlite3.connect(arm_dir / "fts.sqlite3") as db:
            fts_count = db.execute("SELECT count(*) FROM documents").fetchone()[0]
        if fts_count != len(rows) or vector._collection().count() != len(rows):
            raise RuntimeError(f"index count mismatch in {arm}")
        if fts.lexical_analyzer_fingerprint() != v1["lexical_analyzer_fingerprint"]:
            raise ValueError("lexical analyzer differs from V1")
        build[arm] = {"child_chunks": len(rows), "chunk_fingerprint": fingerprint,
                      "resources": len({row["resource_id"] for row in rows}),
                      "parser_versions": sorted({row["parser_version"] for row in rows}),
                      "fts_entries": fts_count, "chroma_entries": vector._collection().count(),
                      "child_chunks_sha256": sha256(arm_dir / "child_chunks.jsonl"),
                      "fts_sha256": sha256(arm_dir / "fts.sqlite3")}
        indexes[arm] = (fts, vector, {row["chunk_id"]: row for row in rows})
        print(f"indexed {arm}: {len(rows)} child chunks", flush=True)
    results = []
    for question in questions:
        for arm, (fts, vector, chunks) in indexes.items():
            sparse = [hit.chunk_id for hit in fts.search(question["query"], limit=RECALL_LIMIT)]
            dense = [hit.chunk_id for hit in await vector.search(question["query"], limit=RECALL_LIMIT)]
            for method, ids in (("bm25", sparse), ("bge_m3", dense), ("rrf", fuse_rrf(sparse, dense, rrf_k=RRF_K))):
                ranking = [chunks[chunk_id] for chunk_id in ids]
                selected = []
                for row in ranking:
                    if row["resource_id"] not in selected:
                        selected.append(row["resource_id"])
                results.append({
                    "arm": arm, "method": method, "question_id": question["question_id"],
                    "intent_id": question["intent_id"], "language": question["language"],
                    "topic": question["primary_topic"],
                    "metrics": score_answerable(evidence[question["intent_id"]], ranking, k=K),
                    "text_metrics": text_locator_metrics(anchors[question["intent_id"]], ranking, parents),
                    "selected_resources": selected[:K],
                    "gold_resource_rank": next((rank for rank, resource in enumerate(selected, 1)
                                                if resource == anchors[question["intent_id"]]["resource_id"]), None),
                    "chunk_ranking": [{"rank": rank, "chunk_id": row["chunk_id"], "resource_id": row["resource_id"],
                                       "version_id": row["version_id"], "page_start": row["page_start"],
                                       "page_end": row["page_end"], "parser_version": row["parser_version"]}
                                      for rank, row in enumerate(ranking, 1)],
                })
        print(f"evaluated {question['question_id']}", flush=True)
    with (output_dir / "per_query.jsonl").open("x", encoding="utf-8") as stream:
        for row in results:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    tests = paired_tests(results)
    with (output_dir / "paired_tests.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(tests[0]))
        writer.writeheader()
        writer.writerows(tests)
    with (output_dir / "parse_log.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(parse_log[0]))
        writer.writeheader()
        writer.writerows(parse_log)
    summary = {
        "status": "p2_parser_sensitivity_dev_candidate_labels_only",
        "human_verified": False, "test_split_evaluated": False, "refusal_evaluated": False,
        "adobe_api_called_in_this_run": False,
        "adobe_source": "saved real Adobe PDF Extract responses from the 2026-09-24 Catalog import (hash-checked)",
        "arms": {"catalog_mixed": "102 Adobe + 2 PyMuPDF (reproduces V1 Catalog chunks exactly)",
                 "pymupdf_all": "PyMuPDF for all 104; 102 resources differ from catalog_mixed",
                 "pymupdf_dev_targets": f"PyMuPDF for {len(targets)} dev evidence resources, catalog parse elsewhere"},
        "dev_target_resources": sorted(targets),
        "parser_constant_dev_resources": sorted({item["resource_id"] for item in anchors.values()} - targets),
        "independent_intents": 20, "query_variants": 40, "k": K, "recall_limit": RECALL_LIMIT, "rrf_k": RRF_K,
        "methods": list(METHODS), "cross_encoder": "not_run_no_pinned_local_model",
        "chunk_policy": POLICY, "tokenizer_fingerprint": TOKENIZER,
        "lexical_analyzer_fingerprint": v1["lexical_analyzer_fingerprint"],
        "embedding_fingerprint": embedding_fp, "model_id": MODEL_ID,
        "model_revision": model_manifest["revision"], "model_weights_sha256": weights_sha,
        "embedding_params": {"device": "cuda:0", "fp16": True, "batch_size": 8, "max_length": 1024,
                             "vector_reuse": "each unique text embedded once; shared chunks and queries identical across arms"},
        "unique_texts_embedded": len(vectors), "embedding_seconds": round(embed_seconds, 1),
        "cuda_device": torch.cuda.get_device_name(0),
        "random_seed": None, "bootstrap_seed": BOOTSTRAP_SEED,
        "build": build,
        "metrics_by_arm_method_language": aggregate(results),
        "reproduction_vs_saved_v1_dev_run": reproduction_check(results),
        "statistics_note": "20 intents, 12 PDFs; intent is the unit, bootstrap over intents and exact sign test on discordant intents. Low power; not a corpus-wide claim.",
        "source_sha256": {"core_manifest.jsonl": sha256(MANIFEST), "evidence_anchors_dev.json": sha256(ANCHORS),
                          "stage2_annotations.jsonl": sha256(ADJUDICATED), "v1_build_report.json": sha256(V1_REPORT),
                          "v1_dev_per_query.jsonl": sha256(V1_DEV_RUN / "per_query.jsonl")},
        "code_provenance": code, "library_versions": library_versions(),
        "command": f"python -u experiments/benchmark-parser-sensitivity-20260927/retrieval_eval.py --output-dir {output_dir.as_posix()}",
    }
    summary["output_sha256"] = {name: sha256(output_dir / name) for name in ("per_query.jsonl", "paired_tests.csv", "parse_log.csv")}
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = asyncio.run(run(args.output_dir))
    print(json.dumps({key: result[key] for key in ("status", "build", "reproduction_vs_saved_v1_dev_run")}, indent=2))
