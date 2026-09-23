from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

import fitz
import pytest

from ped_knowledge.parsing.compare import write_comparison


def test_comparison_writes_separate_review_files_and_preserves_existing_output(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "1 Results")
        page.insert_text((72, 100), "Measured flow increased.")
        document.save(pdf)
    payload = {
        "version": "1.1.0",
        "pages": [{"page_number": 0, "width": 595, "height": 842, "is_scanned": False}],
        "elements": [
            {"Path": "//Document/Sect/H1", "Page": 0, "Text": "1 Results"},
            {"Path": "//Document/Sect/P", "Page": 0, "Text": "Measured flow increased."},
        ],
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("structuredData.json", json.dumps(payload))
    output = tmp_path / "comparison"

    result = write_comparison(pdf, buffer.getvalue(), output, resource_id="paper-test")

    assert result["source_sha256"] == hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert result["adobe"]["parser_version"] == "adobe-pdf-extract-v1"
    assert result["pymupdf"]["parser_version"] == "pymupdf-structured-v2"
    assert (output / "adobe-elements.txt").is_file()
    assert (output / "pymupdf-elements.txt").is_file()
    assert (output / "comparison.json").is_file()
    assert (output / "adobe-extract.zip").read_bytes() == buffer.getvalue()
    with pytest.raises(FileExistsError):
        write_comparison(pdf, buffer.getvalue(), output, resource_id="paper-test")
