# Rebuilt Gold question benchmark

_Status: historical (was plan; relabeled 2026-10-07) · 2026-09-23 · Gold v5 evaluation definition, not used by PEARL_

This experiment compares RAG retrieval methods on Chinese and English questions about pedestrian flow and evacuation transport. The legacy `pilot_gold.jsonl` and `core_gold.jsonl` are historical inputs and are not used to author, validate, or score this set.

## Scope and stages

1. Freeze the experiment corpus. Record resource ID, source SHA-256, parsed-document version, chunk policy, tokenizer, lexical analyzer, embedding model, and index fingerprints.
2. Draft independent research intents from research needs and inspected source evidence. Give each intent natural English and Chinese query variants with the same intended meaning.
3. Validate source hashes, page bounds, extractable evidence, paired queries, duplicates, and split leakage; record unresolved label cases separately.
4. Use 20 answerable intents for development, 100 new answerable intents for a sealed test split, and 20 unanswerable intents for a separate refusal study. These are design targets, not counts to fill with weak questions.
5. Compare retrieval configurations on the same frozen corpus and question set. Report English and Chinese results separately and paired differences. Do not count language variants as independent intents.

## Algorithm matrix

| Configuration | Purpose |
| --- | --- |
| FTS5/BM25 | Lexical baseline; inspect Chinese term segmentation and English exact terms |
| BGE-M3 Dense | Semantic baseline; measure bilingual recall |
| BM25 + Dense + RRF | Test complementary recall under fixed `recall_limit` and `rrf_k` |
| Fusion + Rerank | Measure ranking gain and latency/cost after recall |
| `parent-child-v1` vs `v2` | Isolate chunk/tokenization effects using separate indexes |

Keep corpus, Gold split, top-k, model version and query text fixed within each comparison. Record
per-query rankings, degradations, index fingerprints, runtime, and aggregate metrics.

## Evaluation

For answerable intents, report resource Hit@5, resource Recall@5, complete-evidence@5, exact locator hit rate, MRR, and nDCG@5 by language and question type. For unanswerable intents, report correct refusal and false refusal separately. Keep retrieval metrics separate from answer-generation and citation-quality metrics.

The legacy `GoldQuestion` evaluator cannot represent evidence groups or unanswerable questions. The independent `ped_knowledge.evaluation.gold_v2` scorer now handles grouped evidence, exact locators, paired metrics, and verified refusal labels. Candidate labels and refusal absence are still unverified, and no Gold v2 release gate is implemented. Legacy metric values must not be plotted as if they used the new metric schema.

## Asset locations

Candidate questions, evidence annotations, and corpus snapshot: [`../../memPed/knowledge/gold/2026-09-23-rebuild/`](../../memPed/knowledge/gold/2026-09-23-rebuild/). Any executed experiment must write a uniquely named directory under `outputs/` and must not overwrite an existing report.

## Current status

**✅ Experiment corpus frozen**: 104 resources, 9,112 chunks in `memPed/knowledge/knowledge.sqlite3`

**⚠️ V1 index**: Previously at `outputs/knowledge-index-104-v1-20260924-01/`, now moved to `../../failed/outputs-void-scores/knowledge-index-104-v1-20260924-01/` (PEARL retired this evaluation protocol; see `../../failed/README.md`)
- FTS5/BM25: `fts.sqlite3` (19MB, jieba analyzer)
- BGE-M3/Chroma: `chroma/chroma.sqlite3` (1024-dim vectors)
- Index fingerprints recorded in `build_report.json`

**⚠️ Development evaluation (void scores)**: Gold v* runs moved to `../../failed/outputs-void-scores/`
- Evaluation used Gold v2 scoring semantics (group-level AND/OR), incompatible with PEARL
- All aggregate scores from these runs cannot be used in PEARL reports
- Raw retrieval rankings may be re-scored under PEARL protocol

**⚠️ Test split sealed but not evaluated**: 100 test intents remain unscored per experimental design (one-shot evaluation after configuration finalized)

**⚠️ Remaining work**: Element-level locators, corpus governance final review, test configuration seal. Candidate annotations retain their status until formal Gold v2 release gate is defined.

The current v5 proposed split has 20 development and 100 test answerable intents, including 12 two-source comparisons, and 20 refusal intents. AI review corrected 10 answerable items, reclassified u012 as answerable, and added u021 as a replacement refusal. Independent review clarified that both access tunnels are meant in u021. A subsequent 120-intent review found bilingual wording differences, two cross-page claims, and a source-internal 58%/59% conflict. It also found that an equivalent secondary source for test item rgq-066 is used by development, so u012 replaced rgq-066 in the proposed test split. The v5 hashes are in [`../../memPed/knowledge/gold/2026-09-23-rebuild/full_candidate_manifest_v5.json`](../../memPed/knowledge/gold/2026-09-23-rebuild/full_candidate_manifest_v5.json). It is built by [`build_reviewed_candidate_v3.py`](build_reviewed_candidate_v3.py), [`finalize_candidate_v4.py`](finalize_candidate_v4.py), and [`integrate_review_v5.py`](integrate_review_v5.py), then checked by [`validate_candidate_v3.py`](validate_candidate_v3.py). Earlier bundles remain intact. AI review and technical validation do not establish formal Gold labels; element-level locator review, non-lexical alternative-source search and corpus governance remain open.

## Candidate development run

**⚠️ This section describes void evaluation runs.** All `outputs/gold-v*-dev-*` directories referenced below have been moved to `../../failed/outputs-void-scores/`. The evaluation protocol used Gold v2 scoring semantics (group-level AND across groups, OR within groups), which is incompatible with PEARL's requirement (fact-level AND within groups, OR across groups). Aggregate scores from these runs cannot be used in PEARL reports; raw retrieval rankings may be re-scored under PEARL protocol.

`evaluate_dev.py` scores only the proposed 20 development intents (40 Chinese/English variants)
against the independently built 104-paper V1 index. It checks the candidate file hashes and the
Catalog/FTS/Chroma fingerprints before reading rankings. For BM25, BGE-M3 and RRF, it takes the
first five distinct resources from the top 40 child chunks and writes per-query rankings and
metrics. Evidence groups are AND across groups and OR within a group. Exact page checks examine
all recalled child chunks belonging to those five selected resources, converting the annotation's
zero-based page index to the Catalog's one-based page range; an element ID is also checked when
present. Resource recall counts required evidence groups, so alternate sources within one group
do not inflate the denominator. `per_query.jsonl` stores both the selected resource ranking and
the complete retrieved chunk ranking needed to reproduce locator scores. The run does
not score the proposed test or refusal sets and does not use a reranker.

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -u experiments/benchmark-gold-20260923/evaluate_dev.py --candidate-version v5 --output-dir outputs/gold-v5-dev-exploratory-YYYYMMDD-01
```

The output directory must not exist before the run. `per_query.jsonl` stores each ranking;
`summary.json` records aggregate metrics by method and language, input hashes, index fingerprint,
runner hash, and the candidate-only status. Candidate page notes and alternatives still require
review, so these numbers are diagnostic rather than release-gate scores.
~~The v3 development run is in `outputs/gold-v3-dev-exploratory-20260924-01`.~~
The v4 change affects only the two u021 refusal query variants, so v3 development metrics
also describe v4. ~~The v5 changes affect development items rgq-122 and rgq-128; its completed
development run is in `outputs/gold-v5-dev-exploratory-20260924-01`.~~ The proposed test split
and refusal answers have not been scored.
The summaries record paired Chinese-minus-English differences and resource-miss question IDs.
All previous diagnostic output directories remain intact.

## P0 development audit and fixed comparison protocol

**⚠️ P0/P1 outputs moved to `../../failed/outputs-void-scores/`.** The comparison protocol used Gold v2 scoring semantics incompatible with PEARL.

`audit_dev_v5.py` parses only the materialized 20-intent development package; the full candidate files are hashed but sealed rows are not parsed. It checks the frozen question/annotation/index hashes, paired IDs, source PDF hashes, PDF page bounds, and extractable page text, then creates `per_intent.jsonl`, `review_queue.csv`, and `summary.json` in a new directory. These checks do not verify scientific claim support or bilingual semantic equivalence. ~~The final audit is in `outputs/gold-v5-dev-p0-audit-20260926-03/`; `-01` is an incomplete failed write and `-02` is the earlier completed audit, both retained for provenance.~~

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python experiments/benchmark-gold-20260923/audit_dev_v5.py --output-dir outputs/gold-v5-dev-p0-audit-新编号
```

For each answerable query, the unit is one intent with paired `en` and `zh` variants. For each required group, resources or locators in its `alternatives` are OR; all required groups are AND. `resource_recall@k` counts matched groups divided by required groups, and `complete_evidence@k` is one only when every group has a resource in the first k **distinct** resources. `exact_locator_group_recall@k` and `complete_locator@k` additionally require matching source SHA-256 and annotated page (plus element ID when present) among retrieved chunks of those selected resources. An annotation that specifies only a page remains a page-level locator; it is not element-level precision. MRR uses first relevant distinct-resource rank; nDCG credits each required group once. Report both languages per intent, paired differences, and strata by topic and evidence-group count; question-type strata require a reviewed type label, which v5 lacks.

The controlled comparison holds the 104 active resource IDs and PDF hashes, Gold v5 question/evidence hashes, 40 development queries, `recall_limit=40`, distinct-resource `k=5`, and `rrf_k=60` fixed. Each run must record code revision plus runner hash, chunk policy, tokenizer, lexical analyzer, embedding/reranker revision and weight hash, index fingerprint, parameters, and random seed (including `null` when unused). Future runs must measure per-query wall-clock latency for each method and tokenized parent context cost for the selected resources with a named tokenizer. The 2026-09-24 run did not collect those fields; its latency and context cost are **unavailable**, not zero. The 100 sealed test intents and 20 refusal intents are excluded from this development comparison. Agent-reviewed development labels are usable for research; human review is not a current gate. No static retriever has been frozen because the V2 and lexical candidates have not shown a clear controlled benefit and two answer/locator disputes remain visible.

`diagnose_v1_dev.py` checks live read-only FTS top-40 child IDs against the independently hashed saved V1 run and records query tokens, FTS scores, resource ranks, failure classes, and Dense/RRF rank shifts. ~~Its final output is `outputs/gold-v5-dev-p1-v1-diagnosis-20260926-02/`.~~ Dense and RRF rankings come from the saved run; their models were not rerun in this diagnosis.

```powershell
.\.venv\Scripts\python experiments/benchmark-gold-20260923/diagnose_v1_dev.py --output-dir outputs/gold-v5-dev-p1-v1-diagnosis-新编号
```

`compare_lexical_candidate.py` evaluates the independent V1-chunk lexical FTS against the Stage 1 hash-verified saved V1 Dense top-40 ranking, then recomputes RRF. `evaluate_v2_candidate.py` runs the separate V2 FTS and BGE-M3 Chroma on the same 40 development queries, recomputes RRF, and records warm-model retrieval latency plus selected parent-context token cost. Both reject mismatched corpus, policy, tokenizer, analyzer, model, or Gold fingerprints and check stored index content. ~~The final run outputs are `outputs/gold-v5-dev-p1-lexical-candidate-20260926-02/` and `outputs/gold-v5-dev-p1-v2-candidate-20260926-02/`; the latter uses `outputs/knowledge-index-104-v2-candidate-20260926-02/`.~~ `synthesize_p1.py` creates ~~`outputs/gold-v5-dev-p1-synthesis-20260926-03/`~~ with 20 paired intent rows, configuration summary, and failures; it parses only the development work package and saved development results.

```powershell
.\.venv\Scripts\python experiments/benchmark-gold-20260923/compare_lexical_candidate.py --output-dir outputs/gold-v5-dev-p1-lexical-candidate-新编号
.\.venv\Scripts\python -u experiments/benchmark-gold-20260923/evaluate_v2_candidate.py --index-dir outputs/knowledge-index-104-v2-candidate-20260926-02 --output-dir outputs/gold-v5-dev-p1-v2-candidate-新编号
.\.venv\Scripts\python experiments/benchmark-gold-20260923/synthesize_p1.py --lexical-run outputs/gold-v5-dev-p1-lexical-candidate-20260926-02 --v2-run outputs/gold-v5-dev-p1-v2-candidate-20260926-02 --output-dir outputs/gold-v5-dev-p1-synthesis-新编号
```

Candidate-label result: the pinned lexical terms did not improve the aggregate BM25/RRF scores. V2 Chinese Dense and RRF complete-evidence@5 were 17/20, versus 19/20 for V1; V2 added misses on `rgq-005-zh` and `rgq-022-zh`. English Dense/RRF were 20/20 in both policies. V1 Dense is a **candidate for later adjudicated comparison**, not a frozen Best Static Retriever. Cross-Encoder was not run because no versioned local reranker weights are available. The original V1 run has no per-query latency or parent-context counts, so V2 latency and cost are reported without a retrospective V1 comparison.

The development-only answer/evidence review now follows the [Stage 2 agent-review protocol](../stage2-annotation/README.md), authorized on 2026-09-27. Its separate versioned package marks all 20 intents `development_usable=true`: 18 have agent candidate answers and 2 carry explicit dispute caveats; all remain `human_verified=false`. These later labels were **not** used to retroactively change the P1 retrieval runs or to score sealed test. A future retrieval comparison using agent-adjudicated labels must name that label version and rerun the paired metrics rather than silently reinterpreting old results.

For pre-seal label review, [`find_semantic_alternatives.py`](find_semantic_alternatives.py)
uses the same frozen BGE-M3 index to propose three distinct nonlabel sources per English
answerable intent from the top 100 child chunks. AI reviewers read all 360 proposed source
spans in ~~`outputs/gold-v5-semantic-review-20260924-{a,b,c}`~~; none fully answered the matching
question, and no new source was added. The integrated read-only summary is in
~~`outputs/gold-v5-semantic-review-20260924-integrated`~~. This bounded discovery does not prove
that other PDF pages or external sources lack equivalent evidence.
