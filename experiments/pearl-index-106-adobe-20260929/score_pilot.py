"""Combine blinded reviews and score the eight-intent Adobe development pilot."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / 'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json'
KS = (1, 5, 10, 20)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def write_json(path: Path, value: dict) -> None:
    if path.exists():
        raise FileExistsError(f'refusing to overwrite: {path}')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


def requirement_hits(gold: dict, paths: dict, seen: set[str]) -> dict[str, bool]:
    atoms = {a['atom_id']: any(set(path) <= seen for path in paths[a['atom_id']])
             for a in gold['atoms']}
    return {req['requirement_id']: any(all(atoms[atom] for atom in bundle)
              for bundle in req['support_bundles']) for req in gold['requirements']}


def score_prefix(gold: dict, paths: dict, ranking: list[str], k: int) -> dict:
    seen = set(ranking[:k])
    hits = requirement_hits(gold, paths, seen)
    cov = {g['group_id']: sum(hits[r] for r in g['requirements']) / len(g['requirements'])
           for g in gold['evidence_groups']}
    complete = int(any(value == 1 for value in cov.values()))
    first_complete = None
    if complete:
        for position in range(1, min(k, len(ranking)) + 1):
            prefix_hits = requirement_hits(gold, paths, set(ranking[:position]))
            if any(all(prefix_hits[r] for r in g['requirements']) for g in gold['evidence_groups']):
                first_complete = position
                break
    return {'CEGR': complete, 'BestGroupCov': max(cov.values()),
            'CompleteRR': 1 / first_complete if first_complete else 0.0,
            'first_complete_rank': first_complete, 'group_coverage': cov,
            'requirements_hit': hits}


def combine(directory: Path, output: Path, gold_path: Path) -> None:
    gold = json.loads(gold_path.read_text(encoding='utf-8'))
    run = json.loads((directory / 'run_manifest.json').read_text(encoding='utf-8'))
    if run['gold_sha256'] != sha(gold_path):
        raise ValueError('run Gold SHA mismatch')
    required = read_jsonl(directory / 'review_required_top20_blind.jsonl')
    pool = read_jsonl(directory / 'review_pool_blind.jsonl')
    required_by = {q['intent_id']: {r['chunk_id'] for r in required if r['intent_id'] == q['intent_id']}
                   for q in gold['intents']}
    pool_by = {q['intent_id']: {r['chunk_id'] for r in pool if r['intent_id'] == q['intent_id']}
               for q in gold['intents']}
    reviewed = []
    review_names = ('review-intents-001-004.json', 'review-intents-005-008.json')
    for name in review_names:
        data = json.loads((directory / name).read_text(encoding='utf-8'))
        if data['review_type'] != 'subagent_blind_content':
            raise ValueError('unexpected review type')
        reviewed.extend(data['intents'])
    by_id = {row['intent_id']: row for row in reviewed}
    if len(reviewed) != len(by_id) or set(by_id) != set(required_by):
        raise ValueError('review does not cover eight distinct intents')
    for q in gold['intents']:
        ident = q['intent_id']
        decision = by_id[ident]
        if decision['unresolved']:
            raise ValueError(f'unresolved scoring-range support: {ident}')
        if set(decision['atom_paths']) != {a['atom_id'] for a in q['atoms']}:
            raise ValueError(f'atom coverage mismatch: {ident}')
        for atom_id, paths in decision['atom_paths'].items():
            for path in paths:
                if not path or not set(path) <= pool_by[ident]:
                    raise ValueError(f'path uses absent blind-pool child: {ident}/{atom_id}')
        coverage = decision.get('review_coverage', {})
        covered = coverage.get('required_count')
        if covered != len(required_by[ident]) or coverage.get('all_required_reviewed') is not True:
            raise ValueError(f'blinded top20 review count mismatch: {ident}: {covered} vs {len(required_by[ident])}')
    write_json(output, {'status': 'agent_reviewed_development_pilot', 'review_type': 'subagent_blind_content',
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'run_id': run['run_id'],
        'gold_sha256': sha(gold_path), 'rankings_sha256': sha(directory / 'rankings.jsonl'),
        'candidate_pool_sha256': sha(directory / 'review_pool_blind.jsonl'),
        'required_pool_sha256': sha(directory / 'review_required_top20_blind.jsonl'),
        'review_sha256': {name: sha(directory / name) for name in review_names},
        'scoring_range': list(KS), 'intents': [by_id[q['intent_id']] for q in gold['intents']]})


def score(directory: Path, mapping_path: Path, output: Path, gold_path: Path) -> None:
    gold = json.loads(gold_path.read_text(encoding='utf-8'))
    mapping = json.loads(mapping_path.read_text(encoding='utf-8'))
    run = json.loads((directory / 'run_manifest.json').read_text(encoding='utf-8'))
    if run['gold_sha256'] != sha(gold_path) or mapping['gold_sha256'] != sha(gold_path):
        raise ValueError('Gold hash mismatch')
    if mapping['rankings_sha256'] != sha(directory / 'rankings.jsonl'):
        raise ValueError('rankings hash mismatch')
    for name, expected in run['output_sha256'].items():
        if sha(directory / name) != expected:
            raise ValueError(f'run output changed: {name}')
    if mapping['required_pool_sha256'] != sha(directory / 'review_required_top20_blind.jsonl'):
        raise ValueError('review pool changed')
    q_by = {q['intent_id']: q for q in gold['intents']}
    paths_by = {r['intent_id']: r['atom_paths'] for r in mapping['intents']}
    rankings = read_jsonl(directory / 'rankings.jsonl')
    if len(rankings) != len(q_by) * len(run['methods_executed']):
        raise ValueError('missing method/intent ranking')
    details = []
    for row in rankings:
        ident = row['intent_id']
        if ident not in q_by or row['method'] not in run['methods_executed'] or row['query'] != q_by[ident]['query']:
            raise ValueError('ranking identity mismatch')
        results = row['results']
        if len(results) != 100 or [r['rank'] for r in results] != list(range(1, 101)):
            raise ValueError('invalid Top-100 ranking')
        ids = [r['chunk_id'] for r in results]
        if len(set(ids)) != 100:
            raise ValueError('duplicate result ID')
        scored = {str(k): score_prefix(q_by[ident], paths_by[ident], ids, k) for k in KS}
        details.append({'intent_id': ident, 'method': row['method'], 'scores': scored})
    if len({(r['intent_id'], r['method']) for r in details}) != len(details):
        raise ValueError('duplicate method/intent ranking')
    summary = {method: {str(k): {label: sum(r['scores'][str(k)][field] for r in details
                                              if r['method'] == method) / len(q_by)
                                  for label, field in (('CEGR', 'CEGR'), ('BestGroupCov', 'BestGroupCov'),
                                                       ('CompleteMRR', 'CompleteRR'))}
                        for k in KS} for method in run['methods_executed']}
    write_json(output, {'status': 'preliminary_eight_intent_development_comparison',
        'run_id': run['run_id'], 'intent_count': len(q_by), 'methods': run['methods_executed'],
        'not_executed': {'R4': run['r4_status']}, 'k': list(KS),
        'gold_sha256': sha(gold_path), 'mapping_sha256': sha(mapping_path),
        'rankings_sha256': sha(directory / 'rankings.jsonl'), 'summary': summary, 'details': details,
        'interpretation': 'Eight development intents only. Agent-reviewed child-content support; not human Gold or sealed evaluation.'})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('combine', 'score'))
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mapping', type=Path)
    parser.add_argument('--gold', type=Path, default=GOLD)
    args = parser.parse_args()
    if args.command == 'combine':
        combine(args.directory.resolve(), args.output.resolve(), args.gold.resolve())
    else:
        if args.mapping is None:
            parser.error('--mapping is required for score')
        score(args.directory.resolve(), args.mapping.resolve(), args.output.resolve(), args.gold.resolve())


if __name__ == '__main__':
    main()
