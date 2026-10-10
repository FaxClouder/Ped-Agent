# Frontiers in Physics Removal and JIF Score Retirement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the Frontiers in Physics candidate and active assets while retiring numeric JIF values without changing JIF quartile admission.

**Architecture:** Treat `journal_metrics.csv` and the governed candidate records as current state, Batch 3 manifests as active ingestion state, and dated reports as historical evidence. Migrate the CSV schema in place, remove only the exact `b3-10` active assets, and annotate rather than erase historical evidence.

**Tech Stack:** CSV/JSON/JSONL, Markdown, PowerShell, Python standard library, pytest.

## Global Constraints

- Preserve JIF rank, quartile, and percentile; remove only numeric `jif_value`.
- Preserve JCI value, rank, quartile, and percentile.
- Do not rebuild indexes or chunks.
- Do not overwrite unrelated user changes in the dirty worktree.
- Delete only the verified `fphy-11-1200927.pdf` target after path and SHA-256 checks.

---

### Task 1: Migrate journal metrics and candidate audit records

**Files:**
- Modify: `memPed/knowledge/literature/records/journal_metrics.csv`
- Modify: `memPed/knowledge/literature/records/candidates.csv`
- Modify: `memPed/knowledge/literature/records/exclusions.csv`

**Interfaces:**
- Consumes: the 28-column journal metrics table and the `b3-meta-10` candidate.
- Produces: a 27-column table without `jif_value`, no Frontiers metrics/candidate row, and one exclusion audit row.

- [x] **Step 1: Run a pre-change assertion that proves the old state is present**

Run a Python CSV check that asserts `jif_value` and `Frontiers in Physics` are absent.

Expected: FAIL because both are currently present.

- [x] **Step 2: Apply the targeted CSV edits**

Remove the `jif_value` header and corresponding cell from every metric row, remove the Frontiers metric and candidate rows, and append this exclusion:

```csv
b3-10,10.3389/fphy.2023.1200927,journal_screening,user_excluded_venue,Frontiers in Physics excluded by explicit user decision after journal review,2026-09-21,User
```

- [x] **Step 3: Verify CSV shape and contents**

Expected: 27 metric columns, no malformed rows, no Frontiers activity row, and exactly one `b3-10` exclusion.

### Task 2: Remove active Batch 3 records and PDF

**Files:**
- Modify: `memPed/knowledge/batch-3-incoming/batch3_ingestion_manifest.jsonl`
- Modify: `memPed/knowledge/batch-3-incoming/batch3_extraction.json`
- Delete: `memPed/knowledge/batch-3-incoming/fphy-11-1200927.pdf`

**Interfaces:**
- Consumes: resource ID `b3-10`, DOI `10.3389/fphy.2023.1200927`, and SHA-256 `92a8c1005d9d9568dcea4233dcee0b76c0e6a882bb35c243941230bfabb91572`.
- Produces: active Batch 3 records without the target and a filesystem without the target PDF.

- [x] **Step 1: Verify exact delete target**

Resolve the absolute path inside `memPed/knowledge/batch-3-incoming`, confirm the filename and SHA-256, and record the file size.

- [x] **Step 2: Remove active manifest and extraction entries**

Delete only the matching JSONL record and JSON array object. Parse both files after editing.

- [x] **Step 3: Delete the verified PDF**

Use `Remove-Item -LiteralPath` only after the path checks pass.

- [x] **Step 4: Verify active state**

Expected: 16 manifest records, no target in active extraction, and `Test-Path` returns false for the PDF.

### Task 3: Synchronize current rules and historical evidence

**Files:**
- Modify: `Knowledge-Base/README.md`
- Modify: `memPed/knowledge/collection_standard.md`
- Modify: `docs/superpowers/specs/2026-09-21-journal-metrics-schema-design.md`
- Modify: `docs/batch-3-final-manifest.md`
- Modify: `docs/batch-3-pdf-inventory.md`
- Modify: `docs/batch-3-metadata-summary.md`
- Modify: `docs/batch-3-metadata-extraction.json`
- Modify: `docs/batch-3-metadata-table.txt`
- Modify: `docs/batch-3-literature-candidates.md`
- Modify: `docs/knowledge-base-inventory-20260917.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: the approved design and the post-cleanup active record counts.
- Produces: current rules that require numeric JCI only and historical reports that explicitly mark `b3-10` excluded.

- [x] **Step 1: Update current guidance**

State that numeric JCI remains reference metadata, numeric JIF is not collected, and JIF quartiles still participate in admission.

- [x] **Step 2: Update schema documentation**

Remove `jif_value` from the field list and revise the initial-record history to describe the later Frontiers exclusion.

- [x] **Step 3: Annotate historical Batch 3 documents**

Add an audit note that `b3-10` was excluded on 2026-09-21, update current active counts to 16 where applicable, and mark retained item-level references as historical/excluded.

- [x] **Step 4: Validate maintained-document links**

Confirm the new design and plan links resolve from `docs/README.md`.

### Task 4: Final verification

**Files:**
- Test: `Knowledge-Base/tests/test_governance_manifest.py`
- Test: `Knowledge-Base/tests/test_governance_audit.py`

**Interfaces:**
- Consumes: all preceding changes.
- Produces: evidence that CSV/JSON data is consistent and JIF quartile admission remains intact.

- [x] **Step 1: Run data integrity checks**

Check CSV column counts, JSON parsing, JSONL parsing, active record counts, exclusion uniqueness, and absence of the deleted file.

- [x] **Step 2: Run governance tests**

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_governance_manifest.py Knowledge-Base/tests/test_governance_audit.py -q
```

Expected: all selected tests pass.

- [x] **Step 3: Run scoped diff checks**

Run `git diff --check` on task files and verify remaining Frontiers references are historical entries with an exclusion marker.
