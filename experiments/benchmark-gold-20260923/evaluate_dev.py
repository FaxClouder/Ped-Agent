"""Exploratory candidate retrieval evaluation on the proposed development split."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex
from ped_knowledge.evaluation.gold_v2 import score_answerable
from ped_knowledge.storage import Catalog


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
INDEX = ROOT / "outputs/knowledge-index-104-v1-20260924-01"
POLICY = "parent-child-v1"
K = 5
RECALL_LIMIT = 40
RRF_K = 60


def candidate_paths(version: str) -> tuple[Path, Path, Path]:
    if version not in {"v2", "v3", "v4", "v5"}:
        raise ValueError(f"Unsupported candidate version: {version}")
    return (
        GOLD / f"questions_full_candidate_{version}.jsonl",
        GOLD / f"evidence_planned_candidate_{version}.jsonl",
        GOLD / f"full_candidate_manifest_{version}.json",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def score_question(evidence: dict, ranking: list[dict], *, k: int = K) -> dict[str, float]:
    """Use the versioned Gold v2 scorer for this exploratory runner."""
    return score_answerable(evidence, ranking, k=k)


def _distinct_resources(hits: list, chunks: dict[str, dict], *, k: int = K) -> list[dict]:
    selected: list[dict] = []
    seen: set[str] = set()
    for hit in hits:
        row = chunks.get(hit.chunk_id)
        if row is None or row["resource_id"] in seen:
            continue
        seen.add(row["resource_id"])
        selected.append(row)
        if len(selected) == k:
            break
    return selected


def _chunk_ranking(hits: list, chunks: dict[str, dict]) -> list[dict]:
    """Retain all retrieved child chunks for exact evidence-page scoring."""
    return [chunks[hit.chunk_id] for hit in hits if hit.chunk_id in chunks]


def _serialize_chunk_ranking(ranking: list[dict]) -> list[dict]:
    return [
        {
            "rank": rank,
            "chunk_id": row["chunk_id"],
            "resource_id": row["resource_id"],
            "version_id": row["version_id"],
            "page_start": row["page_start"],
            "page_end": row["page_end"],
            "element_ids": list(row["element_ids"]),
        }
        for rank, row in enumerate(ranking, 1)
    ]


def _rrf(sparse: list, dense: list) -> list:
    from ped_knowledge.contracts import IndexHit

    scores: dict[str, float] = defaultdict(float)
    for hits in (sparse, dense):
        for rank, hit in enumerate(hits, 1):
            scores[hit.chunk_id] += 1 / (RRF_K + rank)
    return [
        IndexHit(chunk_id=chunk_id, score=score)
        for chunk_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    ]


def paired_differences(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Mean zh minus en metric difference, paired by independent intent."""
    pairs: dict[str, dict[str, dict[str, dict[str, float]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in rows:
        pairs[row["method"]][row["intent_id"]][row["language"]] = row["metrics"]
    results: dict[str, dict[str, float]] = {}
    for method, intents in pairs.items():
        if any(set(languages) != {"en", "zh"} for languages in intents.values()):
            raise ValueError("unpaired development query variants")
        metric_names = next(iter(intents.values()))["en"]
        results[method] = {
            name: sum(
                languages["zh"][name] - languages["en"][name]
                for languages in intents.values()
            ) / len(intents)
            for name in metric_names
        }
    return results


class BGEM3Gateway:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.model = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            from FlagEmbedding import BGEM3FlagModel

            self.model = BGEM3FlagModel(str(self.model_path), devices="cuda:0", use_fp16=True)
        vectors = self.model.encode(
            texts,
            batch_size=8,
            max_length=1024,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )["dense_vecs"]
        return vectors.tolist()


def _validate_snapshot(index_dir: Path, catalog: Catalog, fts: FTSIndex, vector: ChromaVectorIndex) -> dict:
    report = json.loads((index_dir / "build_report.json").read_text(encoding="utf-8"))
    current = catalog.official_fingerprint(policy_version=POLICY)
    if report["catalog_fingerprint"] != current:
        raise ValueError("Catalog differs from the frozen index build")
    if fts.source_fingerprint() != current or vector.catalog_fingerprint != current:
        raise ValueError("index fingerprints differ from Catalog")
    if fts.policy_version() != POLICY or vector.policy_version != POLICY:
        raise ValueError("index chunk policy mismatch")
    if fts.tokenizer_fingerprint() != report["tokenizer_fingerprint"]:
        raise ValueError("FTS tokenizer mismatch")
    if vector.tokenizer_fingerprint != report["tokenizer_fingerprint"]:
        raise ValueError("Chroma tokenizer mismatch")
    if fts.lexical_analyzer_fingerprint() != report["lexical_analyzer_fingerprint"]:
        raise ValueError("FTS lexical analyzer mismatch")
    if vector.embedding_fingerprint != report["embedding_fingerprint"]:
        raise ValueError("embedding fingerprint mismatch")
    return report


async def run(output_dir: Path, index_dir: Path, candidate_version: str = "v2") -> None:
    if output_dir.exists():
        raise FileExistsError(f"output directory already exists: {output_dir}")
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this configured BGE-M3 evaluation")
    catalog = Catalog(ROOT / "memPed/knowledge/knowledge.sqlite3")
    fts = FTSIndex(index_dir / "fts.sqlite3")
    vector = ChromaVectorIndex(
        index_dir / "chroma", BGEM3Gateway(ROOT / "memPed/knowledge/models/bge-m3")
    )
    index_report = _validate_snapshot(index_dir, catalog, fts, vector)
    chunks = {row["chunk_id"]: row for row in catalog.list_official_chunks(policy_version=POLICY)}
    questions_path, evidence_path, manifest_path = candidate_paths(candidate_version)
    candidate_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for path in (questions_path, evidence_path):
        if sha256(path) != candidate_manifest["output_sha256"][path.name]:
            raise ValueError(f"candidate Gold asset changed: {path.name}")
    questions = [
        q for q in read_jsonl(questions_path)
        if q.get("proposed_split") == "proposed_dev" and q.get("answerable") is True
    ]
    evidence = {e["intent_id"]: e for e in read_jsonl(evidence_path)}
    if len(questions) != 40 or len({q["intent_id"] for q in questions}) != 20:
        raise ValueError("expected 20 paired development intents")
    for question in questions:
        for group in evidence[question["intent_id"]]["evidence_groups"]:
            for alt in group["alternatives"]:
                if not any(
                    row["resource_id"] == alt["resource_id"]
                    and row["version_id"] == alt["source_pdf_sha256"]
                    for row in chunks.values()
                ):
                    raise ValueError("candidate evidence source absent from frozen index")
    output_dir.mkdir(parents=True)
    rows: list[dict] = []
    for number, question in enumerate(questions, 1):
        query = question["query"]
        sparse = fts.search(query, limit=RECALL_LIMIT)
        dense = await vector.search(query, limit=RECALL_LIMIT)
        for method, hits in (("bm25", sparse), ("bge_m3", dense), ("rrf", _rrf(sparse, dense))):
            ranking = _distinct_resources(hits, chunks)
            chunk_ranking = _chunk_ranking(hits, chunks)
            metrics = score_question(evidence[question["intent_id"]], chunk_ranking)
            rows.append({
                "question_id": question["question_id"],
                "intent_id": question["intent_id"],
                "language": question["language"],
                "topic": question.get("primary_topic"),
                "method": method,
                "ranking": [
                    {
                        "rank": rank,
                        "chunk_id": row["chunk_id"],
                        "resource_id": row["resource_id"],
                        "version_id": row["version_id"],
                        "page_start": row["page_start"],
                        "page_end": row["page_end"],
                    }
                    for rank, row in enumerate(ranking, 1)
                ],
                "chunk_ranking": _serialize_chunk_ranking(chunk_ranking),
                "metrics": metrics,
            })
        print(f"evaluated {number}/{len(questions)} {question['question_id']}", flush=True)
    (output_dir / "per_query.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8"
    )
    metric_names = tuple(rows[0]["metrics"])
    aggregate = {}
    for method in ("bm25", "bge_m3", "rrf"):
        for language in ("en", "zh"):
            selected = [row for row in rows if row["method"] == method and row["language"] == language]
            aggregate[f"{method}/{language}"] = {
                key: sum(row["metrics"][key] for row in selected) / len(selected)
                for key in metric_names
            }
    summary = {
        "status": "exploratory_candidate_dev_only",
        "candidate_version": candidate_version,
        "candidate_label_status": "not_human_verified",
        "test_split_evaluated": False,
        "refusal_evaluated": False,
        "question_variants": len(questions),
        "independent_intents": len({q["intent_id"] for q in questions}),
        "k": K,
        "recall_limit": RECALL_LIMIT,
        "locator_scope": "top_5_distinct_resources_among_recalled_chunks",
        "rrf_k": RRF_K,
        "index_report_sha256": sha256(index_dir / "build_report.json"),
        "catalog_fingerprint": index_report["catalog_fingerprint"],
        "questions_sha256": sha256(questions_path),
        "evidence_sha256": sha256(evidence_path),
        "runner_sha256": sha256(Path(__file__)),
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "random_seed": None,
        "metrics_by_method_language": aggregate,
        "mean_paired_zh_minus_en": paired_differences(rows),
        "resource_miss_question_ids": {
            method: [
                row["question_id"] for row in rows
                if row["method"] == method and row["metrics"]["resource_hit_at_5"] == 0
            ]
            for method in ("bm25", "bge_m3", "rrf")
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(aggregate, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--index-dir", type=Path, default=INDEX)
    parser.add_argument("--candidate-version", choices=("v2", "v3", "v4", "v5"), default="v2")
    args = parser.parse_args()
    asyncio.run(run(args.output_dir.resolve(), args.index_dir.resolve(), args.candidate_version))
