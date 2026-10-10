"""Score reviewed R1 child-to-atom support paths on the eight-intent pilot."""

from __future__ import annotations

import hashlib
import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GOLD = HERE / "pilot-intents-agent-reviewed-v3.json"
KS = (1, 5, 10, 20)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--gold', type=Path, default=GOLD)
    parser.add_argument('--mapping', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    gold_path = args.gold.resolve()
    run = json.loads((directory / "run-manifest.json").read_text(encoding="utf-8"))
    if run["rankings_sha256"] != digest(directory / "rankings.jsonl"):
        raise ValueError("rankings hash mismatch")
    original_gold = json.loads(GOLD.read_text(encoding="utf-8"))
    if run["pilot_sha256"] != digest(GOLD):
        raise ValueError("original Gold hash mismatch")
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    if {q['intent_id']: q['query'] for q in gold['intents']} != {q['intent_id']: q['query'] for q in original_gold['intents']}:
        raise ValueError('rescoring cannot change query identities or query text')
    if gold['corpus_manifest_sha256'] != run['corpus_manifest_sha256']:
        raise ValueError('corpus hash mismatch')
    if digest(directory / 'children.jsonl') != run['children_sha256']:
        raise ValueError('child library hash mismatch')
    rankings = {row["intent_id"]: row for row in map(json.loads,
                (directory / "rankings.jsonl").read_text(encoding="utf-8").splitlines())}
    mapping_path = args.mapping or directory / "support-mapping-agent-reviewed.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    if mapping["gold_sha256"] != digest(gold_path) or mapping["rankings_sha256"] != digest(directory / "rankings.jsonl"):
        raise ValueError("support mapping input hash mismatch")
    if mapping["candidate_pool_sha256"] != digest(directory / "support-review-pool-top20.jsonl"):
        raise ValueError("support review pool hash mismatch")
    if mapping["review_type"] != "subagent_blind_top20":
        raise ValueError("mapping review type mismatch")
    by_intent = {row["intent_id"]: row for row in mapping["intents"]}
    if set(by_intent) != {q["intent_id"] for q in gold["intents"]}:
        raise ValueError("mapping intent coverage mismatch")
    details = []
    for q in gold["intents"]:
        ident = q["intent_id"]
        decision = by_intent[ident]
        if decision["unresolved"]:
            raise ValueError(f"unresolved support: {ident}")
        ranking = rankings[ident]["results"]
        if len(ranking) < 20 or any(row["rank"] != i for i, row in enumerate(ranking, 1)):
            raise ValueError(f"invalid ranking: {ident}")
        top20 = {row["chunk_id"] for row in ranking[:20]}
        atoms = {a["atom_id"] for a in q["atoms"]}
        paths = decision["atom_paths"]
        if set(paths) != atoms:
            raise ValueError(f"atom decision coverage mismatch: {ident}")
        for atom_id, alternatives in paths.items():
            if any(not path or not set(path) <= top20 for path in alternatives):
                raise ValueError(f"invalid child support path: {ident} {atom_id}")
        requirements = {r["requirement_id"]: r for r in q["requirements"]}
        gold_sources = {a["source_id"] for a in q["atoms"]}
        gold_pages = {(a["source_id"], a["page"]) for a in q["atoms"]}
        row = {"intent_id": ident, "stratum": q["main_stratum"], "scores": {}}
        for k in KS:
            seen = {result["chunk_id"] for result in ranking[:k]}
            atom_hit = {aid: any(set(path) <= seen for path in alternatives)
                        for aid, alternatives in paths.items()}
            req_hit = {rid: any(all(atom_hit[aid] for aid in bundle)
                            for bundle in req["support_bundles"])
                       for rid, req in requirements.items()}
            coverages = [sum(req_hit[rid] for rid in group["requirements"]) / len(group["requirements"])
                         for group in q["evidence_groups"]]
            complete = int(any(value == 1.0 for value in coverages))
            first_complete = None
            if complete:
                for prefix in range(1, k + 1):
                    prefix_seen = {result["chunk_id"] for result in ranking[:prefix]}
                    prefix_atoms = {aid: any(set(path) <= prefix_seen for path in alternatives)
                                    for aid, alternatives in paths.items()}
                    prefix_reqs = {rid: any(all(prefix_atoms[aid] for aid in bundle)
                                   for bundle in req["support_bundles"])
                                   for rid, req in requirements.items()}
                    if any(all(prefix_reqs[rid] for rid in group["requirements"])
                           for group in q["evidence_groups"]):
                        first_complete = prefix
                        break
            current = ranking[:k]
            row["scores"][str(k)] = {"CEGR": complete, "BestGroupCov": max(coverages),
                                       "CompleteRR": 1 / first_complete if first_complete else 0.0,
                                       "first_complete_rank": first_complete,
                                       "AnySourceHit": int(any(x["source_id"] in gold_sources for x in current)),
                                       "AnyPageHit": int(any((x["source_id"], x["page"]) in gold_pages
                                                              for x in current)),
                                       "requirements_hit": req_hit}
        details.append(row)
    summary = {"status": "preliminary_known_gold_support_lower_bound", "n": len(details),
               "gold_sha256": digest(gold_path), "rankings_sha256": digest(directory / "rankings.jsonl"),
               "support_mapping_sha256": digest(mapping_path), "method": "R1_BM25_smoke",
               "interpretation": "Scores use agent-reviewed support for registered v3 source atoms only. Equivalent source passages found during review are not yet registered, so these are provisional known-support values and may increase after a uniform Gold/mapping revision.",
               "by_k": {str(k): {metric: sum(row["scores"][str(k)][metric] for row in details) / len(details)
                                  for metric in ("CEGR", "BestGroupCov", "CompleteRR", "AnySourceHit", "AnyPageHit")}
                        for k in KS}, "details": details}
    if gold_path != GOLD.resolve():
        summary['status'] = 'preliminary_agent_reviewed_registered_support'
        summary['interpretation'] = 'Development-only revision analysis on unchanged R1 rankings; registered equivalent evidence has been reviewed by subagents. Not a four-method comparison or sealed evaluation result; support beyond the reviewed top-20 pool is not adjudicated.'
        summary['gold_dataset_id'] = gold['dataset_id']
        summary['original_gold_sha256'] = run['pilot_sha256']
        summary['original_run_manifest_sha256'] = digest(directory / 'run-manifest.json')
        summary['children_sha256'] = run['children_sha256']
        if args.output is None:
            raise ValueError('revised Gold requires a separately named --output')
    target = args.output or directory / "preliminary-scores.json"
    if target.exists():
        if json.loads(target.read_text(encoding="utf-8")) != summary:
            raise SystemExit(f"existing score differs; refusing to overwrite: {target}")
    else:
        target.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"n": summary["n"], "by_k": summary["by_k"]}, sort_keys=True))


if __name__ == "__main__":
    main()
