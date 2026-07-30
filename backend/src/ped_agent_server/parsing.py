from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import fitz

from ped_agent_server.models import CanonicalChunk

PARSER_VERSION = "pedestrian-pdf-v1"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 120
REFERENCE_HEADINGS = {"references", "bibliography", "参考文献"}


def _page_lines(document: fitz.Document) -> list[list[str]]:
    return [
        [line.strip() for line in page.get_text("text").splitlines() if line.strip()]
        for page in document
    ]


def _repeated_edge_lines(pages: list[list[str]]) -> set[str]:
    if len(pages) < 2:
        return set()
    counts: Counter[str] = Counter()
    for lines in pages:
        counts.update(set(lines[:2] + lines[-2:]))
    threshold = max(2, (len(pages) + 1) // 2)
    return {line for line, count in counts.items() if count >= threshold}


def _split_text(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def _clause_locator(text: str, page_number: int) -> tuple[str, str | None]:
    match = re.search(r"第[一二三四五六七八九十百千万0-9.]+条", text)
    if match:
        return f"{match.group(0)} / p.{page_number}", match.group(0)
    return f"p.{page_number}", None


def _clean_page(lines: list[str], repeated: set[str]) -> tuple[str, bool]:
    content: list[str] = []
    reached_references = False
    for line in lines:
        if line.strip().casefold() in REFERENCE_HEADINGS:
            reached_references = True
            break
        if line not in repeated:
            content.append(line)
    return "\n".join(content).strip(), reached_references


def parse_pdf(
    path: Path,
    *,
    resource_id: str,
    version_id: str,
    detect_clauses: bool = False,
) -> list[CanonicalChunk]:
    output: list[CanonicalChunk] = []
    ordinal = 0
    with fitz.open(path) as document:
        if document.needs_pass:
            raise ValueError(f"encrypted PDF is not supported: {path}")
        pages = _page_lines(document)
        repeated = _repeated_edge_lines(pages)
        for page_number, lines in enumerate(pages, start=1):
            cleaned, reached_references = _clean_page(lines, repeated)
            for text in _split_text(cleaned):
                locator, section = (
                    _clause_locator(text, page_number)
                    if detect_clauses
                    else (f"p.{page_number}", None)
                )
                output.append(
                    CanonicalChunk(
                        chunk_id=f"{resource_id}:{version_id[:12]}:{ordinal:05d}",
                        resource_id=resource_id,
                        version_id=version_id,
                        ordinal=ordinal,
                        text=text,
                        page_start=page_number,
                        page_end=page_number,
                        locator=locator,
                        section=section,
                        parser_version=PARSER_VERSION,
                    )
                )
                ordinal += 1
            if reached_references:
                break
    if not output:
        raise ValueError(f"PDF produced no indexable text: {path}")
    return output
