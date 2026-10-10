# PEARL Layer 2 frozen development protocol

*Fixed R4 Top-10 and final-text evidence evaluation · status: current · 2026-10-04 · protocol v1*

## Scope and input boundary

Consume only original development R4, pass 1, Top-10 in saved order. No retrieval, reranking,
Gold-guided selection, or Layer 3/4 execution. Assembly receives query-only records, type-only
metadata, frozen child and parent bodies, tokenizer and configuration. Gold remains separate
for evaluation. Resolve r02 identity from revision/delivery manifests by declared SHA rather
than choosing a latest filename. Original run and output files are read-only inputs.

Reuse `HuggingFaceTokenCounter` from Knowledge-Base. Catalog context expansion depends on a
mutable Catalog and retrieval performs new search, so neither is used here. EvidenceGraph
and citation policy validate structure, not semantic sufficiency; they do not replace review.

## Frozen matrix and assembly

| Configuration | Expansion | Complete serialized context budget |
| --- | --- | --- |
| C0-4096 | child only | 4096 |
| C0-8192 | child only | 8192 |
| C1-4096 | direct parent replacement | 4096 |
| C1-8192 | direct parent replacement | 8192 |

Use pinned local BGE-M3 `tokenizer.json`, SHA from the original run preflight/model binding,
through repository HuggingFaceTokenCounter; special tokens count once per full context.
Record package version and tokenizer fingerprint. This is an accounting tokenizer, not a
claim about an unexecuted generator's tokenizer. Each serialization unit is exactly:

```text
[Source source_id | locator]
Title: title
text
```

Units are separated by exactly two newlines. No chunk IDs, rank, strategy, score or query
appear in the serialized context. Titles, labels and separators all count toward the budget.

C1 verifies parent identity, source, version, parser, policy and declared parent text SHA.
Missing parent retains child. A parent replaces a child only if the complete exact child
body is a substring of the parent body; otherwise retain child and record containment_failed.
This conservative exact check is structural and does not claim semantic completeness.
Merge repeated unit IDs once, preserving earliest child rank and all child associations.
Do not merge merely identical bodies across different source IDs. Rank order is unchanged.

Greedily keep complete units. At the first non-fitting unit, retain a deterministically
selected fitting Unicode-character prefix by bisection with full-string tokenizer tests,
then stop. If no nonempty body with its full metadata header fits, drop that unit and stop.
No decoding/reencoding replacement changes the original prefix. Budget is verified after
serialization; the search need not claim globally maximal prefixes for non-monotone token
counts. Record exact discarded suffix and later dropped units. Tables receive the same rule:
cut headings, units or rows remain visible in traces and must be rejudged from final text.

Persist raw, expanded, deduplicated and final units and full strings, SHA, token counts,
source identity, parent containment, truncation and latency. Reopen saved outputs and check
all hashes and budgets. Output files and stage directories are exclusive-create only.

## Sampling and review

Four types, five each: sort stable intent IDs within each type, use one Random(20261004)
stream to sample five in sorted type order, sort selected IDs, save before assembly. Stage C
has 20 intents and 80 contexts; stage D has 80 intents and 320 contexts. Stage C is a subset
of development, not an independent test set. Inputs and old outputs are SHA-checked before
and after execution. Unknown relations are not inherited from old support maps.

Independent fork_turns=none Agent review receives query, requirements, allowed groups and
anonymous actual context. No strategy, rank, score, old labels or supplemental PDF text.
All support is judged from final retained text. Step attribution requires independently
reviewed before/after actual step strings. Save selected decisions, prompts, model provenance
and hashes; unresolved judgments remain unknown. Human review is not an acceptance gate.

## Frozen scoring and statistics

Requirements are yes/no/unknown. Within group AND: any no gives no; all yes gives yes;
otherwise unknown. Across groups OR: any yes gives yes; all no gives no; otherwise unknown.
Complete Group Coverage lower bound=yes/N and upper bound=(yes+unknown)/N, with all N,
unknown and applicable counts shown. Evidence Coverage is maximum, over allowed groups,
yes-count/group-size lower bound and (yes+unknown)-count/group-size upper bound. Do not
combine partial support from different alternatives to fabricate complete evidence.

Relevance/noise use equal-weight retained serialization units with labels relevant,
irrelevant, mixed, unknown. Relevance counts relevant+mixed; noise counts irrelevant+mixed;
they are not complements. Report unknown bounds and per-context macro averages. Empty
contexts are not applicable; expose applicable_n and unit_n. No independent sufficiency
predictor is executed, therefore prediction accuracy is not reported.

Four predeclared paired contrasts: C1−C0 at 4096 and 8192; 8192−4096 within C0 and C1.
Use exact two-sided McNemar on fully adjudicated pairs and Holm adjustment across four
comparisons. Also report all-N difference bounds and unknown-pair counts. Four-type results
are descriptive strata without extra significance testing. Development findings remain
exploratory despite formal project acceptance of validated Agent evaluation.

Costs include actual context tokens, assembly latency, review invocation and token usage
where available. Never equate token occupancy with semantic noise. Parent-added support
changes Layer 2 only, without modifying Layer 1 CEGR. Layer 3 handoff is documented only.
