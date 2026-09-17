from __future__ import annotations

from pathlib import Path

import fitz

from ped_knowledge.chunking import HierarchicalChunker
from ped_knowledge.contracts import (
    CanonicalDocument,
    CanonicalPage,
    ChunkingPolicy,
    ChunkLevel,
    DocumentElement,
    ElementType,
)
from ped_knowledge.parsing import parse_document


class FakeOCR:
    def extract_page_text(self, path: Path, page_number: int) -> str:
        return f"OCR recovered page {page_number} from {path.name}"


class WordTokenCounter:
    fingerprint = "word-counter-v1"

    def __init__(self) -> None:
        self._tokens: list[str] = []

    def encode(self, text: str) -> list[int]:
        self._tokens = text.split()
        return list(range(len(self._tokens)))

    def decode(self, token_ids: list[int]) -> str:
        return " ".join(self._tokens[token_id] for token_id in token_ids)

    def count(self, text: str) -> int:
        return len(text.split())


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


def test_injected_counter_controls_child_limit_and_provenance() -> None:
    text = " ".join(f"token{index}" for index in range(130))
    document = CanonicalDocument(
        resource_id="paper-token-budget",
        version_id="c" * 64,
        source_hash="c" * 64,
        parser_version="test",
        pages=[CanonicalPage(page_number=1, width=100, height=100, element_ids=("e1",))],
        elements=[
            DocumentElement(
                element_id="e1",
                element_type=ElementType.PARAGRAPH,
                text=text,
                page_number=1,
                order=0,
                locator="p.1",
            )
        ],
    )
    counter = WordTokenCounter()
    chunker = HierarchicalChunker(
        ChunkingPolicy(
            policy_version="parent-child-v2",
            parent_target_tokens=200,
            parent_max_tokens=250,
            child_target_tokens=60,
            child_max_tokens=80,
            child_overlap_tokens=10,
        ),
        token_counter=counter,
    )

    children = [
        item for item in chunker.chunk(document) if item.chunk_level is ChunkLevel.CHILD
    ]

    assert len(children) == 3
    assert all(item.token_count <= 80 for item in children)
    assert all(item.tokenizer_fingerprint == counter.fingerprint for item in children)
    assert children[0].character_start == 0
    assert children[-1].character_end == len(text)


def test_v2_prefers_complete_sentences_and_overlaps_whole_units() -> None:
    sentences = [
        " ".join(f"s{sentence}w{word}" for word in range(30)) + "."
        for sentence in range(4)
    ]
    text = " ".join(sentences)
    document = CanonicalDocument(
        resource_id="paper-sentence-boundaries",
        version_id="d" * 64,
        source_hash="d" * 64,
        parser_version="test",
        pages=[CanonicalPage(page_number=1, width=100, height=100, element_ids=("e1",))],
        elements=[
            DocumentElement(
                element_id="e1",
                element_type=ElementType.PARAGRAPH,
                text=text,
                page_number=1,
                order=0,
                locator="p.1",
            )
        ],
    )
    chunker = HierarchicalChunker(
        ChunkingPolicy(
            policy_version="parent-child-v2",
            parent_target_tokens=200,
            parent_max_tokens=250,
            child_target_tokens=50,
            child_max_tokens=80,
            child_overlap_tokens=10,
        ),
        token_counter=WordTokenCounter(),
    )

    children = [
        item for item in chunker.chunk(document) if item.chunk_level is ChunkLevel.CHILD
    ]

    assert len(children) == 3
    assert all(child.text.endswith(".") for child in children)
    assert all(child.token_count <= 80 for child in children)
    assert sentences[1] in children[0].text
    assert children[1].text.startswith(sentences[1])
    assert all(child.locator == "p.1" for child in children)


def test_v2_marks_token_fallback_for_oversized_sentence() -> None:
    text = " ".join(f"oversized{index}" for index in range(100)) + "."
    document = CanonicalDocument(
        resource_id="paper-hard-split",
        version_id="e" * 64,
        source_hash="e" * 64,
        parser_version="test",
        pages=[CanonicalPage(page_number=2, width=100, height=100, element_ids=("e1",))],
        elements=[
            DocumentElement(
                element_id="e1",
                element_type=ElementType.PARAGRAPH,
                text=text,
                page_number=2,
                order=0,
                locator="p.2",
            )
        ],
    )
    chunker = HierarchicalChunker(
        ChunkingPolicy(
            policy_version="parent-child-v2",
            parent_target_tokens=200,
            parent_max_tokens=250,
            child_target_tokens=60,
            child_max_tokens=80,
            child_overlap_tokens=10,
        ),
        token_counter=WordTokenCounter(),
    )

    children = [
        item for item in chunker.chunk(document) if item.chunk_level is ChunkLevel.CHILD
    ]

    assert len(children) == 2
    assert all(child.token_count <= 80 for child in children)
    assert all(child.hard_split for child in children)
    assert children[0].character_start == 0
    assert children[-1].character_end == len(text)
