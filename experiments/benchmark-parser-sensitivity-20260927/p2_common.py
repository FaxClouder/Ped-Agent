"""Shared read-only helpers for the P2 parser sensitivity experiment.

Nothing here writes to the Catalog, derived assets, or existing indexes.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sqlite3
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE = ROOT / "memPed/knowledge"
CATALOG = KNOWLEDGE / "knowledge.sqlite3"
MANIFEST = KNOWLEDGE / "literature/records/core_manifest.jsonl"
MODEL_DIR = KNOWLEDGE / "models/bge-m3"
V1_REPORT = ROOT / "outputs/knowledge-index-104-v1-20260924-01/build_report.json"
V1_DEV_RUN = ROOT / "outputs/gold-v5-dev-exploratory-20260924-01"
ADJUDICATED = ROOT / "outputs/stage2-agent-adjudicated-20260927-03/annotations.jsonl"
ANCHORS = Path(__file__).with_name("evidence_anchors_dev.json")
POLICY = "parent-child-v1"
TOKENIZER = "regex-token-v1"

# Code whose behaviour defines the parsed documents, chunks, indexes and scores.
PROVENANCE_SOURCES = (
    "Knowledge-Base/src/ped_knowledge/parsing/__init__.py",
    "Knowledge-Base/src/ped_knowledge/parsing/adobe.py",
    "Knowledge-Base/src/ped_knowledge/parsing/compare.py",
    "Knowledge-Base/src/ped_knowledge/chunking/__init__.py",
    "Knowledge-Base/src/ped_knowledge/tokenization/__init__.py",
    "Knowledge-Base/src/ped_knowledge/indexing/__init__.py",
    "Knowledge-Base/src/ped_knowledge/contracts/__init__.py",
    "Knowledge-Base/src/ped_knowledge/evaluation/gold_v2.py",
    "experiments/benchmark-gold-20260923/dev_scope.py",
    "experiments/benchmark-gold-20260923/compare_lexical_candidate.py",
    "experiments/benchmark-parser-sensitivity-20260927/p2_common.py",
    "experiments/benchmark-parser-sensitivity-20260927/evidence_anchors_dev.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def guard_output(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite research output: {path}")


def code_provenance() -> dict:
    """Git HEAD alone is insufficient because the working tree is dirty."""
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    return {
        "git_head": head,
        "working_tree_dirty": bool(status.strip()),
        "git_status_porcelain_sha256": sha256_bytes(status.encode("utf-8")),
        "source_sha256": {name: sha256(ROOT / name) for name in PROVENANCE_SOURCES},
    }


def library_versions() -> dict:
    import importlib.metadata as metadata

    versions = {}
    for package in ("PyMuPDF", "pdfservices-sdk", "FlagEmbedding", "chromadb", "torch",
                    "transformers", "jieba", "numpy"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def resolve_memped(relative: str) -> Path:
    """Catalog paths were written as either ``knowledge\\...`` or relative to ``knowledge``."""
    normalized = relative.replace("\\", "/")
    if normalized.startswith("knowledge/"):
        return ROOT / "memPed" / normalized
    return KNOWLEDGE / normalized


def active_versions() -> dict[str, dict]:
    with sqlite3.connect(f"file:{CATALOG.as_posix()}?mode=ro", uri=True) as db:
        rows = db.execute(
            "SELECT r.resource_id, r.title, v.version_id, v.sha256, v.vault_path, v.derived_path, "
            "v.parser_version FROM resources r JOIN resource_versions v "
            "ON v.version_id = r.active_version_id WHERE r.retrieval_eligibility = 'official' "
            "ORDER BY r.resource_id"
        ).fetchall()
    return {
        row[0]: {
            "resource_id": row[0], "title": row[1], "version_id": row[2], "sha256": row[3],
            "vault_path": resolve_memped(row[4]), "derived_path": resolve_memped(row[5]),
            "catalog_parser_version": row[6],
        }
        for row in rows
    }


def verify_corpus(versions: dict[str, dict]) -> list[dict]:
    records = read_jsonl(MANIFEST)
    expected = {item["resource_id"]: item["sha256"] for item in records}
    actual = {rid: item["version_id"] for rid, item in versions.items()}
    if len(records) != 104 or expected != actual or not all(item["include"] for item in records):
        raise ValueError("manifest and active Catalog members differ")
    if any(item["version_id"] != item["sha256"] for item in versions.values()):
        raise ValueError("active version ids are not source hashes")
    return records


def normalize(text: str) -> str:
    """Parser-neutral text key: NFKC, casefold, keep only letters, digits, '.' and '%'.

    Removing spaces, hyphens and punctuation makes line-break hyphenation, ligatures,
    mathematical alphanumerics and whitespace differences irrelevant.
    """
    folded = unicodedata.normalize("NFKC", text).casefold()
    return "".join(char for char in folded if char.isascii() and (char.isalnum() or char in ".%"))


def anchor_parts(anchor: str | list[str]) -> list[str]:
    parts = [anchor] if isinstance(anchor, str) else list(anchor)
    normalized = [normalize(part) for part in parts]
    if not all(normalized):
        raise ValueError(f"empty normalized anchor: {anchor!r}")
    return normalized


def text_has_anchor(normalized_text: str, anchor: str | list[str]) -> bool:
    """A list anchor requires every part to co-occur in the same text (e.g. table cells)."""
    return all(part in normalized_text for part in anchor_parts(anchor))


def load_anchors() -> dict:
    payload = json.loads(ANCHORS.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "p2-evidence-anchors-v1":
        raise ValueError("unexpected anchor schema")
    return payload


def saved_adobe_zip(version: dict) -> Path | None:
    path = version["derived_path"] / "adobe" / "extract.zip"
    return path if path.is_file() else None


def parse_pymupdf(version: dict):
    """Local structured parse, identical to ``ImportService(parser_backend='pymupdf')``."""
    from ped_knowledge.parsing import parse_document

    return parse_document(version["vault_path"], resource_id=version["resource_id"],
                          version_id=version["version_id"])


def parse_adobe_saved(version: dict):
    """Re-parse the saved real Adobe response; never calls the Adobe API."""
    from ped_knowledge.parsing.adobe import parse_adobe_zip

    path = saved_adobe_zip(version)
    if path is None:
        raise FileNotFoundError(f"no saved Adobe response: {version['resource_id']}")
    document, report, _ = parse_adobe_zip(path.read_bytes(), resource_id=version["resource_id"],
                                          version_id=version["version_id"])
    return document, report


def parse_catalog_backend(version: dict):
    """Reproduce the active Catalog parse with the backend recorded in the Catalog."""
    if version["catalog_parser_version"].startswith("adobe-"):
        return parse_adobe_saved(version)
    if version["catalog_parser_version"].startswith("pymupdf-"):
        return parse_pymupdf(version)
    raise ValueError(f"unknown Catalog parser: {version['catalog_parser_version']}")


def child_rows(document, title: str) -> tuple[list[dict], dict[str, dict]]:
    """Default ``parent-child-v1`` chunks, as index rows plus a parent lookup."""
    from ped_knowledge.chunking import HierarchicalChunker
    from ped_knowledge.contracts import ChunkLevel

    children: list[dict] = []
    parents: dict[str, dict] = {}
    for chunk in HierarchicalChunker().chunk(document):
        row = chunk.model_dump(mode="json")
        row["title"] = title
        if chunk.chunk_level is ChunkLevel.PARENT:
            parents[chunk.chunk_id] = row
        else:
            children.append(row)
    if any(row["policy_version"] != POLICY or row["tokenizer_fingerprint"] != TOKENIZER for row in children):
        raise ValueError("unexpected chunk policy or tokenizer")
    return children, parents


def chunk_fingerprint(rows: list[dict]) -> str:
    """Same ordering and payload as ``Catalog.official_fingerprint``."""
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: (item["resource_id"], item["ordinal"])):
        digest.update(str(row["chunk_id"]).encode("utf-8"))
        digest.update(str(row["text"]).encode("utf-8"))
    return digest.hexdigest()


def covers_page(row: dict, page: int) -> bool:
    return row["page_start"] <= page <= row["page_end"]


def group_text_rank(group: dict, ranking: list[dict], *, resource_id: str,
                    text_of=lambda row: row["text"]) -> int | None:
    """First rank of a chunk that covers the Gold page and contains every required anchor."""
    for rank, row in enumerate(ranking, 1):
        if (row["resource_id"] == resource_id and covers_page(row, group["pdf_page_1based"])
                and all(text_has_anchor(normalize(text_of(row)), anchor) for anchor in group["required"])):
            return rank
    return None


def exact_binomial_two_sided(wins: int, losses: int) -> float:
    """Exact sign test on discordant pairs; 1.0 when there are none."""
    n = wins + losses
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(wins, losses) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def bootstrap_mean_ci(values: list[float], *, seed: int, draws: int = 10000) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    generator = random.Random(seed)
    means = sorted(
        sum(generator.choice(values) for _ in values) / len(values) for _ in range(draws)
    )
    return (means[int(0.025 * draws)], means[int(0.975 * draws) - 1])
