from __future__ import annotations

import io
import json
import zipfile

import pytest

from ped_knowledge.contracts import ElementType
from ped_knowledge.parsing.adobe import parse_adobe_zip


def _sample_zip() -> bytes:
    payload = {
        "version": "1.1.0",
        "pages": [
            {"page_number": 0, "width": 600, "height": 800, "is_scanned": False},
            {"page_number": 1, "width": 600, "height": 800, "is_scanned": False},
        ],
        "elements": [
            {"Path": "//Document/Title", "Page": 0, "Text": "Flow Study", "Bounds": [10, 700, 200, 730]},
            {"Path": "//Document/Sect/H1", "Page": 0, "Text": "1 Results"},
            {"Path": "//Document/Sect/P", "Page": 0, "Text": "First column."},
            {"Path": "//Document/Sect/P[2]", "Page": 0, "Text": "Second column."},
            {"Path": "//Document/Sect/Table", "Page": 1, "filePaths": ["tables/table.png"]},
            {"Path": "//Document/Sect/Table/TR/TH/P", "Page": 1, "Text": "Density"},
            {"Path": "//Document/Sect/Table/TR/TH[2]/P", "Page": 1, "Text": "Speed"},
            {"Path": "//Document/Sect/Table/TR[2]/TD/P", "Page": 1, "Text": "2.1"},
            {"Path": "//Document/Sect/Table/TR[2]/TD[2]/P", "Page": 1, "Text": "1.4"},
            {"Path": "//Document/Sect/Figure", "Page": 1, "filePaths": ["figures/chart.png"]},
        ],
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("structuredData.json", json.dumps(payload))
        archive.writestr("figures/chart.png", b"figure-bytes")
        archive.writestr("tables/table.png", b"table-bytes")
    return output.getvalue()


def test_adobe_zip_preserves_order_page_mapping_table_and_assets() -> None:
    canonical, report, binaries = parse_adobe_zip(
        _sample_zip(), resource_id="paper-adobe", version_id="a" * 64
    )

    assert [item.text for item in canonical.elements if item.element_type is ElementType.PARAGRAPH] == [
        "First column.", "Second column."
    ]
    assert canonical.elements[0].bbox == (10.0, 70.0, 200.0, 100.0)
    table = next(item for item in canonical.elements if item.element_type is ElementType.TABLE)
    assert table.page_number == 2
    assert table.table_data == [["Density", "Speed"], ["2.1", "1.4"]]
    assert table.text == "Density | Speed\n2.1 | 1.4"
    assert all(item.page_number >= 1 for item in canonical.elements)
    assert report.page_count == 2
    assert report.table_count == 1
    assert report.image_count == 1
    assert binaries["adobe/figures/chart.png"] == b"figure-bytes"
    assert binaries["adobe/tables/table.png"] == b"table-bytes"
    assert binaries["adobe/extract.zip"] == _sample_zip()


def test_adobe_zip_rejects_missing_structured_data() -> None:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("other.json", "{}")
    with pytest.raises(ValueError, match="structuredData.json"):
        parse_adobe_zip(output.getvalue(), resource_id="paper-adobe", version_id="a" * 64)

from ped_knowledge.parsing.adobe import load_adobe_credentials


def test_missing_adobe_credentials_has_actionable_error(tmp_path) -> None:
    with pytest.raises(RuntimeError, match="PDF_SERVICES_CLIENT_ID"):
        load_adobe_credentials(tmp_path / "missing.json", environment={})


def test_adobe_credentials_load_from_local_json_without_exposing_values(tmp_path) -> None:
    path = tmp_path / "credentials.json"
    path.write_text(json.dumps({"client_credentials": {"client_id": "id", "client_secret": "secret"}}))
    assert load_adobe_credentials(path, environment={}) == ("id", "secret")


def test_adobe_zip_rejects_empty_asset_path() -> None:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr(
            "structuredData.json",
            json.dumps({
                "pages": [{"page_number": 0, "width": 100, "height": 100}],
                "elements": [
                    {"Path": "//Document/P", "Page": 0, "Text": "Text"},
                    {"Path": "//Document/Figure", "Page": 0, "filePaths": [""]},
                ],
            }),
        )
    with pytest.raises(ValueError, match="unsafe asset path"):
        parse_adobe_zip(output.getvalue(), resource_id="paper-adobe", version_id="a" * 64)


def test_adobe_zip_rejects_windows_separator_traversal() -> None:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("structuredData.json", json.dumps({
            "pages": [{"page_number": 0, "width": 100, "height": 100}],
            "elements": [
                {"Path": "//Document/P", "Page": 0, "Text": "Text"},
                {"Path": "//Document/Figure", "Page": 0, "filePaths": [r"figures/..\\..\\outside.txt"]},
            ],
        }))
        archive.writestr(r"figures/..\\..\\outside.txt", b"bad")
    with pytest.raises(ValueError, match="unsafe asset path"):
        parse_adobe_zip(output.getvalue(), resource_id="paper-adobe", version_id="a" * 64)


def test_adobe_table_preserves_empty_cells() -> None:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("structuredData.json", json.dumps({
            "pages": [{"page_number": 0, "width": 100, "height": 100}],
            "elements": [
                {"Path": "//Document/Table", "Page": 0},
                {"Path": "//Document/Table/TR/TD", "Page": 0, "Text": "A"},
                {"Path": "//Document/Table/TR/TD[2]", "Page": 0},
                {"Path": "//Document/Table/TR/TD[3]", "Page": 0, "Text": "C"},
            ],
        }))
    canonical, _, _ = parse_adobe_zip(output.getvalue(), resource_id="paper-adobe", version_id="a" * 64)
    table = next(item for item in canonical.elements if item.element_type is ElementType.TABLE)
    assert table.table_data == [["A", "", "C"]]


def test_adobe_nested_headings_keep_parent_path() -> None:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("structuredData.json", json.dumps({
            "pages": [{"page_number": 0, "width": 100, "height": 100}],
            "elements": [
                {"Path": "//Document/Title", "Page": 0, "Text": "Study"},
                {"Path": "//Document/H1", "Page": 0, "Text": "Results"},
                {"Path": "//Document/H2", "Page": 0, "Text": "Density"},
                {"Path": "//Document/P", "Page": 0, "Text": "Findings"},
            ],
        }))
    canonical, _, _ = parse_adobe_zip(output.getvalue(), resource_id="paper-adobe", version_id="a" * 64)
    assert canonical.elements[-1].heading_path == ("Study", "Results", "Density")


def test_adobe_zip_rejects_malformed_elements() -> None:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("structuredData.json", json.dumps({
            "pages": [{"page_number": 0, "width": 100, "height": 100}],
            "elements": ["not-an-element"],
        }))
    with pytest.raises(ValueError, match="elements are invalid"):
        parse_adobe_zip(output.getvalue(), resource_id="paper-adobe", version_id="a" * 64)


def test_adobe_zip_rejects_null_element_page() -> None:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("structuredData.json", json.dumps({
            "pages": [{"page_number": 0, "width": 100, "height": 100}],
            "elements": [{"Path": "//Document/P", "Page": None, "Text": "Text"}],
        }))
    with pytest.raises(ValueError, match="element page"):
        parse_adobe_zip(output.getvalue(), resource_id="paper-adobe", version_id="a" * 64)
