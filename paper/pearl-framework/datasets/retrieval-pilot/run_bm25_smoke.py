"""Run a fresh, deterministic R1 smoke retrieval over the PEARL source PDFs.

This builds new page-local children and rankings. It does not score semantic support.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
MANIFEST = HERE.parent / "retrieval-corpus" / "corpus-manifest.jsonl"
PILOT = HERE / "pilot-intents-agent-reviewed-v3.json"
WORD = re.compile(r"\S+")
TOKEN = re.compile(r"[a-z]+|[0-9]+")
CHILD_WORDS = 180
OVERLAP_WORDS = 40
K1 = 1.2
B = 0.75
TOP_N = 100


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(value: str) -> list[str]:
    return TOKEN.findall(unicodedata.normalize("NFKC", value).casefold())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_bm25_smoke.py NEW_OUTPUT_DIRECTORY")
    output = Path(sys.argv[1]).resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    if pilot["status"] != "agent_reviewed_preliminary" or not pilot["gold_frozen"]:
        raise ValueError("pilot Gold is not frozen for the smoke run")
    if pilot["corpus_manifest_sha256"] != sha(MANIFEST):
        raise ValueError("corpus manifest hash mismatch")
    sources = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines()]
    if any(row["selection_status"] != "included" for row in sources):
        raise ValueError("manifest contains a source outside the fixed corpus")
    if len(sources) != 108:
        raise ValueError("unexpected source count")
    output.mkdir(parents=True)
    started = time.perf_counter()
    children: list[dict] = []
    with (output / "children.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for row in sources:
            pdf = REPO / row["source_path"]
            if not pdf.is_file() or sha(pdf) != row["sha256"]:
                raise ValueError(f"source file/hash mismatch: {row['source_id']}")
            with pymupdf.open(pdf) as document:
                if len(document) != row["page_count"]:
                    raise ValueError(f"page count changed: {row['source_id']}")
                for page_number, page in enumerate(document, start=1):
                    page_text = page.get_text("text")
                    words = WORD.findall(page_text)
                    step = CHILD_WORDS - OVERLAP_WORDS
                    for start in range(0, len(words), step):
                        sample = words[start:start + CHILD_WORDS]
                        if not sample:
                            break
                        content = " ".join(sample)
                        chunk_id = f"{row['source_id']}:p{page_number:04d}:w{start:06d}"
                        child = {"chunk_id": chunk_id, "source_id": row["source_id"],
                                 "page": page_number, "word_start": start, "text": content,
                                 "text_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
                        children.append(child)
                        stream.write(json.dumps(child, ensure_ascii=False, sort_keys=True) + "\n")
                        if start + CHILD_WORDS >= len(words):
                            break
    built_seconds = time.perf_counter() - started
    counts = [Counter(analyze(item["text"])) for item in children]
    lengths = [sum(counter.values()) for counter in counts]
    avgdl = sum(lengths) / len(lengths)
    postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for index, terms in enumerate(counts):
        for term, freq in terms.items():
            postings[term].append((index, freq))
    index_seconds = time.perf_counter() - started - built_seconds
    ranks: list[dict] = []
    timings: list[dict] = []
    for intent in pilot["intents"]:
        query_start = time.perf_counter()
        scores = [0.0] * len(children)
        for term in set(analyze(intent["query"])):
            posting = postings.get(term, [])
            df = len(posting)
            if not df:
                continue
            idf = math.log(1.0 + (len(children) - df + 0.5) / (df + 0.5))
            for index, freq in posting:
                denominator = freq + K1 * (1.0 - B + B * lengths[index] / avgdl)
                scores[index] += idf * freq * (K1 + 1.0) / denominator
        ordered = sorted(range(len(children)), key=lambda i: (-scores[i], children[i]["chunk_id"]))[:TOP_N]
        elapsed = time.perf_counter() - query_start
        timings.append({"intent_id": intent["intent_id"], "seconds": elapsed})
        ranks.append({"intent_id": intent["intent_id"], "method": "R1_BM25_smoke",
                      "query": intent["query"], "elapsed_seconds": elapsed,
                      "results": [{"rank": rank, "score": scores[i], **children[i]}
                                  for rank, i in enumerate(ordered, start=1)]})
    with (output / "rankings.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for row in ranks:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    run = {"run_type": "preliminary_dev_smoke", "method": "R1_BM25_only",
           "corpus_version": pilot["corpus_version"], "corpus_manifest_sha256": sha(MANIFEST),
           "pilot_dataset_id": pilot["dataset_id"], "pilot_sha256": sha(PILOT),
           "source_count": len(sources), "child_count": len(children),
           "child_policy": {"page_local": True, "word_split": "regex_non_whitespace",
                            "max_words": CHILD_WORDS, "overlap_words": OVERLAP_WORDS},
           "bm25": {"idf": "ln(1+(N-df+0.5)/(df+0.5))", "k1": K1, "b": B,
                    "query_term_policy": "unique terms", "analyzer": "NFKC casefold [a-z]+|[0-9]+"},
           "ranking": {"depth": TOP_N, "ties": "chunk_id_ascending"},
           "python": sys.version, "pymupdf": pymupdf.VersionBind,
           "build_seconds": built_seconds, "index_seconds": index_seconds,
           "query_timings": timings,
           "children_sha256": sha(output / "children.jsonl"),
           "rankings_sha256": sha(output / "rankings.jsonl"),
           "semantic_support_scored": False,
           "limitations": ["Text-only PyMuPDF extraction; table layout may be lost",
                           "No dense, fusion, or reranker method in this smoke run"]}
    write_json(output / "run-manifest.json", run)
    print(json.dumps({"output": str(output), "sources": len(sources), "children": len(children),
                      "intents": len(ranks), "seconds": time.perf_counter() - started}, sort_keys=True))


if __name__ == "__main__":
    main()
