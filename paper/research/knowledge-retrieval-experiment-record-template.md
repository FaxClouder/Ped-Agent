# Knowledge retrieval experiment record template

*Reusable run record for the Ped-Agent paper preparation workflow · status: plan*

---

Copy this template into `outputs/knowledge-ablation/<run-id>/report.md` after each completed run.
The JSON block should be saved as `experiment.json`; the table should be filled from the run's
`results.json` and `per_question.jsonl`.

## 📋 Run identity

| Field | Value |
| --- | --- |
| Run ID |  |
| Baseline ID |  |
| Date |  |
| Git commit |  |
| Python/package lock |  |
| Host and hardware |  |
| Random seed |  |
| Operator |  |

## 🗃️ Frozen inputs

| Artifact | Path | SHA-256 |
| --- | --- | --- |
| Corpus Manifest |  |  |
| Gold Questions |  |  |
| Retrieval config |  |  |
| Governance snapshot |  |  |

## ⚙️ Configuration

```json
{
  "parser_version": "",
  "chunk_policy": "",
  "parent_target_tokens": 0,
  "child_target_tokens": 0,
  "child_overlap_tokens": 0,
  "retrieval_mode": "",
  "candidate_depth": 0,
  "rrf_k": null,
  "embedding_model": null,
  "reranker_model": null,
  "eligibility_filter": "official-active-only",
  "context_order": "page-preserving"
}
```

## 📏 Aggregate results

| Metric | B0 | This run | Difference | 95% interval | Notes |
| --- | ---: | ---: | ---: | --- | --- |
| Recall@5 |  |  |  |  |  |
| Recall@20 |  |  |  |  |  |
| MRR |  |  |  |  |  |
| nDCG@5 |  |  |  |  |  |
| Locator hit rate |  |  |  |  |  |
| Official leakage |  |  |  |  |  |
| Superseded-hit rate |  |  |  |  |  |
| Query p50 (ms) |  |  |  |  |  |
| Query p95 (ms) |  |  |  |  |  |

## 🔎 Topic slices

| Topic | Questions | Recall@5 | MRR | Locator hit | Regression notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Flow fundamentals |  |  |  |  |  |
| Experiment measurement |  |  |  |  |  |
| Facility/scenario flow |  |  |  |  |  |
| Evacuation/behavior modeling |  |  |  |  |  |
| Safety/risk/intervention |  |  |  |  |  |

## 🧪 Interpretation

### What changed

<!-- State the single primary factor changed from B0. -->

### What improved

<!-- Mention per-question and topic-level evidence, not only the mean. -->

### What regressed

<!-- Record quality, locator, leakage, cost, or reproducibility regressions. -->

### Decision

`retain` / `reject` / `defer`

Reason:

## ✅ Validation checklist

- [ ] Corpus and Gold Questions match the frozen hashes
- [ ] Active resource set and index fingerprint are recorded
- [ ] Per-question rankings and errors are saved
- [ ] Official-source leakage is zero or explicitly explained
- [ ] Query latency and storage cost are recorded
- [ ] Statistical comparison is paired with B0
- [ ] No result is presented as final without a test-set run
