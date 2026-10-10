# Populate Journal Metrics Implementation Plan

> **Historical note (2026-09-21):** The later
> `2026-09-21-remove-frontiers-and-jif-score.md` migration removes `Frontiers in Physics` from
> active records and retires the numeric `jif_value` column. The steps below describe the earlier
> population state and must not be reused as the current schema.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist the seven manually verified journals as nine category-level rows in the journal metrics CSV.

**Architecture:** Replace the legacy journal-level header with the approved long-form schema. Store one row per journal and JCR category, repeat journal-level values where required, and preserve missing evidence as blank fields rather than inferred values.

**Tech Stack:** UTF-8 CSV, PowerShell, Python standard library

## Global Constraints

- Modify only the journal metrics table and maintained-document index for this implementation.
- Do not change admission rules, candidate records, the Catalog, PDFs, chunks, or indexes.
- Use `not_indexed` only for a source that was checked and confirmed absent.
- Keep screenshot-unavailable values blank.

---

### Task 1: Populate the category-level journal metrics table

**Files:**
- Modify: `memPed/knowledge/literature/records/journal_metrics.csv`

**Interfaces:**
- Consumes: the approved schema in `docs/superpowers/specs/2026-09-21-journal-metrics-schema-design.md` and the user-supplied 2025 JCR/CAS screenshots.
- Produces: a CSV keyed by `(venue, jcr_year, jcr_category)` with nine rows covering seven journals.

- [ ] **Step 1: Replace the legacy header**

Use the 28-column header specified by the approved design:

```csv
venue,issn,eissn,edition,publisher,jcr_year,jcr_category,jcr_status,jci_value,jci_rank,jci_quartile,jci_percentile,jif_value,jif_rank,jif_quartile,jif_percentile,total_citations,cas_major_category,cas_major_zone,cas_minor_category,cas_minor_zone,cas_year,cas_status,jci_source,cas_source,verified_at,verified_by,notes
```

- [ ] **Step 2: Add the nine verified category rows**

Add one row each for Physica A, Scientific Reports, Scientific Data, Frontiers in Physics, and Collective Dynamics; add two rows each for Transportation Letters and Physical Review E. Leave unavailable JIF values and identifiers blank. Mark Collective Dynamics as `not_indexed` in both source systems.

- [ ] **Step 3: Validate structure and representative values**

Run:

```powershell
@'
import csv
from pathlib import Path

path = Path("memPed/knowledge/literature/records/journal_metrics.csv")
with path.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

assert len(rows) == 9
assert len({row["venue"] for row in rows}) == 7
keys = [(row["venue"], row["jcr_year"], row["jcr_category"]) for row in rows]
assert len(keys) == len(set(keys))
assert all(not row["jci_quartile"] or row["jci_quartile"] in {"Q1", "Q2", "Q3", "Q4"} for row in rows)
assert all(not row["jif_quartile"] or row["jif_quartile"] in {"Q1", "Q2", "Q3", "Q4"} for row in rows)
assert all(not row["cas_major_zone"] or row["cas_major_zone"] in {"1", "2", "3", "4"} for row in rows)
assert all(not row["cas_minor_zone"] or row["cas_minor_zone"] in {"1", "2", "3", "4"} for row in rows)
assert any(row["venue"] == "Physical Review E" and row["jcr_category"] == "PHYSICS, MATHEMATICAL" and row["jif_rank"] == "12/61" for row in rows)
assert any(row["venue"] == "Collective Dynamics" and row["jcr_status"] == "not_indexed" and row["cas_status"] == "not_indexed" for row in rows)
print("journal_metrics validation passed: 9 rows, 7 venues")
'@ | python -
```

Expected: `journal_metrics validation passed: 9 rows, 7 venues`

### Task 2: Register the implementation plan in the document index

**Files:**
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: the new maintained implementation plan.
- Produces: a repository-relative navigation link to the plan.

- [ ] **Step 1: Add the plan link**

Add this entry beside the journal metrics schema design:

```markdown
- [`superpowers/plans/2026-09-21-populate-journal-metrics.md`](superpowers/plans/2026-09-21-populate-journal-metrics.md)：已核验期刊指标长表的写入与校验步骤。
```

- [ ] **Step 2: Verify links resolve**

Run:

```powershell
Test-Path docs/superpowers/specs/2026-09-21-journal-metrics-schema-design.md
Test-Path docs/superpowers/plans/2026-09-21-populate-journal-metrics.md
```

Expected: both results are `True`.

- [ ] **Step 3: Review the scoped diff**

Run:

```powershell
git diff -- memPed/knowledge/literature/records/journal_metrics.csv docs/README.md docs/superpowers/plans/2026-09-21-populate-journal-metrics.md
```

Expected: the diff contains only the CSV population and the new documentation link; unrelated dirty-worktree changes remain untouched.
