# Journal Admission Quartile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce best-quartile OR admission across CAS, JCI, and JIF, then remove Collective Dynamics from active collection assets.

**Architecture:** Keep full category evidence in `journal_metrics.csv` and store normalized best values in each literature Manifest. Add JIF quartile provenance to the governance contract, compute a comparable best rank across CAS/JCI/JIF, and use that rank for A/B validation while leaving numeric JCI as optional reference metadata.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest, UTF-8 CSV/JSONL, Markdown

## Global Constraints

- CAS major/minor categories use the best populated zone.
- JCI and JIF use the best populated quartile across all JCR categories.
- CAS, JCI, and JIF are alternatives: any one can satisfy the journal-ranking gate.
- Tier A requires at least one rank 1 result; tier B requires at least one rank 1 or 2 result.
- Numeric JCI does not affect admission.
- Preserve all citation-age, content-score, integrity, topic, PDF, and exception rules.
- Preserve the Collective Dynamics `not_indexed` journal audit row and historical evidence.
- Do not create chunks or indexes.
- The worktree already contains unrelated user changes; stage or commit only clean, task-owned files.

---

### Task 1: Specify best-rank behavior with failing tests

**Files:**
- Modify: `Knowledge-Base/tests/test_governance_manifest.py`
- Modify: `Knowledge-Base/tests/governance_samples.py`

**Interfaces:**
- Consumes: `ResourceManifest.model_validate(payload)`.
- Produces: acceptance and rejection cases for CAS-only, JCI-only, JIF-only, and numeric-JCI-independent admission.

- [ ] **Step 1: Extend the shared approved-literature sample**

Add official JIF evidence to the default payload:

```python
"jif_quartile": "Q1",
"jif_year": checked_at.year,
"jif_source": "clarivate_jcr",
```

- [ ] **Step 2: Add parametrized A- and B-tier tests**

Use payload overrides that leave only one ranking family populated:

```python
@pytest.mark.parametrize(
    ("tier", "ranking"),
    [
        ("A", {"cas_zone": 1, "cas_category": "Engineering", "cas_year": 2025, "cas_source": "cas_journal_partition"}),
        ("A", {"jci_quartile": "Q1", "jci_year": 2025, "jci_source": "clarivate_jcr"}),
        ("A", {"jif_quartile": "Q1", "jif_year": 2025, "jif_source": "clarivate_jcr"}),
        ("B", {"cas_zone": 2, "cas_category": "Engineering", "cas_year": 2025, "cas_source": "cas_journal_partition"}),
        ("B", {"jci_quartile": "Q2", "jci_year": 2025, "jci_source": "clarivate_jcr"}),
        ("B", {"jif_quartile": "Q2", "jif_year": 2025, "jif_source": "clarivate_jcr"}),
    ],
)
def test_literature_accepts_any_official_best_ranking(tier, ranking):
    payload = approved_payload_with_all_journal_metrics_cleared(quality_tier=tier)
    payload.update(ranking)
    assert ResourceManifest.model_validate(payload).quality_tier.value == tier
```

`approved_payload_with_all_journal_metrics_cleared` starts from the existing approved fixture and
sets all CAS, JCI, and JIF value/year/source fields to `None` before applying overrides.

- [ ] **Step 3: Add rejection and compatibility tests**

Add tests proving that A rejects only-rank-2 evidence, B rejects only-rank-3 evidence, missing
official provenance is rejected, all rankings absent are rejected, and `jci_value=0.1` with JCI
Q1 still satisfies A:

```python
with pytest.raises(ValueError, match="rank 1"):
    ResourceManifest.model_validate(approved_payload_with_only(jci_quartile="Q2", quality_tier="A"))
with pytest.raises(ValueError, match="rank 1 or 2"):
    ResourceManifest.model_validate(approved_payload_with_only(jif_quartile="Q3", quality_tier="B"))
with pytest.raises(ValueError, match="official JIF"):
    ResourceManifest.model_validate(approved_payload_with_only(jif_quartile="Q1", jif_source=None))
with pytest.raises(ValueError, match="journal ranking"):
    ResourceManifest.model_validate(approved_payload_with_all_journal_metrics_cleared())
payload = approved_payload_with_only(jci_quartile="Q1", jci_value=0.1, quality_tier="A")
assert ResourceManifest.model_validate(payload).quality_tier.value == "A"
```

- [ ] **Step 4: Run the focused tests and verify they fail**

Run:

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_governance_manifest.py -q
```

Expected: new JIF fields are rejected as extra fields and OR-rule cases fail under the old AND
logic.

### Task 2: Implement best-quartile governance

**Files:**
- Modify: `Knowledge-Base/src/ped_knowledge/governance/contracts.py`
- Modify: `Knowledge-Base/src/ped_knowledge/governance/manifest.py`
- Modify: `Knowledge-Base/tests/test_governance_manifest.py`
- Modify: `Knowledge-Base/tests/governance_samples.py`
- Modify: `Knowledge-Base/tests/test_governance_audit.py`

**Interfaces:**
- Produces: `best_journal_rank(cas_zone, jci_quartile, jif_quartile) -> int | None`.
- Adds: optional `jif_quartile`, `jif_year`, and `jif_source` fields on `ResourceManifest`.

- [ ] **Step 1: Add the comparable-rank helper and JIF fields**

Implement:

```python
def best_journal_rank(
    cas_zone: int | None,
    jci_quartile: JournalQuartile | None,
    jif_quartile: JournalQuartile | None,
) -> int | None:
    ranks = [rank for rank in (cas_zone, _quartile_rank(jci_quartile), _quartile_rank(jif_quartile)) if rank is not None]
    return min(ranks) if ranks else None
```

where `_quartile_rank` maps Q1 through Q4 to integers 1 through 4.

- [ ] **Step 2: Validate provenance conditionally**

Require complete CAS provenance only when `cas_zone` is populated, complete JCI provenance when
JCI quartile or numeric value is populated, and complete JIF provenance when JIF quartile is
populated. A/B records must have at least one ranking family; X records keep exception validation.

- [ ] **Step 3: Replace numeric-JCI tier checks**

Use `best_journal_rank` so A requires rank 1 and B allows rank 1 or 2. Do not compare
`jci_value` to 1.0 or 1.5.

- [ ] **Step 4: Add JIF freshness validation**

In `manifest.py`, report `JIF snapshot is older than 12 months` when populated JIF evidence is
older than the permitted window.

- [ ] **Step 5: Update audit fixtures**

Give ordinary A/B audit samples JIF evidence and keep X-tier exception samples valid without
forcing a qualifying rank.

- [ ] **Step 6: Run focused governance tests**

Run:

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_governance_manifest.py Knowledge-Base/tests/test_governance_audit.py -q
```

Expected: all focused tests pass.

### Task 3: Synchronize the maintained admission standard

**Files:**
- Modify: `memPed/knowledge/collection_standard.md`
- Modify: `Knowledge-Base/README.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: the contract behavior from Task 2.
- Produces: current human-readable rules matching the executable offline audit.

- [ ] **Step 1: Replace numeric-JCI admission wording**

Document the best-category normalization, CAS/JCI/JIF OR rule, A rank-1 threshold, B rank-1-or-2
threshold, missing-value behavior, and the fact that numeric JCI is reference-only.

- [ ] **Step 2: Keep non-journal gates unchanged**

Retain formal-version, PDF, citation, integrity, score, topic, batch, and retrieval-evaluation
requirements verbatim except where grammar must change around the new journal rule.

- [ ] **Step 3: Document the governance boundary**

Keep `governance/` described as offline research selection and audit rather than runtime ingestion
enforcement.

### Task 4: Remove Collective Dynamics from active collection assets

**Files:**
- Modify: `memPed/knowledge/literature/records/candidates.csv`
- Modify: `memPed/knowledge/batch-3-incoming/batch3_ingestion_manifest.jsonl`
- Delete: `memPed/knowledge/batch-3-incoming/Boomers_2023_CollectiveDynamics_CroMaExperiments.pdf`
- Modify: `memPed/knowledge/pilot-batch-1-candidates/candidate-list.csv`
- Modify: `memPed/knowledge/pilot-batch-1-candidates/download-guide.md`
- Modify: `docs/batch-2-literature-list.md`
- Modify: `docs/batch-3-final-manifest.md`
- Modify: `docs/batch-3-metadata-summary.md`

**Interfaces:**
- Consumes: the verified `not_indexed` audit row in `journal_metrics.csv`.
- Produces: no active candidate, incoming Manifest, or downloaded PDF for Collective Dynamics.

- [ ] **Step 1: Remove four canonical candidate rows**

Delete DOI rows `10.17815/cd.2022.139`, `10.17815/cd.2018.17`, `10.17815/cd.2018.16`, and
`10.17815/CD.2023.141` from `candidates.csv`.

- [ ] **Step 2: Remove active Batch 3 ingestion assets**

Delete the `b3-07` JSONL record, resolve and verify the exact PDF path remains under
`memPed/knowledge/batch-3-incoming`, then delete that one PDF.

- [ ] **Step 3: Remove active pilot and expansion candidates**

Remove Collective Dynamics rows from the pilot candidate CSV and mark corresponding download and
expansion entries as excluded because the journal is unindexed.

- [ ] **Step 4: Preserve historical evidence with an exclusion note**

Keep metadata extraction/report content but add a prominent note that `b3-07` was excluded on
2026-09-21 and is not an active ingestion item.

### Task 5: Validate rules, data cleanup, and regression safety

**Files:**
- Verify: all files changed in Tasks 1-4

**Interfaces:**
- Produces: reproducible evidence that governance behavior and cleanup match the approved design.

- [ ] **Step 1: Parse active CSV and JSONL files**

Use Python `csv` and `json` to parse every modified active record file and assert no active venue,
DOI, resource ID, or source path contains Collective Dynamics identifiers.

- [ ] **Step 2: Verify audit evidence remains**

Assert `journal_metrics.csv` still contains exactly one Collective Dynamics row with
`jcr_status=not_indexed` and `cas_status=not_indexed`.

- [ ] **Step 3: Run the Knowledge-Base suite**

Run:

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
\.venv\Scripts\python -m pytest Knowledge-Base/tests -q
```

Expected: all tests pass.

- [ ] **Step 4: Review scoped diffs and whitespace**

Run `git diff --check` and inspect only task-owned hunks. Confirm unrelated dirty-worktree changes
remain untouched and no chunk or index assets were created.
