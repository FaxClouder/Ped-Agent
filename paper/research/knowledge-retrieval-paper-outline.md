# Knowledge retrieval experiment paper outline

*Proposed paper-facing structure for the Ped-Agent knowledge-base study · status: plan*

---

This outline maps the executable experiment protocol to a future paper section. It is intentionally
an outline: no result is implied until the corresponding run record exists.

## 📋 Introduction

- Research problem: reliable, locatable evidence retrieval for pedestrian-flow studies
- Why ingestion, Chunking, sparse/dense retrieval, and reranking should be compared separately
- Contributions to claim only after experiments are complete

## 🧭 System and task definition

- Resource types: literature, regulation, and standard
- Technical pipeline: PDF preflight, content-addressed storage, structured parsing, Parent/Child
  Chunking, Catalog, FTS/BM25, optional Dense/RRF/Rerank
- Evidence output: resource identity, version, text, page/section/clause locator
- Formal-source and version eligibility boundary

## 🗃️ Corpus and benchmark construction

- Corpus selection and governance snapshot
- Resource counts by type, topic, language, and version
- Gold Question construction and locator annotation
- Development/test separation and hash-based freeze
- Query taxonomy and topic slices

## ⚙️ Experimental settings

- Hardware and software versions
- Baseline B0
- Ablation factors and parameter grids
- Index construction and candidate-depth settings
- Reranker and embedding configuration
- Reproducibility artifacts and isolated run directories

## 📏 Evaluation metrics

### Retrieval quality

- Recall@5/20
- MRR
- nDCG@k
- Topic-level results

### Evidence quality and safety

- Locator hit rate
- Official-source leakage
- Superseded/duplicate hit rate

### Engineering cost

- Import and index build time
- Query p50/p95 latency
- Memory, index size, and derived-asset size

## 🔬 Results

- B0 versus parser/chunk variants
- B0 versus retrieval variants
- Candidate depth and reranking quality-cost curves
- Governance negative control
- Topic-level and per-question analysis
- Statistical intervals and multiple-comparison disclosure

## 🧪 Discussion

- Which factors materially affect evidence retrieval
- Quality-cost trade-offs
- Failure cases: scans, tables, terminology, regulations, version conflicts
- What is specific to the pedestrian-flow corpus
- Limits of a small pilot and transferability to the core corpus

## ✅ Reproducibility and release

- Frozen Manifest and Gold Questions
- Git commit and package lock
- Parser/chunk/index/model fingerprints
- Run record and per-question outputs
- Active retrieval configuration only after acceptance gates

## 📌 Claim boundary

The paper may claim only results supported by frozen run artifacts. A design proposal, unit-test
result, or successful single-document smoke import is not a retrieval-effectiveness result.
