# Knowledge Base Inventory Report

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。
**Date**: 2026-09-17\
**Database**: `memPed/knowledge/knowledge.sqlite3`

> **2026-09-21 audit update:** This document is a historical index snapshot. `b3-10` was later
> removed from the active candidate, manifest, extraction, and PDF sets by explicit user decision
> after Frontiers in Physics review. No index rebuild is represented by this report.

---

## 📊 Current Status

### Total Resources
- **50 literature papers** (all marked as `retrieval_eligibility='official'`)
- **5,624 chunks** extracted from these 50 papers

### Batch Distribution

| Batch | Papers | Chunks | Notes |
|-------|--------|--------|-------|
| **Pilot (t1~t5)** | 31 | 3,626 | Original gold standard collection |
| **Batch 1** | 3 | 413 | helbing-1995, nature-2021, nature-2024 |
| **Batch 3** | 16 | 1,585 | Latest batch (just indexed) |
| **Total** | **50** | **5,624** | |

### Batch 3 Breakdown (16 papers, 1,585 chunks)

| ID | Title | Chunks |
|----|-------|--------|
| b3-01 | Enhanced empirical data for the fundamental | 53 |
| b3-02 | Measuring the steady state of pedestrian flow in bottleneck experiments | 78 |
| b3-03 | Physica A 595 (2022) 127077 | 59 |
| b3-04 | Experimental study on the synchronization mechanism... | 150 |
| b3-05 | Discovering interaction | 87 |
| b3-06 | Inclusive crowd evacuation | 138 |
| b3-07 | Pedestrian Crowd Management | 150 |
| b3-08 | Crowd model calibration at strategic, tactical, and operational levels... | 125 |
| b3-09 | Dense Crowd Dynamics and Pedestrian Trajectories: A Multiscale Field Dataset... | 108 |
| b3-10 | Multi-agent modeling of crowd (historical; excluded 2026-09-21) | 87 |
| b3-11 | Microscopic modeling of attention-based movement behaviors | 87 |
| b3-13 | Data-driven physics-based modeling of pedestrian dynamics | 86 |
| b3-14 | High-statistics pedestrian dynamics on stairways... | 95 |
| b3-16 | Optimizing crowd evacuation: evaluation of strategies... | 76 |
| b3-17 | Modelling emergent pedestrian evacuation behaviors... | 86 |
| b3-18 | Continuous agent-based modeling of adult-child pairs... | 120 |

---

## ⚠️ Known Issues

### 1. Missing Metadata in Batch 3
All 16 Batch 3 papers lack structured metadata:
- ❌ No `authors` field
- ❌ No `year` field\
- ❌ No `doi` field
- ❌ No `source_url` field

Only basic fields exist:
- ✅ `resource_id`, `title`, `language`, `sha256`, `source_path`

**Impact**: Cannot filter by author/year, cannot verify publication details programmatically.

### 2. Incomplete Titles
Several titles are truncated due to first-page extraction issues:
- `b3-01`: "Enhanced empirical data for the fundamental" (missing "diagram and flow through bottlenecks")
- `b3-03`: "Physica A 595 (2022) 127077" (journal reference instead of title)
- `b3-05`, `b3-06`, `b3-10`, `b3-11`: All truncated

**Fixed during ingestion**: 9 titles were manually corrected after initial extraction failed.

### 3. Quality Gate Not Applied
The 16 Batch 3 papers were imported based on **technical eligibility** (readable PDF, unique SHA-256) but not validated against `collection_standard.md` criteria:
- ❓ CAS zone (Chinese Academy of Sciences classification)
- ❓ JCI ≥ 1.0
- ❓ Citation count thresholds
- ❓ Quality score ≥ 80

**Action needed**: Manual verification in Web of Science required.

### 4. File Management
- Original PDFs (18 files, 284MB) remain in `memPed/knowledge/batch-3-incoming/`
- Files have been copied to Vault (by SHA-256)
- 3 files still use placeholder names:
  - `Author_2024_ScientificReports_VerticalEvacuationSynchronization.pdf`
  - `Author_2025_ScientificReports_DeepGenerativeSurrogateCrowds.pdf`
  - `Author_2025_ScientificReports_InclusiveCrowdEvacuation.pdf`

**Recommendation**: Delete `batch-3-incoming/` after confirming Vault integrity; rename placeholder files using extracted author info.

### 5. Duplicate Detection
During Batch 3 import, 2 duplicates were caught by SHA-256:
- `phrs-47-1609310.pdf` → already exists as `t5-03`
- `s10287-023-00482-y.pdf` → already exists as `t4-05`

**Status**: ✅ Successfully blocked, no duplicate entries in database.

---

## 🔍 Index Status

### 1. SQLite FTS5 (Full-Text Search)
- ✅ **Indexed**: 5,624 chunks
- ✅ **Tokenizer**: jieba (Chinese) + simple (English fallback)
- ✅ **BM25 ranking**: Active with custom field weights (3.0, 1.5, 1.0, 0)

### 2. Chroma + BGE-M3 (Vector Search)
- ✅ **Indexed**: 5,624 chunks
- ✅ **Model**: BAAI/bge-m3 (local, CUDA-accelerated)
- ✅ **Dimension**: 1024
- ✅ **Collection**: `pedestrian_knowledge_base`

---

## 📈 Coverage by Research Domain

Based on pilot categorization (t1-t5 series):

| Domain | Pilot Papers | Batch 3 Candidates | Total Potential |
|--------|-------------|-------------------|----------------|
| **T1: Flow Fundamentals** | 5 | ? | ? |
| **T2: Experiment & Measurement** | 6 | ? | ? |
| **T3: Facility & Scenario Flow** | 7 | ? | ? |
| **T4: Evacuation & Modeling** | 10 | ? | ? |
| **T5: Safety & Risk** | 5 | ? | ? |

**Note**: Batch 3 domain distribution unknown due to missing metadata. Manual classification needed.

---

## 🎯 Next Steps

### Immediate (Data Quality)
1. **Metadata enrichment**: Extract authors/year/DOI from PDFs or query external databases
2. **Quality verification**: Validate Batch 3 against `collection_standard.md` in Web of Science
3. **Title correction**: Fix remaining truncated titles in database
4. **File cleanup**: Remove `batch-3-incoming/` after Vault verification

### Short-term (Retrieval Enhancement)
5. **BM25 optimization decision**:
   - Option A: Keep FTS5, improve tokenization (porter stemmer for English)
   - Option B: Migrate to Elasticsearch for advanced analysis
6. **Hybrid retrieval tuning**: Adjust FTS/vector weight balance
7. **Domain classification**: Categorize Batch 3 papers into T1-T5 domains

### Medium-term (Scale)
8. **Batch 4 planning**: Continue to 100-paper target
9. **Metadata pipeline**: Automate DOI lookup and citation count fetching
10. **Quality dashboard**: Build monitoring for collection standards compliance

---

## 📌 Key Metrics

```
Total papers:        50
Total chunks:        5,624
Avg chunks/paper:    112.5
Index backends:      2 (FTS5 + Chroma)
Retrieval modes:     3 (text, semantic, hybrid)
Storage:            ~284MB (Batch 3 PDFs) + Vault + indexes
```

**Database integrity**: ✅ All 50 papers have active versions and chunks\
**Duplicate prevention**: ✅ SHA-256 deduplication working\
**Retrieval readiness**: ✅ Both indexes operational
