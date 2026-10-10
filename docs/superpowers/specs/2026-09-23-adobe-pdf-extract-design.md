# Adobe PDF Extract optional parser design

_Original design record for the Knowledge-Base Adobe adapter · status: historical_

## Goal

Use Adobe PDF Extract JSON to improve reading order and table extraction in a controlled comparison, while keeping PyMuPDF as the default parser.

## Boundary

- A local ignored credentials file at `Knowledge-Base/local/pdfservices-api-credentials.json` contains only the downloaded Adobe client credentials. No credential value enters Git, logs, reports, or tests.
- Adobe SDK runs only when `ImportService(parser_backend="adobe")` is chosen. The default remains PyMuPDF.
- The adapter converts Adobe's ordered `elements` and zero-based `pages` to `CanonicalDocument` and `ParseReport` with the input SHA-256 as `version_id` and an Adobe parser version.
- Adobe table paths become one table element with text and row data. Figure renditions are saved as derived assets. Raw Adobe response is kept as a local derived ZIP for provenance.
- API errors fail the import without silently switching parsers. Existing active versions remain active after a failed replacement.

## Validation

- Unit tests use a small synthetic Adobe ZIP and cover reading order, page mapping, table rows, figure assets, malformed ZIP, and service selection.
- Run the Knowledge-Base module suite and then all repository tests because the CanonicalDocument contract is consumed by chunking and storage.
- Run one smoke request using the Adobe sample PDF. Compare extracted structure to PyMuPDF without asserting that one parser is inherently more accurate.

## Implementation record (2026-09-23)

The optional adapter, explicit import selection, derived assets, and independent comparison command are implemented. The default parser remains PyMuPDF. The Adobe sample PDF was used for an actual API smoke request; no research-corpus accuracy result is established. Current usage and data boundaries are documented in [`Knowledge-Base/README.md`](../../../Knowledge-Base/README.md) and [`memPed/README.md`](../../../memPed/README.md).
