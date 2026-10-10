"""Merge blinded R4 support decisions and uniformly rescore R1-R4 at K<=20."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from score_pilot import KS, score_prefix  # noqa: E402


BASE = ROOT / 'outputs/pearl-retrieval-dev-pilot-8-adobe106-20260929-01'
R4 = ROOT / 'outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01'
GOLD = ROOT / 'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json'
OLD_MAP = BASE / 'pearl-retrieval-dev-pilot-8-adobe106-support-map-pearl-retrieval-dev-pilot-8-adobe106-20260929-01.json'
NEW_MAP = R4 / 'pearl-retrieval-dev-pilot-8-adobe106-support-map-pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01.json'
SCORES = R4 / 'preliminary-scores-r1-r4.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def write_json(path: Path, value: dict) -> None:
    if path.exists():
        raise FileExistsError(f'refusing to overwrite: {path}')
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')


def validate_new_reviews(required: dict[str, set[str]], reviews: list[dict]) -> None:
    if len(reviews) != len({row['intent_id'] for row in reviews}) or set(required) != {row['intent_id'] for row in reviews}:
        raise ValueError('review intent coverage mismatch')
    for review in reviews:
        ident = review['intent_id']
        if review.get('unresolved'):
            raise ValueError(f'unresolved review: {ident}')
        decisions = review['decisions']
        ids = [decision['chunk_ids'][0] for decision in decisions if len(decision['chunk_ids']) == 1]
        if len(ids) != len(decisions) or len(ids) != len(set(ids)) or set(ids) != required[ident]:
            raise ValueError(f'blind review candidate coverage mismatch: {ident}')
        if any(not decision.get('reason') or not isinstance(decision.get('supports'), list) for decision in decisions):
            raise ValueError(f'incomplete blind review decision: {ident}')


def main() -> None:
    if NEW_MAP.exists() or SCORES.exists():
        raise FileExistsError('refusing to overwrite support map or scores')
    gold = json.loads(GOLD.read_text(encoding='utf-8'))
    old_map = json.loads(OLD_MAP.read_text(encoding='utf-8'))
    base_run = json.loads((BASE / 'run_manifest.json').read_text(encoding='utf-8'))
    r4_run = json.loads((R4 / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in base_run['output_sha256'].items():
        if sha(BASE / name) != expected:
            raise ValueError(f'base run changed: {name}')
    for name, expected in r4_run['output_sha256'].items():
        if sha(R4 / name) != expected:
            raise ValueError(f'R4 run changed: {name}')
    if any(value != sha(GOLD) for value in (base_run['gold_sha256'], r4_run['gold_sha256'], old_map['gold_sha256'])):
        raise ValueError('Gold identity mismatch')
    if old_map['rankings_sha256'] != sha(BASE / 'rankings.jsonl') or r4_run['r3_rankings_sha256'] != sha(BASE / 'rankings.jsonl'):
        raise ValueError('R1-R3 ranking identity mismatch')
    q_by = {row['intent_id']: row for row in gold['intents']}
    old_by = {row['intent_id']: row for row in old_map['intents']}
    base_rows = read_jsonl(BASE / 'rankings.jsonl')
    r4_rows = read_jsonl(R4 / 'rankings-r4.jsonl')
    r3_by = {row['intent_id']: row for row in base_rows if row['method'] == 'R3'}
    required_old = defaultdict(set)
    for row in read_jsonl(BASE / 'review_required_top20_blind.jsonl'):
        required_old[row['intent_id']].add(row['chunk_id'])
    new_pool = read_jsonl(R4 / 'review_new_top20_blind.jsonl')
    required_new = defaultdict(set)
    pool_by = defaultdict(set)
    for row in new_pool:
        if any(field in row for field in ('rank', 'r3_rank', 'score', 'method')):
            raise ValueError('new review pool is not blind')
        required_new[row['intent_id']].add(row['chunk_id'])
        pool_by[row['intent_id']].add(row['chunk_id'])
    for row in r4_rows:
        ident = row['intent_id']
        r3 = r3_by[ident]
        if row['query'] != q_by[ident]['query'] or len(row['results']) != 100:
            raise ValueError(f'R4 ranking invalid: {ident}')
        if {r['chunk_id']: (r['text'], r['text_sha256']) for r in row['results']} != {
                r['chunk_id']: (r['text'], r['text_sha256']) for r in r3['results']}:
            raise ValueError(f'R3/R4 candidate identity mismatch: {ident}')
        expected_new = {r['chunk_id'] for r in row['results'][:20]} - required_old[ident]
        if expected_new != required_new[ident]:
            raise ValueError(f'new blind review pool mismatch: {ident}')
    if len(r4_rows) != len(q_by) or set(r3_by) != set(q_by):
        raise ValueError('intent matrix incomplete')
    review_names = ('review-r4-001-004.json', 'review-r4-005-008.json')
    review_rows = []
    for name in review_names:
        data = json.loads((R4 / name).read_text(encoding='utf-8'))
        review_rows.extend(data['intents'])
    validate_new_reviews(required_new, review_rows)
    review_by = {row['intent_id']: row for row in review_rows}
    merged_rows = []
    for ident, q in q_by.items():
        old = old_by[ident]
        new = review_by[ident]
        atom_ids = {atom['atom_id'] for atom in q['atoms']}
        additions = new.get('atom_paths_additions', {})
        if not set(additions) <= atom_ids:
            raise ValueError(f'unknown atom in review additions: {ident}')
        all_candidates = {row['chunk_id'] for row in read_jsonl(BASE / 'review_pool_blind.jsonl') if row['intent_id'] == ident} | pool_by[ident]
        paths = {atom: [list(path) for path in old['atom_paths'][atom]] for atom in atom_ids}
        for atom, new_paths in additions.items():
            for path in new_paths:
                if not path or not set(path) <= all_candidates or not set(path) & required_new[ident]:
                    raise ValueError(f'invalid new support path: {ident}/{atom}')
                if path not in paths[atom]:
                    paths[atom].append(path)
        for decision in new['decisions']:
            if not set(decision['supports']) <= atom_ids:
                raise ValueError(f'unknown atom in decision: {ident}')
        merged_rows.append({**old, 'decisions': old['decisions'] + new['decisions'],
                            'atom_paths': paths, 'unresolved': [],
                            'review_coverage': {**old['review_coverage'],
                                                'new_r4_required_count': len(required_new[ident]),
                                                'new_r4_required_reviewed': True}})
    mapping = {
        'status': 'agent_reviewed_development_pilot_r1_r4',
        'review_type': 'subagent_blind_content',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'run_id': r4_run['run_id'], 'source_run_id': base_run['run_id'],
        'scoring_range': list(KS), 'gold_sha256': sha(GOLD),
        'base_support_map_sha256': sha(OLD_MAP),
        'base_rankings_sha256': sha(BASE / 'rankings.jsonl'),
        'r4_rankings_sha256': sha(R4 / 'rankings-r4.jsonl'),
        'new_blind_pool_sha256': sha(R4 / 'review_new_top20_blind.jsonl'),
        'review_sha256': {name: sha(R4 / name) for name in review_names},
        'new_review_candidate_count': len(new_pool),
        'deep_21_100_support_status': 'not_exhaustively_adjudicated',
        'intents': merged_rows,
    }
    all_rankings = base_rows + r4_rows
    if len(all_rankings) != len(q_by) * 4 or {(r['intent_id'], r['method']) for r in all_rankings} != {
            (ident, method) for ident in q_by for method in ('R1', 'R2', 'R3', 'R4')}:
        raise ValueError('ranking matrix incomplete')
    path_by = {row['intent_id']: row['atom_paths'] for row in merged_rows}
    details = []
    for row in all_rankings:
        ident = row['intent_id']
        if row['query'] != q_by[ident]['query'] or len(row['results']) != 100:
            raise ValueError(f'bad ranking: {ident}/{row["method"]}')
        ids = [item['chunk_id'] for item in row['results']]
        if len(ids) != len(set(ids)) or [item['rank'] for item in row['results']] != list(range(1, 101)):
            raise ValueError(f'bad ranking order: {ident}/{row["method"]}')
        details.append({'intent_id': ident, 'method': row['method'],
                        'scores': {str(k): score_prefix(q_by[ident], path_by[ident], ids, k) for k in KS}})
    summary = {method: {str(k): {label: sum(row['scores'][str(k)][field] for row in details if row['method'] == method) / len(q_by)
                                  for label, field in (('CEGR', 'CEGR'), ('BestGroupCov', 'BestGroupCov'), ('CompleteMRR', 'CompleteRR'))}
                        for k in KS} for method in ('R1', 'R2', 'R3', 'R4')}
    write_json(NEW_MAP, mapping)
    write_json(SCORES, {
        'status': 'preliminary_eight_intent_development_comparison',
        'run_id': r4_run['run_id'], 'intent_count': len(q_by), 'methods': ['R1', 'R2', 'R3', 'R4'],
        'k': list(KS), 'gold_sha256': sha(GOLD), 'mapping_sha256': sha(NEW_MAP),
        'base_rankings_sha256': sha(BASE / 'rankings.jsonl'),
        'r4_rankings_sha256': sha(R4 / 'rankings-r4.jsonl'),
        'summary': summary, 'details': details,
        'interpretation': 'Eight development intents only. Agent-reviewed child-content support; not human Gold or sealed evaluation.',
    })
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
