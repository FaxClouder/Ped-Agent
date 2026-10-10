"""P2 step 3: paired PyMuPDF / Adobe parse-quality material for the development PDFs.

Reuses ``ped_knowledge.parsing.compare.write_comparison`` with the Adobe response saved
by the 2026-09-24 import, so no PDF is uploaded. Writes only to a new output directory.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import pymupdf

from ped_knowledge.contracts import ElementType
from ped_knowledge.parsing.compare import write_comparison

from p2_common import (
    ANCHORS, ADJUDICATED, active_versions, anchor_parts, child_rows, code_provenance,
    covers_page, guard_output, library_versions, load_anchors, normalize, parse_adobe_saved,
    parse_pymupdf, saved_adobe_zip, sha256, sha256_bytes, text_has_anchor, verify_corpus,
)

SHINGLE = 24
STEP = 8
MANUAL_FIELDS = ("reading_order", "missing_or_duplicated_text", "table_rows_columns",
                 "page_numbers", "key_values_units", "gold_evidence_locatable", "notes")


def shingles(text: str, *, step: int = STEP) -> Counter:
    return Counter(text[i:i + SHINGLE] for i in range(0, max(0, len(text) - SHINGLE + 1), step))


def page_texts(document) -> dict[int, str]:
    pages: dict[int, list[str]] = {}
    for element in document.elements:
        if element.text:
            pages.setdefault(element.page_number, []).append(element.text)
    return {page: normalize("\n".join(texts)) for page, texts in pages.items()}


def text_layer_coverage(raw_pages: list[str], parsed: dict[int, str], last_page: int) -> dict:
    """Recall of raw PDF text-layer shingles, restricted to pages both parsers still cover."""
    raw = Counter()
    for page in range(1, last_page + 1):
        raw.update(shingles(raw_pages[page - 1]))
    parsed_all = "".join(parsed.get(page, "") for page in range(1, last_page + 1))
    dense = shingles(parsed_all, step=1)
    recovered = sum(count for gram, count in raw.items() if gram in dense)
    own = shingles(parsed_all)
    raw_dense = shingles("".join(raw_pages[:last_page]), step=1)
    excess = sum(max(0, count - raw_dense.get(gram, 0)) for gram, count in own.items())
    return {
        "text_layer_shingle_recall": recovered / max(1, sum(raw.values())),
        "shingle_excess_over_text_layer": excess / max(1, sum(own.values())),
    }


def anchor_locations(document, children: list[dict], parents: dict[str, dict], anchor, page: int) -> dict:
    elements = [item for item in document.elements if item.text]
    normalized = [normalize(item.text) for item in elements]
    by_page = page_texts(document)
    pages_found = sorted(p for p, text in by_page.items() if text_has_anchor(text, anchor))
    single = any(item.page_number == page and text_has_anchor(text, anchor)
                 for item, text in zip(elements, normalized))
    span = None
    for start, item in enumerate(elements):
        if item.page_number != page:
            continue
        joined = ""
        for width in range(1, 9):
            if start + width > len(elements):
                break
            joined += normalized[start + width - 1]
            if text_has_anchor(joined, anchor):
                span = width if span is None else min(span, width)
                break
    child_hits = [row for row in children if text_has_anchor(normalize(row["text"]), anchor)]
    child_on_page = [row for row in child_hits if covers_page(row, page)]
    parent_on_page = [row for row in parents.values()
                      if covers_page(row, page) and text_has_anchor(normalize(row["text"]), anchor)]
    return {
        "in_document": text_has_anchor(normalize("".join(item.text for item in elements)), anchor),
        "pages_found": pages_found,
        "on_gold_page": page in pages_found,
        "single_element_on_gold_page": single,
        "min_consecutive_elements_from_gold_page": span,
        "child_chunks_containing": len(child_hits),
        "child_chunks_containing_on_gold_page": len(child_on_page),
        "gold_child_page_spans": sorted({f"{row['page_start']}-{row['page_end']}" for row in child_on_page}),
        "parent_chunk_containing_on_gold_page": bool(parent_on_page),
    }


def table_dump(document, pages: set[int]) -> list[dict]:
    return [
        {"page_number": item.page_number, "rows": item.table_data, "row_count": len(item.table_data or []),
         "column_counts": sorted({len(row) for row in item.table_data or []})}
        for item in document.elements
        if item.element_type is ElementType.TABLE and item.page_number in pages
    ]


def resource_stats(document, report, children, parents, raw_pages, last_page) -> dict:
    parsed = page_texts(document)
    spans = [row["page_end"] - row["page_start"] + 1 for row in children]
    return {
        "parser_version": document.parser_version,
        "pages": report.page_count,
        "pages_with_text": len(parsed),
        "last_page_with_text": max(parsed) if parsed else None,
        "empty_pages": list(report.empty_pages),
        "elements": report.element_count,
        "tables": report.table_count,
        "images": report.image_count,
        "normalized_characters": sum(len(text) for text in parsed.values()),
        "parent_chunks": len(parents),
        "child_chunks": len(children),
        "mean_child_page_span": sum(spans) / len(spans),
        "multi_page_child_share": sum(span > 1 for span in spans) / len(spans),
        **text_layer_coverage(raw_pages, parsed, last_page),
    }


def run(output_dir: Path) -> dict:
    guard_output(output_dir)
    versions = active_versions()
    verify_corpus(versions)
    anchors = load_anchors()
    resources = sorted({item["resource_id"] for item in anchors["intents"]})
    output_dir.mkdir(parents=True)
    compare_root = output_dir / "compare"
    stats_rows, page_rows, anchor_rows, group_rows, checklist, provenance = [], [], [], [], [], {}
    tables = {}
    for resource in resources:
        version = versions[resource]
        source_sha = sha256(version["vault_path"])
        if source_sha != version["version_id"]:
            raise ValueError(f"vault PDF hash differs from active version: {resource}")
        with pymupdf.open(version["vault_path"]) as pdf:
            raw_pages = [normalize(page.get_text()) for page in pdf]
        documents = {"pymupdf": parse_pymupdf(version)}
        zip_path = saved_adobe_zip(version)
        record = {"source_pdf_sha256": source_sha, "catalog_parser_version": version["catalog_parser_version"],
                  "page_count": len(raw_pages)}
        if zip_path is not None:
            archive = zip_path.read_bytes()
            documents["adobe"] = parse_adobe_saved(version)
            catalog_doc = json.loads((version["derived_path"] / "document.json").read_text(encoding="utf-8"))
            record.update({
                "adobe_response_sha256": sha256_bytes(archive),
                "adobe_response_origin": "saved real Adobe PDF Extract response from the 2026-09-24 Catalog import; no new upload in P2",
                "adobe_structured_data_version": documents["adobe"][0].elements[0].metadata.get("adobe_version"),
                "adobe_reparse_equals_catalog_document": json.loads(documents["adobe"][0].model_dump_json()) == catalog_doc,
            })
            record["compare_summary"] = write_comparison(
                version["vault_path"], archive, compare_root / resource, resource_id=resource)
        else:
            record["adobe_status"] = "not_run: no saved Adobe response; upload authorization not confirmed (rights_status=pending)"
            (compare_root / resource).mkdir(parents=True)
        chunked = {}
        for parser, (document, report) in documents.items():
            (compare_root / resource / f"{parser}-document.json").write_text(
                document.model_dump_json(indent=2), encoding="utf-8")
            chunked[parser] = child_rows(document, version["title"])
        last_page = min(max(page_texts(doc)) for doc, _ in documents.values())
        record["coverage_compared_through_page"] = last_page
        provenance[resource] = record
        for parser, (document, report) in documents.items():
            children, parents = chunked[parser]
            stats_rows.append({"resource_id": resource, "parser": parser,
                               **resource_stats(document, report, children, parents, raw_pages, last_page)})
            parsed = page_texts(document)
            for page in range(1, len(raw_pages) + 1):
                page_rows.append({"resource_id": resource, "parser": parser, "page": page,
                                  "text_layer_chars": len(raw_pages[page - 1]),
                                  "parsed_chars": len(parsed.get(page, ""))})
        gold_pages = set()
        for intent in (item for item in anchors["intents"] if item["resource_id"] == resource):
            for group in intent["groups"]:
                page = group["pdf_page_1based"]
                gold_pages.add(page)
                for parser, (document, _) in documents.items():
                    children, parents = chunked[parser]
                    located = []
                    for kind in ("required", "supplementary"):
                        for anchor in group[kind]:
                            result = anchor_locations(document, children, parents, anchor, page)
                            anchor_rows.append({"intent_id": intent["intent_id"], "group_id": group["group_id"],
                                                "pdf_page_1based": page, "parser": parser, "kind": kind,
                                                "anchor": " + ".join(anchor_parts(anchor)) if isinstance(anchor, list) else anchor,
                                                **result})
                            if kind == "required":
                                located.append(result)
                    together = [row for row in children if covers_page(row, page) and all(
                        text_has_anchor(normalize(row["text"]), anchor) for anchor in group["required"])]
                    group_rows.append({
                        "intent_id": intent["intent_id"], "group_id": group["group_id"], "pdf_page_1based": page,
                        "parser": parser, "required_anchor_count": len(located),
                        "all_required_on_gold_page": all(item["on_gold_page"] for item in located),
                        "all_required_in_some_gold_child": all(item["child_chunks_containing_on_gold_page"] for item in located),
                        "all_required_in_one_gold_child": bool(together),
                        "all_required_in_one_gold_parent": any(
                            covers_page(row, page) and all(text_has_anchor(normalize(row["text"]), anchor) for anchor in group["required"])
                            for row in chunked[parser][1].values()),
                    })
            for diagnostic in intent.get("diagnostic", []):
                for parser, (document, _) in documents.items():
                    children, parents = chunked[parser]
                    anchor_rows.append({"intent_id": intent["intent_id"], "group_id": "diagnostic",
                                        "pdf_page_1based": diagnostic["pdf_page_1based"], "parser": parser,
                                        "kind": "diagnostic", "anchor": diagnostic["anchor"],
                                        **anchor_locations(document, children, parents, diagnostic["anchor"],
                                                           diagnostic["pdf_page_1based"])})
        tables[resource] = {parser: table_dump(document, gold_pages) for parser, (document, _) in documents.items()}
        for parser in documents:
            checklist.append({"resource_id": resource, "parser": parser,
                              "gold_pages": ";".join(str(p) for p in sorted(gold_pages)),
                              **{field: "" for field in MANUAL_FIELDS}})
        print(f"reviewed {resource}: {', '.join(documents)}", flush=True)

    def write_csv(name: str, rows: list[dict]) -> None:
        with (output_dir / name).open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows({key: json.dumps(value) if isinstance(value, list) else value
                              for key, value in row.items()} for row in rows)

    write_csv("resource_stats.csv", stats_rows)
    write_csv("page_stats.csv", page_rows)
    write_csv("anchor_locatability.csv", anchor_rows)
    write_csv("group_locatability.csv", group_rows)
    write_csv("manual_review_checklist_template.csv", checklist)
    (output_dir / "gold_page_tables.json").write_text(json.dumps(tables, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "status": "p2_parse_review_dev_pdfs_only",
        "adobe_api_called_in_this_run": False,
        "human_verified": False,
        "resources": provenance,
        "anchor_file_sha256": sha256(ANCHORS),
        "label_source_sha256": sha256(ADJUDICATED),
        "shingle_definition": f"normalized text, {SHINGLE}-character shingles, raw step {STEP}; text layer = PyMuPDF page.get_text()",
        "caveat": "Text-layer coverage uses the PDF's embedded text layer, the same layer PyMuPDF reads; it measures omissions/duplication relative to that layer, not OCR accuracy or Adobe superiority.",
        "code_provenance": code_provenance(),
        "library_versions": library_versions(),
        "command": f"python experiments/benchmark-parser-sensitivity-20260927/parse_review.py --output-dir {output_dir.as_posix()}",
    }
    names = ("resource_stats.csv", "page_stats.csv", "anchor_locatability.csv", "group_locatability.csv",
             "manual_review_checklist_template.csv", "gold_page_tables.json")
    summary["output_sha256"] = {name: sha256(output_dir / name) for name in names}
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps({key: result[key] for key in ("status", "adobe_api_called_in_this_run")}, indent=2))
