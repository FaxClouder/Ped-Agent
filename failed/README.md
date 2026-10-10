# Failed / Deprecated Assets

**Status:** Historical archive (2026-09-29)  
**Purpose:** Deprecated experiments and void scoring outputs from pre-PEARL evaluation protocols

---

## 📂 Contents

### `stage1-analysis/` (from `experiments/`)

**Why deprecated:**
- Relies on `paper/evaluation-reports/gold-v5-dev-20260924/` which **never existed in Git** and is now missing
- Writes to `paper/evaluation-reports/stage1-analysis-*/` which violates the repository boundary (paper/ is for publication assets, not runtime outputs)
- Superseded by PEARL framework's Layer 1 retrieval protocol

**What's preserved:**
- `analyze_stage1.py` (696 lines) — offline re-scoring pipeline for frozen rankings
- `test_stage1_analysis.py` — test suite
- `generate_dashboard.py` — visualization script
- `__pycache__/` — may contain bytecode for deleted auxiliary scripts

**Referenced by (broken links):**
- `docs/README.md:33` — links to non-existent `paper/evaluation-reports/stage1-analysis-20260926-02/`
- `paper/README.md:14,28,44,46,50,60-64` — multiple references to evaluation-reports structure
- `Knowledge-Base/README.md:81` — Stage 1 analysis cross-reference

### `outputs-void-scores/` (from `outputs/`)

**41 directories, 164 MB total** — Gold v2/v3/v4/v5 evaluation runs with **void scoring semantics**

**Why deprecated:**
- Scores computed with Gold v2 logic (evidence groups are AND, alternatives within group are OR)
- PEARL requires inverted logic (groups are OR, alternatives within group are AND)
- Cutoff was @5; PEARL uses @10
- All intents, questions, and evidence labels are retired — PEARL redesigns from scratch

**What's still reusable** (if extracted before deprecation):
- Raw retrieval rankings (`per_query.jsonl` files) can be **re-scored** under new logic
- Input hashes and experiment provenance metadata
- Timestamp-indexed output structure as a reproducibility pattern

**Categories:**
- `gold-v2-*` (17 dirs) — agent review iterations, refusal audit, early exploratory runs
- `gold-v3-*` (2 dirs) — exploratory and technical audit
- `gold-v4-*` (4 dirs) — alternative review iterations
- `gold-v5-*` (18 dirs) — P0/P1 audit cycles, lexical/v1/v2 candidate comparisons, synthesis reports

**Referenced by (25+ broken links):**
- `experiments/benchmark-gold-20260923/README.md` — 15 explicit output paths
- `experiments/benchmark-index-20260924/README.md:31` — gold-v5 P1 synthesis
- `docs/experiment-readiness-status-20260924.md` — 6 status checks
- `Knowledge-Base/README.md:80,83` — gold-v5 dev results
- `memPed/README.md:71` — exploratory run
- `paper/PedRAGent/existing-assets-inventory-2026-09-29.md:52` — asset inventory

---

## ⚠️ Git status

Per user decision (2026-09-29):
- **`failed/README.md`** and **`failed/stage1-analysis/*.py`** → committed (decision record + reusable scripts)
- **`failed/stage1-analysis/__pycache__/`** → .gitignored (but **preserved** — some .pyc are the only trace of deleted scripts)
- **`failed/outputs-void-scores/`** → .gitignored (164 MB; not reintroduced to Git history)

See `.gitignore` additions:
```gitignore
failed/**/results/
failed/**/*.sqlite3*
failed/outputs-void-scores/
```

---

## 🔗 Migration performed

| Source                          | Destination                           | Date       |
|---------------------------------|---------------------------------------|------------|
| `experiments/stage1-analysis/`  | `failed/stage1-analysis/`            | 2026-09-29 |
| `outputs/gold-v*/` (41 dirs)    | `failed/outputs-void-scores/gold-v*/`| 2026-09-29 |

**Broken links requiring fix:**
- 3 READMEs referencing `paper/evaluation-reports/` (never existed)
- 25 references to `outputs/gold-v*` (now under `failed/outputs-void-scores/`)

---

## 🧪 What remains reusable in `outputs/`

> **2026-10-07 note:** the table below is the 2026-09-29 snapshot. `gold-v2-snapshot-20260924-01/`
> is in `failed/outputs-void-scores/`, not `outputs/`, and `outputs/` has since grown to 64
> directories (~31 GB). The current directory-level classification is in
> [`docs/rag-asset-audit-2026-10-07.md`](../docs/rag-asset-audit-2026-10-07.md).

After this migration, `outputs/` retained **19 directories, 948 MB**:

| Asset                                       | Size  | Status       | Why kept                                    |
|---------------------------------------------|-------|--------------|---------------------------------------------|
| `knowledge-index-104-v1-20260924-01/`       | 113M  | Frozen       | V1 candidate index for comparison           |
| `knowledge-index-104-v2-candidate-*-0[12]/` | 290M  | Frozen       | V2 candidate indexes (2 runs)               |
| `knowledge-index-104-v1-lexical-candidate/` | 16M   | Frozen       | Lexical (BM25) baseline                     |
| `parser-sensitivity-p2-retrieval-*/`        | 422M  | Frozen       | P2 retrieval paired comparison (Adobe vs PyMuPDF) |
| `parser-sensitivity-p2-parse-*/`            | 81M   | Frozen       | P2 parsing outputs with provenance          |
| `stage2-agent-adjudicated-*/`               | ~500K | Schema       | 18 agent-reviewed answers + 2 contested     |
| `gold-v2-snapshot-20260924-01/`             | 146M  | Reference    | Snapshot for format/schema reference only   |
| `chunk-cleanup-backup-*/`                   | 27M   | Backup       | Pre-change state for rollback               |
| `metadata-batch-1-backup-*/`                | 1.1M  | Backup       | Metadata snapshot                           |

**Total reusable:** 419M indexes + 503M parser sensitivity assets + schema references = ~950M

---

## 📚 Related decisions

- **PEARL framework** (`paper/pearl-framework/`) declares all pre-PEARL eval results **void** but does **not** void:
  - Parsing/indexing/evaluation **scripts**
  - 102 Adobe PDF Extract API responses (`memPed/knowledge/derived/`, ~1.6G, also local-only)
  - Evidence anchor strings (`experiments/benchmark-parser-sensitivity-20260927/evidence_anchors_dev.json`)
  - `core_manifest.jsonl` SHA-256 hashes for 104 papers

- **Gold v2 scorer semantic inversion** — main branch `gold_v2.py` has inverted AND/OR vs PEARL; correct `metrics_v2_solution_b.py` exists on branch `codex/memped-knowledge-staging` (worktree `.worktrees/memped-knowledge-update`, commit 481db39) but not yet merged.

See memory:
- `pearl-discards-results-not-assets.md`
- `gold-v2-scorer-and-or-inverted.md`
- `never-touch-pycache.md`

---

## 🗑️ If reconsidering deletion

Before deleting `failed/`:
1. Confirm PEARL corpus will **not** reuse the same 104 PDFs (if yes, keep `outputs-void-scores/` for raw rankings)
2. Extract any `per_query.jsonl` needed for re-scoring demonstrations
3. Archive `stage1-analysis/*.py` elsewhere if the offline re-scoring pattern is valuable

**Do not delete without checking:** `outputs/`, `memPed/knowledge/derived/`, `experiments/`, and `.codex-tmp/` are all .gitignored — local deletion is permanent.
