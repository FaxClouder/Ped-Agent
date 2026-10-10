"""Rebuild the PEARL Retrieval source inventory from local domain PDFs.

Reads source PDFs and historical bibliographic metadata; never reads Gold, indexes,
rankings, or prior evaluation scores. Writes metadata only into this directory.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pymupdf


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
KNOWLEDGE = REPO / "memPed" / "knowledge"
RECORDS = KNOWLEDGE / "literature" / "records"
HOLD_DIR = KNOWLEDGE / "batch-1-held"
STOPWORDS = {"the", "and", "of", "in", "to", "for", "with", "on", "is", "are", "from", "that"}
CORPUS_VERSION = "pearl-retrieval-corpus-2026-09-29-01"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def jsonl(path: Path, rows: list[dict]) -> None:
    content = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    if path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise RuntimeError(f"Frozen output differs: {path}; create a new corpus version")
        return
    path.write_text(content, encoding="utf-8")


def load_metadata() -> tuple[dict[str, dict], dict[str, dict]]:
    core = {}
    for line in (RECORDS / "core_manifest.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        core[Path(row["source_path"]).name] = row
    inventory = {}
    for batch in range(1, 6):
        path = KNOWLEDGE / f"batch-{batch}-incoming" / f"batch{batch}_inventory.csv"
        with path.open(encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                inventory[row["filename"]] = row
    with (RECORDS / "candidates.csv").open(encoding="utf-8-sig", newline="") as source:
        by_doi = {row["doi"].lower(): row for row in csv.DictReader(source) if row.get("doi")}
    for row in inventory.values():
        candidate = by_doi.get((row.get("doi") or "").lower(), {})
        row["language"] = row.get("language") or candidate.get("language")
    return core, inventory


def audit(path: Path, core: dict[str, dict], inventory: dict[str, dict]) -> tuple[dict, dict | None]:
    expected = core.get(path.name, {})
    catalog = inventory.get(path.name, {})
    actual_hash = sha256(path)
    rel_path = path.relative_to(REPO).as_posix()
    warnings = []
    if expected and expected["sha256"].lower() != actual_hash:
        warnings.append("historical_manifest_hash_mismatch")
    if catalog and catalog.get("sha256") and catalog["sha256"].lower() != actual_hash:
        warnings.append("inventory_hash_mismatch")

    page_count = 0
    text_pages = 0
    low_text_pages = 0
    char_count = 0
    sample = ""
    pdf_error = None
    try:
        with pymupdf.open(path) as document:
            if document.needs_pass:
                raise ValueError("encrypted PDF")
            page_count = len(document)
            for index, page in enumerate(document):
                text = page.get_text("text")
                char_count += len(text.strip())
                text_pages += len(text.strip()) >= 100
                low_text_pages += len(text.strip()) < 100
                if index < 3:
                    sample += " " + text[:5000]
    except Exception as error:
        pdf_error = f"{type(error).__name__}: {error}"

    words = [word.lower() for word in re.findall(r"[A-Za-z]+", sample)]
    english_cue = sum(word in STOPWORDS for word in words)
    title = expected.get("title") or catalog.get("title") or ""
    title_tokens = {word.lower() for word in re.findall(r"[A-Za-z]+", title)
                    if len(word) > 3 and word.lower() not in STOPWORDS}
    title_overlap = round(len(title_tokens & set(words)) / len(title_tokens), 3) if title_tokens else None
    if page_count == 0 or text_pages == 0:
        warnings.append("no_extractable_text")
    if 0 < page_count and low_text_pages:
        warnings.append("low_text_pages_present")
    if len(words) < 100 or english_cue < 10:
        warnings.append("english_text_needs_manual_review")
    if title_overlap is not None and title_overlap < 0.5:
        warnings.append("pdf_title_needs_manual_review")
    if pdf_error:
        warnings.append("pdf_open_error")

    historical_id = expected.get("resource_id") or catalog.get("resource_id")
    derived_path = KNOWLEDGE / "derived" / historical_id / actual_hash if historical_id else None
    derived_document_present = bool(derived_path and (derived_path / "document.json").is_file())
    derived_chunks_present = bool(derived_path and (derived_path / "chunks.jsonl").is_file())

    held = path.parent == HOLD_DIR
    if held:
        decision = "hold_outside_incoming"
    elif pdf_error or page_count == 0 or text_pages == 0 or "historical_manifest_hash_mismatch" in warnings:
        decision = "technical_review"
    elif "english_text_needs_manual_review" in warnings:
        decision = "language_review"
    else:
        decision = "candidate"

    common = {
        "corpus_version": CORPUS_VERSION,
        "source_id": "pearl-src-" + actual_hash[:16],
        "source_path": rel_path,
        "sha256": actual_hash,
        "bytes": path.stat().st_size,
        "title_metadata": expected.get("title") or catalog.get("title") or None,
        "doi_metadata": expected.get("doi") or catalog.get("doi") or None,
        "language_metadata": expected.get("language") or catalog.get("language") or None,
        "topic_metadata": expected.get("topics") or ([catalog["primary_topic"]] if catalog.get("primary_topic") else []),
        "historical_resource_id": historical_id or None,
        "page_count": page_count,
        "text_pages_ge_100_chars": text_pages,
        "low_text_pages_lt_100_chars": low_text_pages,
        "extractable_char_count": char_count,
        "first_three_pages_english_cue_count": english_cue,
        "first_three_pages_ascii_word_count": len(words),
        "metadata_title_token_overlap_first_three_pages": title_overlap,
        "warnings": warnings,
        "technical_status": decision,
        "selection_status": "included" if decision == "candidate" else "excluded",
        "pdf_error": pdf_error,
        "historical_derived_document_present": derived_document_present,
        "historical_derived_chunks_present": derived_chunks_present,
    }
    manifest = None
    if decision == "candidate":
        manifest = {
            key: common[key]
            for key in (
                "source_id", "source_path", "sha256", "bytes", "title_metadata",
                "doi_metadata", "language_metadata", "topic_metadata", "page_count", "technical_status",
            )
        }
        manifest["corpus_version"] = CORPUS_VERSION
        manifest["selection_status"] = "included"
    return common, manifest


def main() -> None:
    core, inventory = load_metadata()
    paths = [
        file
        for batch in range(1, 6)
        for file in (KNOWLEDGE / f"batch-{batch}-incoming").glob("*.pdf")
    ] + list(HOLD_DIR.glob("*.pdf"))
    audit_rows = []
    manifest_rows = []
    for path in sorted(paths, key=lambda item: item.as_posix().lower()):
        row, candidate = audit(path, core, inventory)
        audit_rows.append(row)
        if candidate:
            manifest_rows.append(candidate)
    jsonl(HERE / "corpus-audit.jsonl", audit_rows)
    jsonl(HERE / "corpus-manifest.jsonl", manifest_rows)
    print(json.dumps({"scanned": len(audit_rows), "candidate": len(manifest_rows),
                      "status_counts": dict(Counter(row["technical_status"] for row in audit_rows))},
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
