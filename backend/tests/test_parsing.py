from pathlib import Path

import fitz
import pytest

from ped_agent.parsing import parse_pdf


def create_pdf(path: Path) -> None:
    with fitz.open() as document:
        for page_number in range(1, 4):
            page = document.new_page()
            page.insert_text((72, 36), "Repeated Header")
            page.insert_text((72, 90), f"Page {page_number} pedestrian evidence " + "flow " * 120)
            page.insert_text((72, 760), "Repeated Footer")
        document.save(path)


def test_parser_removes_repeated_edges_and_preserves_page_locator(tmp_path: Path) -> None:
    pdf = tmp_path / "sample.pdf"
    create_pdf(pdf)

    chunks = parse_pdf(
        pdf,
        resource_id="paper-parser-2026",
        version_id="b" * 64,
    )

    assert chunks
    assert all("Repeated Header" not in item.text for item in chunks)
    assert all("Repeated Footer" not in item.text for item in chunks)
    assert chunks[0].locator == "p.1"
    assert max(len(item.text) for item in chunks) <= 1200


def test_parser_extracts_regulation_clause_locator(tmp_path: Path) -> None:
    pdf = tmp_path / "regulation.pdf"
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text(
            (72, 72),
            "第五条 安全出口附近应避免形成高密度拥堵。",
            fontname="china-s",
        )
        document.save(pdf)

    chunks = parse_pdf(
        pdf,
        resource_id="reg-parser-2026",
        version_id="d" * 64,
        detect_clauses=True,
    )

    assert chunks[0].locator == "第五条 / p.1"
    assert chunks[0].section == "第五条"


def test_parser_stops_before_reference_section(tmp_path: Path) -> None:
    pdf = tmp_path / "references.pdf"
    with fitz.open() as document:
        first = document.new_page()
        first.insert_text((72, 72), "Observed pedestrian density evidence.")
        second = document.new_page()
        second.insert_text((72, 72), "References")
        second.insert_text((72, 100), "Unrelated cited title and author names.")
        document.save(pdf)

    chunks = parse_pdf(
        pdf,
        resource_id="paper-references-2026",
        version_id="e" * 64,
    )

    assert [item.locator for item in chunks] == ["p.1"]
    assert all("Unrelated cited title" not in item.text for item in chunks)


def test_parser_rejects_pdf_without_indexable_text(tmp_path: Path) -> None:
    pdf = tmp_path / "blank.pdf"
    with fitz.open() as document:
        document.new_page()
        document.save(pdf)

    with pytest.raises(ValueError, match="no indexable text"):
        parse_pdf(pdf, resource_id="paper-blank-2026", version_id="f" * 64)
