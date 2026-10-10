# Literature Manifest Readiness Implementation Plan

_已确认设计的实施清单与执行记录 · status: plan_

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible, non-importable readiness table for exactly 104 content-score-passing papers, leaving four temporarily unused papers out of every generated row.

**Architecture:** A new offline governance module joins the five inventories with candidate, screening, citation and journal records by normalized DOI, checks local PDF bytes without importing them, and renders CSV plus a local audit report. The active `IngestionManifest` and `ImportService` are not changed or called.

**Tech Stack:** Python standard-library CSV/JSON/hashlib, PyMuPDF for read-only PDF inspection, pytest, repository Markdown and CSV.

## Global Constraints

- Only 104 `total_score > 65` records get output rows; four `temporarily_not_used` records stay only in existing source tables and count as exclusions.
- No `include` field or importable JSONL in the draft; do not call `ImportService.import_manifest` or build indexes.
- Unknown integrity, rights, publication version, journal match, citation or A/B/X grade stays pending; no fabricated approvals.
- New output paths only: `memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv` and `memPed/knowledge/reports/manifest-readiness-2026-09-23.md`. Never overwrite existing outputs.
- Preserve source/input hashes, algorithm version, file hashes and per-row provenance. Keep executable code out of `memPed/`.
- The checkout contains unrelated uncommitted changes. Stage or commit only new files owned by this task; do not alter historical PDF reports or existing manifests.

## File responsibilities

- `Knowledge-Base/src/ped_knowledge/governance/readiness.py`: read-only joins, checks and deterministic CSV/report rendering. Public entry point: `build_readiness(root: Path) -> ReadinessBuild`.
- `Knowledge-Base/tests/test_manifest_readiness.py`: filtering, missing-value, conflict, hash and no-import behavior.
- `memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv`: generated 104-row review artifact, not a technical Manifest.
- `memPed/knowledge/reports/manifest-readiness-2026-09-23.md`: local audit summary, blockers and input provenance.
- `docs/README.md`: link to plan and local report, preserving its existing edits.

---

### Task 1: Readiness join and exclusion logic

**Files:**
- Create: `Knowledge-Base/src/ped_knowledge/governance/readiness.py`
- Create: `Knowledge-Base/tests/test_manifest_readiness.py`

**Interfaces:** `build_readiness(root: Path) -> ReadinessBuild`, where `ReadinessBuild.rows` contains dictionaries using `READINESS_FIELDS`, `excluded_count` is an integer, and `input_hashes` maps repository-relative input paths to SHA-256.

- [x] **Step 1: Write failing tests.** Build a tiny `tmp_path` fixture with two inventory/candidate/screening records: score 66 / `pass` and score 65 / `temporarily_not_used_content_at_most_65`; five batch inventory CSVs exist, four empty. Add assertions:

  ```python
  from ped_knowledge.governance.readiness import build_readiness

  result = build_readiness(tmp_path)
  assert [row["doi"] for row in result.rows] == ["10.1000/approved"]
  assert result.excluded_count == 1
  assert "include" not in result.rows[0]
  assert "10.1000/held" not in result.render_csv()
  ```

  Also assert duplicate DOI or absent candidate produces a named build issue rather than a silently skipped record. Tests must not call the import pipeline.
- [x] **Step 2: Run red.** Set `PYTHONPATH` to all four `src` directories, then run `python -m pytest Knowledge-Base/tests/test_manifest_readiness.py -q`. Expected failure: `readiness` module or entry point missing.
- [x] **Step 3: Implement minimal join.** Normalize DOI by trim/casefold, read each table with `csv.DictReader`, reject duplicate keys, read all five inventories, and select only screen rows with integer score `> 65`, `fulltext_screen=pass` and non-held decision. Fail visibly on a mismatch between score/status or a missing one-to-one source record. Keep row order by batch number and inventory order. Define `ReadinessBuild.render_csv()` using `csv.DictWriter` and `io.StringIO` so it cannot write files itself.
- [x] **Step 4: Run green.** Rerun the focused test and `git diff --check` on new code. Expected: tests pass, no importable JSONL created.

### Task 2: Read-only PDF, citation, journal and governance fields

**Files:**
- Modify: `Knowledge-Base/src/ped_knowledge/governance/readiness.py`
- Modify: `Knowledge-Base/tests/test_manifest_readiness.py`

**Interfaces:** Each row adds `source_path`, `inventory_sha256`, `actual_sha256`, `hash_status`, `pdf_status`, `page_count`, `publication_status`, `citation_count`, `citation_source`, `citation_checked_at`, `journal_match_status`, `journal_best_rank`, `integrity_status`, `rights_status`, `quality_tier`, `manual_review_status`, and `blocker_codes`.

- [x] **Step 1: Write failing tests.** Use one valid locally created PDF fixture and a known SHA to expect `hash_status=match`, `pdf_status=readable`, a positive page count, and retained citation source/value/date. Add missing/incorrect SHA and absent citation cases expecting explicit blockers. Add a row with `pending_manual_content_review` and assert the blocker is retained even when the score passes. Assert unknown rights/integrity and blank quality tier remain `pending`/blank.
- [x] **Step 2: Run red.** Rerun the focused test; expected failures are missing fields or incorrect blocker values, not fixture/setup errors.
- [x] **Step 3: Implement minimal checks.** Use `hashlib.sha256` over source files and `pymupdf.open` read-only for page count/text access. Use the inventory SHA as an input, never rewrite it. Match candidate/citation by DOI. Match journal venue by normalized exact name plus four explicit source-backed aliases; calculate best available rank only from verified rows and mark unmatched names pending. Never infer formal publication or permission from a DOI/PDF alone. Add `input_hashes` for the nine CSV inputs: five inventories plus candidate, screening, citation and journal metrics.
- [x] **Step 4: Run green.** Focused tests pass. Inspect resulting fields for one complete, one missing-citation, one identity-held and one manual-review fixture.

### Task 3: Generate and verify local outputs

**Files:**
- Create: `memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv`
- Create: `memPed/knowledge/reports/manifest-readiness-2026-09-23.md`
- Modify: `docs/README.md`

**Interfaces:** `ReadinessBuild.render_csv() -> str` and `ReadinessBuild.render_report() -> str`; generation is read-only until these strings are applied to new files.

- [x] **Step 1: Run a read-only build against the workspace.** Call `build_readiness(Path.cwd())`, print its row count, excluded count, blocker distribution and SHA input fingerprints. Expected: 104 rows, 4 excluded, zero duplicate DOI/resource_id/SHA and no source table mutation.
- [x] **Step 2: Create outputs with `apply_patch`.** Capture the deterministic CSV and report text from `render_csv()` and `render_report()` and apply each to a new file only after `Test-Path` confirms it does not exist. The report has one H1, italic context with `status: current`, per-batch counts, blocker counts, SHA provenance and a statement that no import occurred. Do not emit any row or DOI for the four held papers.
- [x] **Step 3: Verify saved artifacts.** Independently parse the CSV: 104 rows, 104 unique DOI/resource_id/SHA, no `include` column, four held DOI absent, all source paths exist, actual hashes agree with the recorded status. Confirm input files have the same SHA-256 as at the start and the two existing Manifest files remain unchanged. Check report links and `git diff --check` on scoped paths.
- [x] **Step 4: Test and hand off.** Run `Knowledge-Base/tests/test_manifest_readiness.py` first and then the repository's full suite:

  ```powershell
  $env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
  .\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
  ```

  Report actual counts and any blockers. Do not call `preflight_manifest` on the draft, import PDFs, or mark `include=true`.
