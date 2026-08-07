"""Structured PDF parsing with observable OCR and plain-text fallback paths."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any, cast

from ped_knowledge.contracts import (
    AssetRef,
    CanonicalDocument,
    CanonicalPage,
    ChunkLevel,
    DocumentElement,
    ElementType,
    KnowledgeChunk,
    OCRGateway,
    ParseReport,
)

PARSER_VERSION = "pymupdf-structured-v2"
LEGACY_CHUNK_SIZE = 1200
LEGACY_CHUNK_OVERLAP = 120
REFERENCE_HEADINGS = {"references", "bibliography", "参考文献"}
HEADING_PATTERN = re.compile(
    r"^(?:\d+(?:\.\d+)*\s+|第[一二三四五六七八九十百千万0-9]+[章节]\s*|[A-Z][A-Z\s-]{3,})"
)
CLAUSE_PATTERN = re.compile(r"第[一二三四五六七八九十百千万0-9.]+条")
CAPTION_PATTERN = re.compile(r"^(?:fig(?:ure)?\.?|table|图|表)\s*\d+", re.IGNORECASE)
LIST_PATTERN = re.compile(r"^(?:[-•▪◦]|\(?\d+[.)]|[（(]?[一二三四五六七八九十]+[）)])\s*")


def parse_document(
    path: Path,
    *,
    resource_id: str,
    version_id: str,
    detect_clauses: bool = False,
    ocr_gateway: OCRGateway | None = None,
) -> tuple[CanonicalDocument, ParseReport]:
    fitz = _fitz()
    elements: list[DocumentElement] = []
    pages: list[CanonicalPage] = []
    assets: list[AssetRef] = []
    empty_pages: list[int] = []
    manual_review_pages: list[int] = []
    text_page_count = 0
    ocr_page_count = 0
    degradation_reasons: list[str] = []
    table_count = 0
    image_count = 0
    reached_references = False
    heading_path: tuple[str, ...] = ()

    with fitz.open(path) as document:
        if document.needs_pass:
            raise ValueError(f"encrypted PDF is not supported: {path}")
        if document.page_count < 1:
            raise ValueError(f"PDF has no pages: {path}")
        repeated = _repeated_edge_lines(document)
        for page_index, page in enumerate(document, start=1):
            page_element_ids: list[str] = []
            blocks = page.get_text("dict", sort=True).get("blocks", [])
            body_size = _body_font_size(blocks)
            page_has_text = False
            for block in blocks:
                if block.get("type") != 0:
                    continue
                text = _block_text(block)
                if not text or _is_repeated_block(text, repeated):
                    continue
                if text.casefold() in REFERENCE_HEADINGS:
                    reached_references = True
                    break
                element_type = _classify_element(
                    text,
                    block,
                    body_size=body_size,
                    detect_clauses=detect_clauses,
                    first_text=not elements,
                )
                if element_type in {ElementType.TITLE, ElementType.HEADING}:
                    heading_path = _next_heading_path(heading_path, text, element_type)
                locator = _locator(text, page_index, detect_clauses)
                element = _element(
                    resource_id,
                    version_id,
                    page_index,
                    len(elements),
                    element_type,
                    text,
                    _bbox(block.get("bbox")),
                    heading_path,
                    locator,
                )
                elements.append(element)
                page_element_ids.append(element.element_id)
                page_has_text = True
            if reached_references:
                pages.append(
                    CanonicalPage(
                        page_number=page_index,
                        width=float(page.rect.width),
                        height=float(page.rect.height),
                        element_ids=tuple(page_element_ids),
                    )
                )
                break

            tables = _extract_tables(page)
            for table_index, table in enumerate(tables, start=1):
                table_text = _render_table(table["rows"])
                element = _element(
                    resource_id,
                    version_id,
                    page_index,
                    len(elements),
                    ElementType.TABLE,
                    table_text,
                    table["bbox"],
                    heading_path,
                    f"table {table_index} / p.{page_index}",
                    table_data=table["rows"],
                )
                elements.append(element)
                page_element_ids.append(element.element_id)
                assets.append(
                    AssetRef(
                        asset_type="table",
                        path=f"tables/{element.element_id}.json",
                        page_number=page_index,
                        element_id=element.element_id,
                    )
                )
                table_count += 1
            for image_index, image in enumerate(page.get_images(full=True), start=1):
                xref = int(image[0])
                element = _element(
                    resource_id,
                    version_id,
                    page_index,
                    len(elements),
                    ElementType.IMAGE,
                    "",
                    None,
                    heading_path,
                    f"image {image_index} / p.{page_index}",
                    metadata={"xref": xref},
                )
                elements.append(element)
                page_element_ids.append(element.element_id)
                assets.append(
                    AssetRef(
                        asset_type="image",
                        path=f"images/{element.element_id}",
                        page_number=page_index,
                        element_id=element.element_id,
                    )
                )
                image_count += 1

            ocr_applied = False
            if not page_has_text:
                ocr_text = (
                    ocr_gateway.extract_page_text(path, page_index).strip()
                    if ocr_gateway is not None
                    else ""
                )
                if ocr_text:
                    ocr_applied = True
                    ocr_page_count += 1
                    element = _element(
                        resource_id,
                        version_id,
                        page_index,
                        len(elements),
                        ElementType.OCR_TEXT,
                        ocr_text,
                        None,
                        heading_path,
                        f"p.{page_index}",
                    )
                    elements.append(element)
                    page_element_ids.append(element.element_id)
                else:
                    empty_pages.append(page_index)
                    manual_review_pages.append(page_index)
            else:
                text_page_count += 1
            pages.append(
                CanonicalPage(
                    page_number=page_index,
                    width=float(page.rect.width),
                    height=float(page.rect.height),
                    ocr_applied=ocr_applied,
                    element_ids=tuple(page_element_ids),
                )
            )

    indexable = [item for item in elements if item.text.strip()]
    if not indexable:
        raise ValueError(f"PDF produced no indexable text: {path}")
    if empty_pages:
        degradation_reasons.append("pages_without_extractable_text")
    if ocr_gateway is None and empty_pages:
        degradation_reasons.append("ocr_gateway_unavailable")
    canonical = CanonicalDocument(
        resource_id=resource_id,
        version_id=version_id,
        source_hash=version_id,
        parser_version=PARSER_VERSION,
        pages=pages,
        elements=elements,
        assets=assets,
    )
    report = ParseReport(
        resource_id=resource_id,
        version_id=version_id,
        parser_version=PARSER_VERSION,
        page_count=len(pages),
        text_page_count=text_page_count,
        ocr_page_count=ocr_page_count,
        empty_pages=tuple(empty_pages),
        element_count=len(elements),
        table_count=table_count,
        image_count=image_count,
        degraded=bool(degradation_reasons),
        degradation_reasons=tuple(degradation_reasons),
        manual_review_pages=tuple(manual_review_pages),
    )
    return canonical, report


def write_derived_assets(
    root: Path,
    document: CanonicalDocument,
    report: ParseReport,
    chunks: list[KnowledgeChunk],
    *,
    source_path: Path,
) -> list[tuple[str, str, str]]:
    target = root / document.resource_id / document.version_id
    target.mkdir(parents=True, exist_ok=True)
    assets: list[tuple[str, str, str]] = []
    assets.append(_write_text(target, "document.json", document.model_dump_json(indent=2)))
    assets.append(
        _write_text(
            target,
            "elements.jsonl",
            "\n".join(item.model_dump_json() for item in document.elements) + "\n",
        )
    )
    assets.append(
        _write_text(
            target,
            "chunks.jsonl",
            "\n".join(item.model_dump_json() for item in chunks) + "\n",
        )
    )
    assets.append(_write_text(target, "parse_report.json", report.model_dump_json(indent=2)))
    table_dir = target / "tables"
    for element in document.elements:
        if element.element_type is not ElementType.TABLE or element.table_data is None:
            continue
        table_dir.mkdir(parents=True, exist_ok=True)
        json_name = f"{element.element_id}.json"
        html_name = f"{element.element_id}.html"
        assets.append(
            _write_text(
                target,
                f"tables/{json_name}",
                json.dumps(element.table_data, ensure_ascii=False, indent=2),
            )
        )
        assets.append(_write_text(target, f"tables/{html_name}", _table_html(element.table_data)))
    assets.extend(_write_images(target, document, source_path))
    return assets


def parse_pdf(
    path: Path,
    *,
    resource_id: str,
    version_id: str,
    detect_clauses: bool = False,
) -> list[KnowledgeChunk]:
    """Compatibility parser that retains the original 1200-character chunk contract."""
    document, _ = parse_document(
        path,
        resource_id=resource_id,
        version_id=version_id,
        detect_clauses=detect_clauses,
    )
    chunks: list[KnowledgeChunk] = []
    ordinal = 0
    by_page: dict[int, list[DocumentElement]] = {}
    for element in document.elements:
        if element.text.strip() and element.element_type is not ElementType.IMAGE:
            by_page.setdefault(element.page_number, []).append(element)
    for page_number, page_elements in by_page.items():
        text = "\n".join(item.text for item in page_elements).strip()
        section = next(
            (
                match.group(0)
                for item in page_elements
                if (match := CLAUSE_PATTERN.search(item.text)) is not None
            ),
            None,
        )
        locator = (
            f"{section} / p.{page_number}" if detect_clauses and section else f"p.{page_number}"
        )
        for part in _split_legacy(text):
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{resource_id}:{version_id[:12]}:{ordinal:05d}",
                    resource_id=resource_id,
                    version_id=version_id,
                    ordinal=ordinal,
                    text=part,
                    page_start=page_number,
                    page_end=page_number,
                    locator=locator,
                    section=section,
                    parser_version=PARSER_VERSION,
                    chunk_level=ChunkLevel.CHILD,
                    policy_version="legacy-char-v1",
                    element_ids=tuple(item.element_id for item in page_elements),
                )
            )
            ordinal += 1
    return chunks


def _fitz():
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF parsing") from exc
    return fitz


def _repeated_edge_lines(document: Any) -> set[str]:
    pages = [
        [line.strip() for line in page.get_text("text").splitlines() if line.strip()]
        for page in document
    ]
    if len(pages) < 2:
        return set()
    counts: Counter[str] = Counter()
    for lines in pages:
        counts.update(set(lines[:2] + lines[-2:]))
    threshold = max(2, (len(pages) + 1) // 2)
    return {line for line, count in counts.items() if count >= threshold}


def _block_text(block: dict[str, Any]) -> str:
    lines: list[str] = []
    for line in block.get("lines", []):
        text = "".join(str(span.get("text", "")) for span in line.get("spans", [])).strip()
        if text:
            lines.append(text)
    return "\n".join(lines).strip()


def _body_font_size(blocks: list[dict[str, Any]]) -> float:
    sizes = [
        float(span.get("size", 0))
        for block in blocks
        if block.get("type") == 0
        for line in block.get("lines", [])
        for span in line.get("spans", [])
        if span.get("text", "").strip()
    ]
    return median(sizes) if sizes else 10.0


def _classify_element(
    text: str,
    block: dict[str, Any],
    *,
    body_size: float,
    detect_clauses: bool,
    first_text: bool,
) -> ElementType:
    if detect_clauses and CLAUSE_PATTERN.match(text):
        return ElementType.CLAUSE
    if CAPTION_PATTERN.match(text):
        return ElementType.CAPTION
    if LIST_PATTERN.match(text):
        return ElementType.LIST
    maximum_size = max(
        (
            float(span.get("size", 0))
            for line in block.get("lines", [])
            for span in line.get("spans", [])
        ),
        default=0,
    )
    if first_text and maximum_size >= body_size * 1.35:
        return ElementType.TITLE
    if HEADING_PATTERN.match(text) or maximum_size >= body_size * 1.18:
        return ElementType.HEADING
    return ElementType.PARAGRAPH


def _next_heading_path(
    current: tuple[str, ...], text: str, element_type: ElementType
) -> tuple[str, ...]:
    normalized = " ".join(text.split())[:200]
    if element_type is ElementType.TITLE:
        return (normalized,)
    match = re.match(r"^(\d+(?:\.\d+)*)", normalized)
    if match:
        depth = match.group(1).count(".") + 1
        return current[:depth] + (normalized,)
    return current[:1] + (normalized,)


def _locator(text: str, page_number: int, detect_clauses: bool) -> str:
    if detect_clauses and (match := CLAUSE_PATTERN.search(text)):
        return f"{match.group(0)} / p.{page_number}"
    return f"p.{page_number}"


def _element(
    resource_id: str,
    version_id: str,
    page_number: int,
    order: int,
    element_type: ElementType,
    text: str,
    bbox: tuple[float, float, float, float] | None,
    heading_path: tuple[str, ...],
    locator: str,
    *,
    table_data: list[list[str]] | None = None,
    metadata: dict[str, Any] | None = None,
) -> DocumentElement:
    payload = f"{resource_id}|{version_id}|{page_number}|{order}|{element_type}|{text}"
    element_id = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return DocumentElement(
        element_id=element_id,
        element_type=element_type,
        text=text,
        page_number=page_number,
        bbox=bbox,
        order=order,
        heading_path=heading_path,
        locator=locator,
        table_data=table_data,
        metadata=metadata or {},
    )


def _bbox(value: object) -> tuple[float, float, float, float] | None:
    if not isinstance(value, (tuple, list)) or len(value) != 4:
        return None
    converted = tuple(float(item) for item in value)
    return cast(tuple[float, float, float, float], converted)


def _is_repeated_block(text: str, repeated: set[str]) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return bool(lines) and all(line in repeated for line in lines)


def _extract_tables(page: Any) -> list[dict[str, Any]]:
    finder = getattr(page, "find_tables", None)
    if not callable(finder):
        return []
    try:
        tables = finder().tables
    except (AttributeError, RuntimeError, ValueError):
        return []
    results: list[dict[str, Any]] = []
    for table in tables:
        rows = [
            ["" if cell is None else str(cell).strip() for cell in row] for row in table.extract()
        ]
        if rows:
            results.append(
                {
                    "rows": rows,
                    "bbox": tuple(float(value) for value in table.bbox),
                }
            )
    return results


def _render_table(rows: list[list[str]]) -> str:
    return "\n".join(" | ".join(cell for cell in row) for row in rows)


def _table_html(rows: list[list[str]]) -> str:
    escaped = [
        "<tr>" + "".join(f"<td>{_escape_html(cell)}</td>" for cell in row) + "</tr>" for row in rows
    ]
    return "<table>" + "".join(escaped) + "</table>"


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def _write_text(root: Path, relative_path: str, content: str) -> tuple[str, str, str]:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    asset_type = Path(relative_path).stem.split(".")[0]
    return asset_type, relative_path, hashlib.sha256(content.encode("utf-8")).hexdigest()


def _write_images(
    target: Path,
    document: CanonicalDocument,
    source_path: Path,
) -> list[tuple[str, str, str]]:
    image_elements = [item for item in document.elements if item.element_type is ElementType.IMAGE]
    if not image_elements:
        return []
    fitz = _fitz()
    assets: list[tuple[str, str, str]] = []
    with fitz.open(source_path) as source:
        for element in image_elements:
            xref = int(element.metadata["xref"])
            extracted = source.extract_image(xref)
            data = extracted.get("image")
            if not isinstance(data, bytes):
                continue
            extension = str(extracted.get("ext", "bin"))
            relative_path = f"images/{element.element_id}.{extension}"
            path = target / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            assets.append(("image", relative_path, hashlib.sha256(data).hexdigest()))
    return assets


def _split_legacy(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + LEGACY_CHUNK_SIZE)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - LEGACY_CHUNK_OVERLAP
    return chunks


__all__ = ["PARSER_VERSION", "parse_document", "parse_pdf", "write_derived_assets"]
