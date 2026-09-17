# RAG Tokenization V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible `parent-child-v2` retrieval candidate with valid Gold evaluation, policy-isolated chunks, BGE-compatible token accounting, sentence-aware boundaries, and deterministic bilingual BM25 analysis.

**Architecture:** Keep canonical documents and the Catalog as sources of truth. Store V1 and V2 chunks side by side by policy, build indexes from an explicit policy, and activate candidates only through the existing evaluation gate. Use injected token counters so boundary algorithms remain testable without local model assets.

**Tech Stack:** Python 3.12, Pydantic, SQLite/FTS5, jieba, Hugging Face tokenizers, Chroma, pytest.

## Global Constraints

- Do not overwrite existing research outputs or indexes.
- Preserve input hashes, policy/model versions, tokenizer fingerprints, and result provenance.
- Official V2 builds fail when the configured tokenizer is unavailable or mismatched.
- No Web service, queue, UI, semantic chunker, or LLM-generated boundary logic.
- Run Knowledge-Base tests first and the four-module suite before completion.

---

### Task 1: Repair the Gold evaluation contract and pilot data

**Files:**
- Create: `Knowledge-Base/tests/test_evaluation.py`
- Modify: `Knowledge-Base/src/ped_knowledge/evaluation/__init__.py`
- Modify: `memPed/knowledge/pilot_gold.jsonl`
- Modify: `memPed/knowledge/pilot_config.json`
- Modify: `memPed/knowledge/core_config.json`

**Interfaces:**
- Produces: `EvaluationAcceptanceConfig.minimum_question_count: int`
- Produces: `validate_gold_resources(questions, available_resource_ids) -> None`
- Preserves: `load_gold(path) -> list[GoldQuestion]`

- [ ] **Step 1: Write failing tests for minimum count and resource validation**

```python
def test_acceptance_uses_a_minimum_question_count():
    config = EvaluationAcceptanceConfig(
        minimum_question_count=1,
        k=5,
        minimum_recall_at_k=0.8,
        minimum_mrr=0.7,
        minimum_locator_hit_rate=0.75,
        maximum_non_official_leakage=0.0,
    )
    report = EvaluationReport(
        question_count=2, k=5, recall_at_k=1, mrr=1,
        ndcg_at_k=1, locator_hit_rate=1,
    )
    assert audit_evaluation(report, config, non_official_leakage=0).is_compliant

def test_gold_resource_validation_reports_missing_ids():
    questions = [GoldQuestion(
        question_id="q1", query="query",
        expected_resource_ids=["missing"], expected_locators=["p.1"],
    )]
    with pytest.raises(ValueError, match="missing"):
        validate_gold_resources(questions, {"present"})
```

- [ ] **Step 2: Run the tests and confirm they fail because the new API is absent**

Run: `python -m pytest Knowledge-Base/tests/test_evaluation.py -q`

Expected: import or validation failures for `minimum_question_count` and `validate_gold_resources`.

- [ ] **Step 3: Implement the new acceptance and validation behavior**

```python
class EvaluationAcceptanceConfig(BaseModel):
    minimum_question_count: int = Field(ge=1)
    # existing metric fields remain unchanged

def validate_gold_resources(
    questions: list[GoldQuestion], available_resource_ids: set[str]
) -> None:
    missing = sorted({rid for q in questions for rid in q.expected_resource_ids} - available_resource_ids)
    if missing:
        raise ValueError(f"Gold Questions reference missing resources: {', '.join(missing)}")
```

Change `audit_evaluation()` to reject only when `report.question_count < minimum_question_count`.

- [ ] **Step 4: Normalize all 31 Gold records and configs**

Use `expected_resource_ids`, `expected_locators`, lowercase normal IDs, and the three explicit legacy mappings in the design. Set both configs to `"minimum_question_count": 30`.

- [ ] **Step 5: Run evaluation and Knowledge-Base tests**

Run: `python -m pytest Knowledge-Base/tests/test_evaluation.py Knowledge-Base/tests/test_retrieval_and_release.py -q`

Expected: all selected tests pass and `load_gold(memPed/knowledge/pilot_gold.jsonl)` returns 31 questions.

- [ ] **Step 6: Commit**

```powershell
git add Knowledge-Base/tests/test_evaluation.py Knowledge-Base/src/ped_knowledge/evaluation/__init__.py memPed/knowledge/pilot_gold.jsonl memPed/knowledge/pilot_config.json memPed/knowledge/core_config.json
git commit -m "fix: restore reproducible retrieval evaluation baseline"
```

### Task 2: Allow chunk-policy builds to coexist

**Files:**
- Modify: `Knowledge-Base/src/ped_knowledge/storage/__init__.py`
- Modify: `Knowledge-Base/src/ped_knowledge/ingestion/__init__.py`
- Modify: `Knowledge-Base/tests/test_ingestion_pipeline.py`
- Modify: `Knowledge-Base/tests/test_retrieval_and_release.py`

**Interfaces:**
- Produces: `Catalog.replace_chunks(version_id, chunks, *, policy_version)`
- Produces: `Catalog.list_official_chunks(*, policy_version)`
- Produces: `Catalog.official_fingerprint(*, policy_version)`
- Produces: `Catalog.record_chunk_build(...)`

- [ ] **Step 1: Write failing coexistence and migration tests**

```python
def test_chunk_policies_coexist_for_the_same_resource_version(tmp_path):
    catalog, record = catalog_with_active_resource(tmp_path)
    catalog.replace_chunks(record.sha256, [chunk("v1", "parent-child-v1")], policy_version="parent-child-v1")
    catalog.replace_chunks(record.sha256, [chunk("v2", "parent-child-v2")], policy_version="parent-child-v2")
    assert [c["chunk_id"] for c in catalog.list_official_chunks(policy_version="parent-child-v1")] == ["v1"]
    assert [c["chunk_id"] for c in catalog.list_official_chunks(policy_version="parent-child-v2")] == ["v2"]
```

- [ ] **Step 2: Run the focused test and confirm the signature fails**

Run: `python -m pytest Knowledge-Base/tests/test_ingestion_pipeline.py -q`

Expected: failure because Catalog methods do not accept `policy_version`.

- [ ] **Step 3: Add `chunk_builds` schema and policy-scoped operations**

```sql
CREATE TABLE IF NOT EXISTS chunk_builds (
  version_id TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  tokenizer_fingerprint TEXT NOT NULL,
  source_fingerprint TEXT NOT NULL,
  chunk_count INTEGER NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (version_id, policy_version)
);
```

Delete and select chunks using both `version_id` and `policy_version`. Require policy arguments at index-building call sites.

- [ ] **Step 4: Update ingestion and test fixtures to pass explicit policy versions**

Pass `self.chunker.policy.policy_version` to `replace_chunks()`. Existing callers that represent V1 use `parent-child-v1`.

- [ ] **Step 5: Run storage, ingestion, and retrieval tests**

Run: `python -m pytest Knowledge-Base/tests/test_ingestion_pipeline.py Knowledge-Base/tests/test_retrieval_and_release.py -q`

Expected: all selected tests pass, including legacy-schema migration.

- [ ] **Step 6: Commit**

```powershell
git add Knowledge-Base/src/ped_knowledge/storage/__init__.py Knowledge-Base/src/ped_knowledge/ingestion/__init__.py Knowledge-Base/tests
git commit -m "feat: isolate chunks by policy version"
```

### Task 3: Add deterministic token counters and chunk provenance

**Files:**
- Create: `Knowledge-Base/src/ped_knowledge/tokenization/__init__.py`
- Create: `Knowledge-Base/tests/test_tokenization.py`
- Modify: `Knowledge-Base/src/ped_knowledge/contracts/__init__.py`
- Modify: `Knowledge-Base/src/ped_knowledge/chunking/__init__.py`

**Interfaces:**
- Produces: `TokenCounter`, `RegexTokenCounter`, `HuggingFaceTokenCounter`
- Extends: `KnowledgeChunk.token_count`, `tokenizer_fingerprint`, character offsets, `hard_split`
- Changes: `HierarchicalChunker(policy=None, token_counter=None)`

- [ ] **Step 1: Write failing counter and provenance tests**

```python
def test_fake_counter_controls_child_hard_limit():
    counter = FakeTokenCounter()
    chunker = HierarchicalChunker(
        ChunkingPolicy(policy_version="parent-child-v2", child_target_tokens=4, child_max_tokens=5, child_overlap_tokens=1),
        token_counter=counter,
    )
    children = child_chunks(chunker.chunk(document_with_text("one two three four five six")))
    assert all(item.token_count <= 5 for item in children)
    assert all(item.tokenizer_fingerprint == counter.fingerprint for item in children)
```

- [ ] **Step 2: Run focused tests and confirm missing APIs fail**

Run: `python -m pytest Knowledge-Base/tests/test_tokenization.py Knowledge-Base/tests/test_parsing_and_chunking.py -q`

- [ ] **Step 3: Implement counters and fail-fast fingerprint checking**

`RegexTokenCounter` wraps the V1 regex. `HuggingFaceTokenCounter.from_local_path()` loads `tokenizer.json`, verifies its SHA-256, and uses `encode`/`decode` without network access.

- [ ] **Step 4: Populate provenance fields from the counter**

Keep V1 behavior when no counter is supplied. V2 requires an injected model counter and includes its fingerprint in chunk IDs.

- [ ] **Step 5: Run tokenization and chunking tests**

Run: `python -m pytest Knowledge-Base/tests/test_tokenization.py Knowledge-Base/tests/test_parsing_and_chunking.py -q`

- [ ] **Step 6: Commit**

```powershell
git add Knowledge-Base/src/ped_knowledge/tokenization Knowledge-Base/src/ped_knowledge/contracts Knowledge-Base/src/ped_knowledge/chunking Knowledge-Base/tests
git commit -m "feat: add reproducible chunk token counters"
```

### Task 4: Implement boundary-preserving V2 child chunks

**Files:**
- Modify: `Knowledge-Base/src/ped_knowledge/chunking/__init__.py`
- Modify: `Knowledge-Base/tests/test_parsing_and_chunking.py`
- Create: `Knowledge-Base/config/retrieval/chunking-v2.yaml`

**Interfaces:**
- Produces: deterministic element → paragraph → sentence → token fallback splitting
- Guarantees: every V2 child is at most `child_max_tokens`

- [ ] **Step 1: Write failing tests for Chinese/English sentences, oversized units, overlap, and locators**

```python
def test_v2_prefers_complete_bilingual_sentences():
    children = build_v2("第一句。第二句！ Third sentence. Fourth sentence.")
    assert children[0].text.endswith(("。", "！", "."))
    assert all(child.token_count <= child_max for child in children)

def test_v2_marks_token_fallback_for_an_oversized_atomic_unit():
    children = build_v2("oversized " * 100)
    assert any(child.hard_split for child in children)
```

- [ ] **Step 2: Run tests and confirm V1 fixed-window behavior fails the new assertions**

- [ ] **Step 3: Implement boundary units and token-budget merging**

Carry element ID, page, locator, and character offsets on every internal unit. Use a fixed bilingual sentence rule and a tracked abbreviation set; use tokenizer slicing only for oversized atomic units.

- [ ] **Step 4: Add the tracked V2 YAML configuration**

Record policy name, tokenizer identity, targets, maxima, overlap, and boundary strategy. Resolve and record the tokenizer hash from the configured local asset during each build.

- [ ] **Step 5: Run chunking and ingestion tests**

Run: `python -m pytest Knowledge-Base/tests/test_parsing_and_chunking.py Knowledge-Base/tests/test_ingestion_pipeline.py -q`

- [ ] **Step 6: Commit**

```powershell
git add Knowledge-Base/src/ped_knowledge/chunking Knowledge-Base/tests Knowledge-Base/config/retrieval/chunking-v2.yaml
git commit -m "feat: preserve sentence boundaries in v2 chunks"
```

### Task 5: Add versioned bilingual lexical analysis and OR recall

**Files:**
- Modify: `Knowledge-Base/src/ped_knowledge/tokenization/__init__.py`
- Modify: `Knowledge-Base/src/ped_knowledge/indexing/__init__.py`
- Create: `Knowledge-Base/config/retrieval/lexical-v1.yaml`
- Create: `Knowledge-Base/config/retrieval/pedestrian_terms.txt`
- Create: `Knowledge-Base/config/retrieval/stopwords_zh_en.txt`
- Create: `Knowledge-Base/tests/test_indexing.py`

**Interfaces:**
- Produces: `JiebaLexicalAnalyzer.analyze(text) -> list[str]`
- Produces: `JiebaLexicalAnalyzer.fingerprint: str`
- Changes: `FTSIndex(path, analyzer=None)` and FTS metadata

- [ ] **Step 1: Write failing domain-term, stopword, and OR-query tests**

```python
def test_domain_analyzer_preserves_pedestrian_terms(analyzer):
    assert "社会力模型" in analyzer.analyze("社会力模型与行人流基本图")
    assert "与" not in analyzer.analyze("社会力模型与行人流基本图")

def test_fts_query_recalls_a_document_when_only_one_term_matches(tmp_path, analyzer):
    index = build_index(tmp_path, analyzer, body="社会力模型")
    assert index.search("社会力模型 不存在的附加词")
```

- [ ] **Step 2: Run indexing tests and confirm default jieba/AND behavior fails**

- [ ] **Step 3: Implement the analyzer and tracked configuration**

Load jieba terms and stopwords without changing global jieba state. Hash normalized config and file bytes. Preserve alphanumeric identifiers, years, model names, and DOI components.

- [ ] **Step 4: Inject the analyzer into FTS rebuild/search and persist its fingerprint**

Build query syntax with quoted terms joined by `OR`; keep BM25 weights unchanged. Reject an index whose stored lexical fingerprint differs from the active analyzer.

- [ ] **Step 5: Run indexing and hybrid-retrieval tests**

Run: `python -m pytest Knowledge-Base/tests/test_indexing.py Knowledge-Base/tests/test_retrieval_and_release.py -q`

- [ ] **Step 6: Commit**

```powershell
git add Knowledge-Base/src/ped_knowledge/tokenization Knowledge-Base/src/ped_knowledge/indexing Knowledge-Base/config/retrieval Knowledge-Base/tests
git commit -m "feat: add versioned domain lexical retrieval"
```

### Task 6: Add candidate manifests, audits, and end-to-end verification

**Files:**
- Modify: `Knowledge-Base/src/ped_knowledge/indexing/__init__.py`
- Modify: `Knowledge-Base/src/ped_knowledge/evaluation/__init__.py`
- Modify: `Knowledge-Base/tests/test_retrieval_and_release.py`
- Modify: `Knowledge-Base/README.md`
- Modify: `docs/README.md`

**Interfaces:**
- Produces: versioned index metadata including policy and lexical fingerprints
- Produces: chunk length/truncation audit fields in evaluation artifacts

- [ ] **Step 1: Write failing tests for stale-policy rejection and audit fields**

Test that HybridRetriever rejects a candidate whose Catalog, chunk-policy, embedding, or lexical fingerprints differ, and that the audit reports oversize/hard-split counts.

- [ ] **Step 2: Run focused tests and confirm metadata is missing**

- [ ] **Step 3: Implement manifest metadata and audits**

Include policy, tokenizer, lexical analyzer, embedding max length/normalization, Catalog fingerprint, Gold hash, and code revision. Do not create or overwrite a release directory from unit tests.

- [ ] **Step 4: Update current documentation**

Document V1/V2 status accurately, mark V2 as candidate until a real local index and Gold run are executed, and add maintained-document links.

- [ ] **Step 5: Run module and repository verification**

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
E:\F_Workspace\F-Agent-Paper\.venv\Scripts\python.exe -m pytest Knowledge-Base/tests -q
E:\F_Workspace\F-Agent-Paper\.venv\Scripts\python.exe -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
```

Expected: zero failures. Real BGE, Chroma, and Gold metrics are reported only if the local assets are explicitly run against a new candidate directory.

- [ ] **Step 6: Commit**

```powershell
git add Knowledge-Base docs
git commit -m "docs: document RAG tokenization v2 candidate"
```
