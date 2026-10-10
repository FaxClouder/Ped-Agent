# Session 2 source and chunk preparation

*Experiment-local interfaces and fixed counterexamples · status: current · 2026-10-05*

Implemented [source_view.py](source_view.py), [table_snapshot.py](table_snapshot.py), [parent_graph.py](parent_graph.py), [chunkers.py](chunkers.py), and [semantic_threshold.py](semantic_threshold.py). No historical source, output, module, or contract files were changed by this worker. No remote calls, commits, E1 grid, or real research scores were produced by this worker.

Source coordinates preserve Python Unicode code points and original character content. Display separators are separately recorded without evidence identity. JSON-string array fields are decoded; duplicate element identities fail. Ambiguous legacy substring locations remain ambiguous and never establish semantic support. Heading paths are metadata and headings appear only once in source content.

Public tables freeze independently of C1–C4/B0 at 256 BGE tokens, using contiguous complete raw rows where possible and reversible token-offset fallback for oversized rows/cells. The frozen conservative repeated-header policy is `none`: no synthetic header copies are introduced. Exact raw Adobe row/cell mappings are retained; mismatching raw/table-data representations remain `unresolved`, with original text retained. All views share the global snapshot SHA but embed only their own table records. Unresolved cell mappings must remain explicit blockers for affected formal numeric comparisons.

Public parents group continuous paragraphs within actual heading paths and table barriers; the default cap is 1536 BGE tokens. Oversized paragraphs use sentence/token fallback. Multiple intersecting public parents are bound when the graph is attached to the view. C1 uses real tokenizer offsets and verified legal windows; no maximal-character-prefix property is claimed for core windows. C2 preserves paragraphs before sentence/token fallback. C3 additionally keeps sections separate. C4 uses frozen corpus-only adjacent sentence distances and never applies an adjacent-pair distance repeatedly to fragments of one oversized sentence. B0 preserves regex windows320/overlap48 and historical heading/1200-target/1800-maximum grouping on the public source representation. It is distinct from BGE-token C1.

Overlap/prefix maintain the original core SHA and source spans. Overlap is confined to source barriers and C3 sections; complete sentences are preferred. Prefix text can come only from original heading/title elements, with title then leaf then ancestors and a 64-token verified cap. Prefix spans never become core support spans. Retrieval `text_sha256` is raw UTF-8 SHA-256; structural identities use canonical JSON SHA-256.

Semantic calibration records sentence source spans, adjacent pair distances, exclusions, NumPy linear quantile, model identity and source-view hashes. The fixed vector reference gives distances1/2 and q90=1.9. Empty/zero/nonfinite cases remain explicit. Vector identity hashes NumPy dtype/shape and contiguous float64 bytes to avoid a huge JSON vector serialization. Actual all-corpus model execution and saved vectors belong to the root worker's smoke evidence, not these fixed-vector unit checks.

## Verification

Initial test-first run before production files existed: `12 failed in 1.96s`, exit1, each failed the explicit missing-implementation assertion. New multi-parent binding, long-sentence semantic-fragment and raw UTF-8 hash tests were each observed failing before their implementations were changed.

Latest command, from repository root:

```powershell
$env:PYTHONPATH='Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src'
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python -m pytest experiments/pearl-chunking-dev80-20261005/test_source_chunks.py Knowledge-Base/tests/test_parsing_and_chunking.py Knowledge-Base/tests/test_tokenization.py -q
```

Latest result after independent B0 review repair: `32 passed in 1.09s`, exit0. The source suite has19 tests and loads the actual local `memPed/knowledge/models/bge-m3/tokenizer.json` using `HuggingFaceTokenCounter`; the existing13 Knowledge-Base tests also pass. Tokenizer execution is real. Fixed-vector semantic references are algorithm checks and do not claim real model validation.

The independent reviewer found that B0 originally ended at the next token start/EOF, differing from the legacy last matched token end. A failing fixed counterexample with leading/trailing whitespace, an emoji, punctuation, internal newlines and multiple source elements reproduced this difference: `1 failed, 18 passed in 0.79s`, exit1. The adapter now trims each rendered element exactly as legacy `_render_elements` does, while retaining its original raw coordinate offset; regex windows start at `matches[start].start()` and end at `matches[end-1].end()`. Its retrieval text now equals `HierarchicalChunker()._regex_child_texts(adapted_public_body)` in the fixed reference. Whitespace-only elements do not generate B0 chunks. The explicit public changes remain removal of heading-path injection, common tables and public parents. B0 does not claim an exhaustive raw-character core partition: element-edge whitespace and regex-window boundary gaps are intentionally omitted according to historical regex semantics; all retained characters still map to original source spans.

## Remaining scope

Independent source review and root all-corpus model/saved-output verification remain separate acceptance steps. This report does not mark E0 complete. Source-view final artifacts must be rebuilt with the final source implementation because the view identity now includes the optional original document title. The prefix currently ignores external registry title metadata unless its text exists in a raw heading/title element. No synthetic title span is created. Formal support is the responsibility of the shared source support map; a uniquely located substring alone remains insufficient.
