"""Adobe PDF Extract adapter for canonical knowledge documents."""

from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from ped_knowledge.contracts import (
    AssetRef,
    CanonicalDocument,
    CanonicalPage,
    DocumentElement,
    ElementType,
    ParseReport,
)

PARSER_VERSION = "adobe-pdf-extract-v1"
_TABLE_CELL = re.compile(r"^(?P<row>.+/TR(?:\[\d+\])?)/(?P<cell>TH|TD)(?:\[\d+\])?(?:/|$)")
_HEADING = re.compile(r"H[1-6]$")
_CAPTION = re.compile(r"^(?:fig(?:ure)?\.?|table|图|表)\s*\d+", re.IGNORECASE)


def parse_adobe_zip(
    archive_bytes: bytes, *, resource_id: str, version_id: str
) -> tuple[CanonicalDocument, ParseReport, dict[str, bytes]]:
    """Convert Adobe's ZIP into the repository's ordered canonical document."""
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as exc:
        raise ValueError("Adobe response is not a ZIP archive") from exc
    with archive:
        if "structuredData.json" not in archive.namelist():
            raise ValueError("Adobe response has no structuredData.json")
        try:
            source = json.loads(archive.read("structuredData.json"))
        except (json.JSONDecodeError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
            raise ValueError("Adobe structuredData.json is invalid") from exc
        if not isinstance(source, dict):
            raise ValueError("Adobe structuredData.json is not an object")
        page_data = source.get("pages", [])
        raw_elements = source.get("elements", [])
        if not isinstance(page_data, list) or not page_data:
            raise ValueError("Adobe response has no pages")
        if not isinstance(raw_elements, list) or any(
            not isinstance(item, dict) for item in raw_elements
        ):
            raise ValueError("Adobe response elements are invalid")
        if any(not isinstance(page, dict) for page in page_data):
            raise ValueError("Adobe response pages are invalid")

        try:
            pages = [
                CanonicalPage(
                    page_number=int(page["page_number"]) + 1,
                    width=float(page["width"]),
                    height=float(page["height"]),
                )
                for page in page_data
            ]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Adobe response pages are invalid") from exc
        page_by_number = {page.page_number: page for page in pages}
        if len(page_by_number) != len(pages):
            raise ValueError("Adobe response has duplicate pages")
        table_entries = [item for item in raw_elements if _last_segment(str(item.get("Path", ""))) == "Table"]
        table_paths = [str(item["Path"]) for item in table_entries]
        elements: list[DocumentElement] = []
        assets: list[AssetRef] = []
        binaries: dict[str, bytes] = {"adobe/extract.zip": archive_bytes}
        page_ids: dict[int, list[str]] = defaultdict(list)
        heading_path: tuple[str, ...] = ()
        table_count = 0
        image_count = 0
        reached_references = False

        for raw in raw_elements:
            path = str(raw.get("Path", ""))
            if any(path.startswith(table_path + "/") for table_path in table_paths):
                continue
            try:
                page_number = int(raw.get("Page", -1)) + 1
            except (TypeError, ValueError) as exc:
                raise ValueError("Adobe element page is invalid") from exc
            if page_number not in page_by_number:
                raise ValueError(f"Adobe element references unknown page {page_number}")
            kind = _last_segment(path)
            text = str(raw.get("Text") or "").strip()
            if text.casefold() in {"references", "bibliography", "参考文献"}:
                reached_references = True
            if reached_references:
                break
            if kind == "Table":
                element_type = ElementType.TABLE
                table_data = _table_rows(path, raw_elements)
                text = "\n".join(" | ".join(row) for row in table_data)
                table_count += 1
            elif kind == "Figure":
                element_type = ElementType.IMAGE
                table_data = None
                image_count += 1
            elif text:
                table_data = None
                if kind == "Title":
                    element_type = ElementType.TITLE
                    heading_path = (text,)
                elif _HEADING.fullmatch(kind):
                    element_type = ElementType.HEADING
                    heading_path = heading_path[: int(kind[1])] + (text,)
                elif _CAPTION.match(text):
                    element_type = ElementType.CAPTION
                elif "/L/" in path or kind in {"Lbl", "LBody"}:
                    element_type = ElementType.LIST
                else:
                    element_type = ElementType.PARAGRAPH
            else:
                continue
            element_id = hashlib.sha256(
                f"{resource_id}|{version_id}|{len(elements)}|{path}|{text}".encode("utf-8")
            ).hexdigest()[:24]
            element = DocumentElement(
                element_id=element_id,
                element_type=element_type,
                text=text,
                page_number=page_number,
                bbox=_top_left_bbox(raw.get("Bounds"), page_by_number[page_number].height),
                order=len(elements),
                heading_path=heading_path,
                locator=f"p.{page_number}",
                table_data=table_data,
                metadata={"adobe_path": path, "adobe_version": str(source.get("version", ""))},
            )
            elements.append(element)
            page_ids[page_number].append(element_id)
            file_paths = raw.get("filePaths", [])
            if not isinstance(file_paths, list) or any(
                not isinstance(file_path, str) for file_path in file_paths
            ):
                raise ValueError("Adobe element filePaths are invalid")
            for file_path in file_paths:
                validated = _asset_path(file_path)
                if validated not in archive.namelist():
                    raise ValueError(f"Adobe response missing asset {validated}")
                relative_path = f"adobe/{validated}"
                try:
                    binaries[relative_path] = archive.read(validated)
                except zipfile.BadZipFile as exc:
                    raise ValueError(f"Adobe response asset is corrupted: {validated}") from exc
                assets.append(
                    AssetRef(
                        asset_type="image" if kind == "Figure" else "table_rendition",
                        path=relative_path,
                        page_number=page_number,
                        element_id=element_id,
                    )
                )

    if not any(item.text for item in elements):
        raise ValueError("Adobe response produced no indexable text")
    populated = {item.page_number for item in elements if item.text}
    scanned = {int(item["page_number"]) + 1 for item in page_data if item.get("is_scanned")}
    empty = tuple(page.page_number for page in pages if page.page_number not in populated)
    for page in pages:
        page.element_ids = tuple(page_ids[page.page_number])
        page.ocr_applied = page.page_number in scanned and page.page_number in populated
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
        text_page_count=len(populated - scanned),
        ocr_page_count=len(populated & scanned),
        empty_pages=empty,
        element_count=len(elements),
        table_count=table_count,
        image_count=image_count,
        degraded=bool(empty),
        degradation_reasons=("pages_without_extractable_text",) if empty else (),
        manual_review_pages=empty,
    )
    return canonical, report, binaries


def _last_segment(path: str) -> str:
    return re.sub(r"\[\d+\]$", "", path.rsplit("/", 1)[-1])


def _top_left_bbox(value: Any, page_height: float) -> tuple[float, float, float, float] | None:
    if not isinstance(value, list) or len(value) != 4:
        return None
    try:
        left, bottom, right, top = (float(item) for item in value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Adobe element bounds are invalid") from exc
    return (left, page_height - top, right, page_height - bottom)


def _asset_path(value: Any) -> str:
    raw = str(value)
    if "\\" in raw:
        raise ValueError("Adobe response contains an unsafe asset path")
    path = PurePosixPath(raw)
    if not path.parts or path.is_absolute() or ".." in path.parts or path.parts[0] not in {"figures", "tables"}:
        raise ValueError("Adobe response contains an unsafe asset path")
    return str(path)


def _table_rows(table_path: str, elements: list[dict[str, Any]]) -> list[list[str]]:
    rows: dict[str, dict[str, str]] = {}
    for item in elements:
        path = str(item.get("Path", ""))
        if not path.startswith(table_path + "/"):
            continue
        match = _TABLE_CELL.match(path)
        if not match:
            continue
        text = str(item.get("Text") or "").strip()
        row = rows.setdefault(match.group("row"), {})
        cell_path = path[: match.end()].rstrip("/")
        row.setdefault(cell_path, "")
        if text:
            row[cell_path] = " ".join(filter(None, (row[cell_path], text)))
    return [list(cells.values()) for cells in rows.values()]

def load_adobe_credentials(
    credential_path: Path | None = None, *, environment: dict[str, str] | None = None
) -> tuple[str, str]:
    """Read credentials from process environment or an ignored local JSON file."""
    import os

    values = environment if environment is not None else os.environ
    client_id = values.get("PDF_SERVICES_CLIENT_ID", "")
    client_secret = values.get("PDF_SERVICES_CLIENT_SECRET", "")
    if client_id and client_secret:
        return client_id, client_secret
    path = credential_path or Path(__file__).parents[3] / "local" / "pdfservices-api-credentials.json"
    if not path.is_file():
        raise RuntimeError(
            "Adobe credentials are missing; set PDF_SERVICES_CLIENT_ID and "
            "PDF_SERVICES_CLIENT_SECRET or provide Knowledge-Base/local/pdfservices-api-credentials.json"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        credentials = payload["client_credentials"]
        client_id = str(credentials["client_id"])
        client_secret = str(credentials["client_secret"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RuntimeError("Adobe credentials file is invalid") from exc
    if not client_id or not client_secret:
        raise RuntimeError("Adobe credentials file is incomplete")
    return client_id, client_secret


def extract_adobe_pdf(path: Path, *, credential_path: Path | None = None) -> bytes:
    """Submit a PDF to Adobe Extract and return its ZIP without persisting secrets."""
    try:
        from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
        from adobe.pdfservices.operation.exception.exceptions import (
            SdkException,
            ServiceApiException,
            ServiceUsageException,
        )
        from adobe.pdfservices.operation.pdf_services import PDFServices
        from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
        from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
        from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
        from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
        from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_renditions_element_type import ExtractRenditionsElementType
        from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult
    except ImportError as exc:
        raise RuntimeError("Install ped-knowledge[adobe] to use Adobe PDF Extract") from exc

    client_id, client_secret = load_adobe_credentials(credential_path)
    try:
        service = PDFServices(
            ServicePrincipalCredentials(client_id=client_id, client_secret=client_secret)
        )
        source = service.upload(input_stream=path.read_bytes(), mime_type=PDFServicesMediaType.PDF)
        options = ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
            elements_to_extract_renditions=[
                ExtractRenditionsElementType.TABLES,
                ExtractRenditionsElementType.FIGURES,
            ],
        )
        location = service.submit(ExtractPDFJob(input_asset=source, extract_pdf_params=options))
        result = service.get_job_result(location, ExtractPDFResult)
        return service.get_content(result.get_result().get_resource()).get_input_stream()
    except (SdkException, ServiceApiException, ServiceUsageException) as exc:
        raise RuntimeError(f"Adobe PDF Extract failed ({type(exc).__name__})") from exc
