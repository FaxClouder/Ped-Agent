# PEARL development child support review

*Independent content review contract · status: current · 2026-10-03*

The reviewer reads only its assigned content packets and this contract. It must not inspect execution records, retrieval code, other reviewers' decisions, or any sealed evaluation material. Packets contain no method identity, order, rank, or score. Source metadata establishes identity and traceability; source or page coincidence does not establish content support.

For every assigned intent, read the entire actual text of every `candidates` child. Check the semantic question, answer, each requirement's claim and scope, and every atom. Check subject, population, experiment identity, setting, condition, numbers, decimal precision, units and table headings. Explicitly inspect multiple-child combinations that supply complementary information. Count only literal child content, with same-study links where needed. Do not supply missing information from a parent, source PDF, reference answer, or external knowledge. If text is corrupted, ambiguous or contradictory, retain the issue and do not lower the requirement. Supplementary content may establish additional positive paths, but anything not sufficiently reviewed stays unresolved.

The source anchors describe frozen semantic evidence. Semantically equivalent actual child text may count when it supports the same fact and all necessary conditions; preserve the reason and actual excerpts. Never treat lexical matches or similarity scores as support labels. Never generate accepted paths or blanket negatives by an automated heuristic. Helpers may arrange and search content for reading; all decisions require actual content adjudication by the reviewer.

Write one new JSON file in `review/decisions/<intent_id>.json`, using this schema:

```json
{
  "review_type": "subagent_blind_content",
  "packet_sha256": "sha256 of the exact assigned packet bytes",
  "intent_id": "pearl-dev-000",
  "reviewer_id": "actual agent identifier",
  "reviewer_configuration": "inherited session configuration; no override",
  "atom_paths": {"a1": [["child-id-1", "child-id-2"]], "a2": []},
  "path_evidence": [
    {"atom_id": "a1", "chunk_ids": ["child-id-1", "child-id-2"],
     "reason": "Explain how these texts jointly provide the complete atom and necessary scope.",
     "excerpts": [{"chunk_id": "child-id-1", "text": "Exact literal substring"},
                  {"chunk_id": "child-id-2", "text": "Exact literal substring"}]}
  ],
  "reviewed_ids": ["every candidate ID and any sufficiently reviewed supplementary ID"],
  "unresolved_ids": ["unreviewed supplementary IDs only"],
  "rejection_summary": "Explain negative candidates and ambiguous near misses, grouping by concrete content mismatch when useful.",
  "notes": "Processing loss or limitations; no retrieval outcome inference."
}
```

`atom_paths` must include every atom, including atoms with no actual support. Within a path, all children are necessary together (AND); paths for one atom are independent sufficient alternatives (OR). One child may support several atoms. An atom with only a value and no necessary unit/heading/condition must have no complete path until sufficient joint content is found. Minimal paths make first-completion scoring interpretable. For each accepted path supply nonempty literal excerpts from every child and a semantic reason. Every `candidates` ID must appear in `reviewed_ids`; if any remains semantically unresolved, do not pretend completion: report it to the coordinator for adjudication. Every remaining supplementary ID must be explicitly unresolved. Do not overwrite any existing decision; revisions use separate filenames and an explicit revision trail.

Report a compact completion count and actual limitations. The status remains Agent-reviewed preliminary, with no human verification claim.
