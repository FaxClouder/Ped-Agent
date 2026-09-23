"""Write a reviewable comparison of local and Adobe PDF extraction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from ped_knowledge.contracts import CanonicalDocument, ElementType
from ped_knowledge.parsing import parse_document
from ped_knowledge.parsing.adobe import extract_adobe_pdf, parse_adobe_zip


def write_comparison(
    source_path: Path, adobe_zip: bytes, output_dir: Path, *, resource_id: str
) -> dict[str, Any]:
    """Persist parser outputs to a new directory without changing Catalog state."""
    if output_dir.exists():
        raise FileExistsError(f"comparison output already exists: {output_dir}")
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    local, local_report = parse_document(
        source_path, resource_id=resource_id, version_id=source_hash
    )
    adobe, adobe_report, _ = parse_adobe_zip(
        adobe_zip, resource_id=resource_id, version_id=source_hash
    )
    summary = {
        "resource_id": resource_id,
        "source_sha256": source_hash,
        "adobe_response_sha256": hashlib.sha256(adobe_zip).hexdigest(),
        "pymupdf": _summary(local, local_report.model_dump()),
        "adobe": _summary(adobe, adobe_report.model_dump()),
        "review_note": "Counts are descriptive; inspect element order and table rows before judging accuracy.",
    }
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "comparison.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "pymupdf-elements.txt").write_text(_element_lines(local), encoding="utf-8")
    (output_dir / "adobe-elements.txt").write_text(_element_lines(adobe), encoding="utf-8")
    (output_dir / "pymupdf-tables.json").write_text(_tables(local), encoding="utf-8")
    (output_dir / "adobe-tables.json").write_text(_tables(adobe), encoding="utf-8")
    (output_dir / "adobe-extract.zip").write_bytes(adobe_zip)
    return summary


def _summary(document: CanonicalDocument, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "parser_version": document.parser_version,
        "page_count": report["page_count"],
        "text_page_count": report["text_page_count"],
        "ocr_page_count": report["ocr_page_count"],
        "empty_pages": report["empty_pages"],
        "element_count": report["element_count"],
        "table_count": report["table_count"],
        "image_count": report["image_count"],
        "text_characters": sum(len(item.text) for item in document.elements),
    }


def _element_lines(document: CanonicalDocument) -> str:
    return "\n".join(
        f"p.{item.page_number}\t{item.element_type.value}\t{item.text.replace(chr(10), ' | ')}"
        for item in document.elements
        if item.text
    ) + "\n"


def _tables(document: CanonicalDocument) -> str:
    return json.dumps(
        [
            {"page_number": item.page_number, "locator": item.locator, "rows": item.table_data}
            for item in document.elements
            if item.element_type is ElementType.TABLE
        ],
        ensure_ascii=False,
        indent=2,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Adobe Extract and PyMuPDF on one PDF")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resource-id")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"output directory already exists: {args.output}")
    adobe_zip = extract_adobe_pdf(args.pdf)
    result = write_comparison(
        args.pdf, adobe_zip, args.output, resource_id=args.resource_id or args.pdf.stem
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
