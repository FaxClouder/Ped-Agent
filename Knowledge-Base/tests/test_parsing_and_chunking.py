from __future__ import annotations

from pathlib import Path

import fitz

from ped_knowledge.chunking import HierarchicalChunker
from ped_knowledge.contracts import ChunkLevel, ElementType
from ped_knowledge.parsing import parse_document


class FakeOCR:
    def extract_page_text(self, path: Path, page_number: int) -> str:
        return f"OCR recovered page {page_number} from {path.name}"


def test_canonical_parser_records_page_elements_and_observable_ocr(tmp_path: Path) -> None:
    pdf = tmp_path / "mixed.pdf"
    with fitz.open() as document:
        text_page = document.new_page()
        text_page.insert_text((72, 72), "1 Introduction", fontsize=18)
        text_page.insert_text((72, 110), "Pedestrian flow evidence and measurement details.")
        document.new_page()
        document.save(pdf)

    canonical, report = parse_document(
        pdf,
        resource_id="paper-structured",
        version_id="a" * 64,
        ocr_gateway=FakeOCR(),
    )

    assert report.page_count == 2
    assert report.ocr_page_count == 1
    assert report.empty_pages == ()
    assert any(item.element_type is ElementType.HEADING for item in canonical.elements)
    assert any(item.element_type is ElementType.OCR_TEXT for item in canonical.elements)
    assert canonical.pages[1].ocr_applied is True


def test_parent_child_chunk_ids_are_deterministic(tmp_path: Path) -> None:
    pdf = tmp_path / "document.pdf"
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "2 Method", fontsize=18)
        for index in range(12):
            page.insert_text(
                (72, 110 + index * 24),
                f"Paragraph {index} describes pedestrian density speed and flow observations.",
            )
        document.save(pdf)
    canonical, _ = parse_document(
        pdf,
        resource_id="paper-deterministic",
        version_id="b" * 64,
    )
    chunker = HierarchicalChunker()

    first = chunker.chunk(canonical)
    second = chunker.chunk(canonical)

    assert [item.chunk_id for item in first] == [item.chunk_id for item in second]
    parents = [item for item in first if item.chunk_level is ChunkLevel.PARENT]
    children = [item for item in first if item.chunk_level is ChunkLevel.CHILD]
    assert parents and children
    assert {item.parent_chunk_id for item in children}.issubset({item.chunk_id for item in parents})
