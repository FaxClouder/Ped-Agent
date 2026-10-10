"""Find non-labeled dense-retrieval source candidates for pre-seal annotation review."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex
from ped_knowledge.storage import Catalog

from evaluate_dev import BGEM3Gateway, GOLD, INDEX, POLICY, ROOT, _validate_snapshot, candidate_paths, read_jsonl, sha256


async def run(output_dir: Path, *, version: str = "v5", index_dir: Path = INDEX) -> None:
    if output_dir.exists():
        raise FileExistsError(output_dir)
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for the frozen BGE-M3 index")
    questions_path, evidence_path, manifest_path = candidate_paths(version)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for path in (questions_path, evidence_path):
        if sha256(path) != manifest["output_sha256"][path.name]:
            raise ValueError(f"Candidate file changed: {path.name}")
    catalog = Catalog(ROOT / "memPed/knowledge/knowledge.sqlite3")
    fts = FTSIndex(index_dir / "fts.sqlite3")
    vector = ChromaVectorIndex(index_dir / "chroma", BGEM3Gateway(ROOT / "memPed/knowledge/models/bge-m3"))
    index_report = _validate_snapshot(index_dir, catalog, fts, vector)
    chunks = {r["chunk_id"]: r for r in catalog.list_official_chunks(policy_version=POLICY)}
    evidence = {r["intent_id"]: r for r in read_jsonl(evidence_path)}
    questions = [q for q in read_jsonl(questions_path) if q.get("answerable") is True and q["language"] == "en"]
    if len(questions) != 120:
        raise ValueError("Expected 120 English answerable variants")
    rows = []
    for number, q in enumerate(questions, 1):
        known = {a["resource_id"] for g in evidence[q["intent_id"]]["evidence_groups"] for a in g["alternatives"]}
        hits = await vector.search(q["query"], limit=100)
        candidates = []
        seen = set()
        for rank, hit in enumerate(hits, 1):
            chunk = chunks.get(hit.chunk_id)
            if chunk is None or chunk["resource_id"] in known or chunk["resource_id"] in seen:
                continue
            seen.add(chunk["resource_id"])
            candidates.append({
                "retrieved_chunk_rank": rank, "resource_id": chunk["resource_id"],
                "version_id": chunk["version_id"], "pdf_page_start_1based": chunk["page_start"],
                "pdf_page_end_1based": chunk["page_end"], "chunk_id": chunk["chunk_id"],
                "title": chunk["title"], "text_excerpt": chunk["text"][:700],
            })
            if len(candidates) == 3:
                break
        rows.append({"intent_id": q["intent_id"], "question_id": q["question_id"], "query": q["query"], "known_resource_ids": sorted(known), "candidates": candidates})
        if number % 20 == 0:
            print(f"prepared {number}/120", flush=True)
    output_dir.mkdir(parents=True)
    (output_dir / "candidates.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    summary = {
        "status": "candidate_discovery_only_not_test_scoring", "candidate_version": version,
        "intents": len(rows), "index_catalog_fingerprint": index_report["catalog_fingerprint"],
        "index_report_sha256": sha256(index_dir / "build_report.json"),
        "candidate_manifest_sha256": sha256(manifest_path),
        "method": "BGE-M3 dense top 100 child chunks per English query; first 3 distinct sources outside existing evidence groups",
        "limitations": ["Candidates require PDF-page review before evidence inclusion", "Retrieval may miss semantic alternatives beyond top 100 chunks", "Not a test-set performance evaluation"],
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-version", choices=("v5",), default="v5")
    args = parser.parse_args()
    asyncio.run(run(args.output_dir.resolve(), version=args.candidate_version))
