# Adobe PDF Extract Optional Parser Implementation Plan

_Implementation checklist for the approved optional Adobe parser · status: plan_

**Goal:** Add a credentials-backed optional Adobe structured parser and validate it against the Adobe sample PDF.

**Architecture:** Keep `ImportService`'s default PyMuPDF path. An Adobe adapter calls the SDK and converts its ZIP into the existing canonical document contract; the derived writer persists provider assets and source provenance.

**Tech Stack:** Python 3.12, pdfservices-sdk 4.2.0, PyMuPDF, Pydantic, pytest.

## Global constraints

- Never commit or print Adobe credentials or research PDFs.
- Preserve source SHA-256, parser version, page locators, and asset hashes.
- Never overwrite an existing research output.

### Task 1: Adobe result conversion

**Files:** `Knowledge-Base/src/ped_knowledge/parsing/adobe.py`, `Knowledge-Base/tests/test_adobe_parsing.py`

- [x] Add a failing synthetic ZIP test for ordered elements, zero-based pages, table cells, and figure assets.
- [x] Implement strict ZIP parsing and conversion to `CanonicalDocument` and `ParseReport`.
- [x] Run `Knowledge-Base/tests/test_adobe_parsing.py` and confirm it passes.

### Task 2: SDK call and credentials

**Files:** `Knowledge-Base/src/ped_knowledge/parsing/adobe.py`, `Knowledge-Base/pyproject.toml`, `Knowledge-Base/README.md`

- [x] Add failing tests for missing credentials and malformed provider responses.
- [x] Implement optional SDK invocation and ignored local credentials file discovery.
- [x] Run the Adobe sample PDF smoke call, saving output under the ignored local directory.

### Task 3: Import integration and derived assets

**Files:** `Knowledge-Base/src/ped_knowledge/ingestion/__init__.py`, `Knowledge-Base/src/ped_knowledge/parsing/__init__.py`, `Knowledge-Base/tests/test_ingestion_pipeline.py`

- [x] Add a failing import test selecting Adobe and verifying derived image, raw ZIP, and Catalog parser version.
- [x] Wire explicit parser selection and provider assets into derived writes.
- [x] Run module tests and the full four-module test suite.
