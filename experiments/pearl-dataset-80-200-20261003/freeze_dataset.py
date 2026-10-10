"""Freeze reviewed development annotations and seal independent evaluation annotations."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from dataset_audit import STRATA, all_leakage_candidates, read_rows, require, sha, validate_structure

PILOT = ROOT / 'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json'
CORPUS = ROOT / 'paper/pearl-framework/datasets/retrieval-corpus/corpus-manifest-v02.jsonl'
SOURCES = ROOT / 'outputs/pearl-index-106-adobe-20260929-01/sources.jsonl'

def require_review(rows: list[dict], review: dict, candidate_hash: str, author_id: str) -> None:
    require(review['candidate_sha256'] == candidate_hash, 'review candidate hash mismatch')
    require(review['reviewer_id'] and review['reviewer_id'] != author_id, 'reviewer must be independent of author')
    require(not review['unresolved'], 'unresolved semantic review')
    by_id = {row['intent_id']: row for row in review['intents']}
    require(len(by_id) == len(review['intents']) == len(rows) and set(by_id) == {row['intent_id'] for row in rows}, 'semantic review intent coverage')
    for q in rows:
        decision = by_id[q['intent_id']]
        require(decision['decision'] == 'accept' and not decision['findings'] and decision['reason'], f'{q["intent_id"]}: semantic review not accepted')
        require(set(decision['checked_atom_ids']) == {a['atom_id'] for a in q['atoms']}, f'{q["intent_id"]}: semantic review atom coverage')
        require(all(decision[field] is True for field in ('stratum_confirmed', 'all_complete_paths_sufficient', 'family_distinct_within_batch')), f'{q["intent_id"]}: semantic review criterion failed')

def require_leakage_review(flags: list[dict], review: dict, expected_ids: set[str] | None = None) -> None:
    require(not any(flag['type'] in ('shared_family_id', 'exact_query', 'numeric_template') for flag in flags), 'hard family/query/template leakage requires repair')
    require(review['all_intents_semantically_scanned'] is True and not review['unresolved'], 'global family scan unresolved')
    if expected_ids is not None:
        ids = review['reviewed_intent_ids']
        require(len(ids) == len(set(ids)) and set(ids) == expected_ids, 'global semantic scan intent coverage')
    key = lambda row: (row.get('comparison_scope', 'cross_split'), row['type'], row['left'], row['right'])
    reviewed = {key(row): row for row in review['adjudications']}
    require(len(reviewed) == len(review['adjudications']) and set(reviewed) == {key(flag) for flag in flags}, 'leakage review pair coverage')
    require(all(row['decision'] == 'distinct' and row['reason'] for row in reviewed.values()), 'unresolved near-duplicate candidate')

def write_json(path: Path, value: dict) -> None:
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')

def validate_source_partition(groups: dict, universe: set[str], pilot_sources: set[str]) -> dict:
    members = {role: set(groups[role]) for role in ('dev', 'eval_a', 'eval_b')}
    require(all(len(members[role]) == len(groups[role]) for role in members), 'duplicate source partition member')
    require(not any(members[a] & members[b] for a, b in (('dev', 'eval_a'), ('dev', 'eval_b'), ('eval_a', 'eval_b'))), 'source authoring groups must be disjoint')
    require(set.union(*members.values()) == universe and len(universe) == 106, 'source partition must cover frozen 106-source inventory')
    require(pilot_sources <= members['dev'], 'pilot sources must remain in development partition')
    require({role: len(ids) for role, ids in members.items()} == {'dev': 32, 'eval_a': 37, 'eval_b': 37}, 'source partition counts')
    evaluation = members['eval_a'] | members['eval_b']
    return {'development_authoring_sources': len(members['dev']), 'evaluation_authoring_sources': len(evaluation),
            'intersection': sorted(members['dev'] & evaluation), 'retrieval_corpus_sources': len(universe)}

def validate_eval_provenance(paths: set[Path], directory: Path) -> None:
    for path in paths:
        require(path.resolve().is_relative_to(directory.resolve()), 'evaluation provenance path outside current authoring run')
        require(path.is_file(), f'evaluation provenance missing: {path}')

def freeze(config_path: Path, output: Path) -> None:
    require(not output.exists(), f'refusing to overwrite: {output}')
    config = json.loads(config_path.read_text(encoding='utf-8'))
    directory = ROOT / config['authoring_directory']
    allocation = json.loads((directory / 'source-allocation.json').read_text(encoding='utf-8'))
    for relative, expected_hash in allocation['packet_sha256'].items():
        require(sha(directory / relative) == expected_hash, f'authoring source packet changed: {relative}')
    pilot = json.loads(PILOT.read_text(encoding='utf-8'))
    require(sha(PILOT) == allocation['pilot_gold_sha256'], 'original pilot Gold changed')
    require(sha(CORPUS) == allocation['corpus_manifest_sha256'], 'frozen corpus changed')
    require(sha(SOURCES) == allocation['sources_snapshot_sha256'], 'source inventory changed')
    inventory = {row['source_id']: row for row in read_rows(SOURCES)}
    partition = validate_source_partition(allocation['groups'], set(inventory), {a['source_id'] for q in pilot['intents'] for a in q['atoms']})
    provenance, parts = {}, {}
    for role in ('dev', 'eval_a', 'eval_b'):
        item = config['parts'][role]
        candidate = ROOT / item['candidates']
        review_path = ROOT / item['review']
        audit_path = ROOT / item['audit']
        rows = read_rows(candidate)
        review = json.loads(review_path.read_text(encoding='utf-8'))
        audit = json.loads(audit_path.read_text(encoding='utf-8'))
        require(review['review_type'] == 'independent_subagent_source_semantics', 'unexpected semantic review type')
        require_review(rows, review, sha(candidate), item['author_id'])
        require(audit['status'] == 'traceability_passed' and not audit['problems'] and audit['candidate_sha256'] == sha(candidate), 'candidate traceability audit missing/stale/failed')
        require(audit['source_allocation_sha256'] == sha(directory / 'source-allocation.json'), 'audit source allocation changed')
        allowed = set(allocation['groups'][role])
        for q in rows:
            validate_structure(q, allowed)
        require(dict(Counter(q['main_stratum'] for q in rows)) == allocation['stratum_quotas'][role], 'part stratum quotas')
        parts[role] = rows
        provenance[role] = {'author_id': item['author_id'], 'reviewer_id': review['reviewer_id'],
                            'author_model_id': item.get('author_model_id', 'not_recorded'),
                            'review_model_id': review['model_id'],
                            'candidates': item['candidates'], 'candidate_sha256': sha(candidate),
                            'review': item['review'], 'review_sha256': sha(review_path),
                            'audit': item['audit'], 'audit_sha256': sha(audit_path)}
    dev = pilot['intents'] + parts['dev']
    evaluation = parts['eval_a'] + parts['eval_b']
    for rows, count in ((dev, 20), (evaluation, 50)):
        require(dict(Counter(q['main_stratum'] for q in rows)) == {kind: count for kind in STRATA}, 'final stratum quotas')
        require(len({q['intent_id'] for q in rows}) == len(rows), 'duplicate final intent ID')
    require(not {q['intent_id'] for q in dev} & {q['intent_id'] for q in evaluation}, 'intent split leakage')
    require(dev[:8] == pilot['intents'], 'original eight pilot questions changed')
    flags = all_leakage_candidates(dev, evaluation)
    leak_path = ROOT / config['leakage_review']
    leak_review = json.loads(leak_path.read_text(encoding='utf-8'))
    expected_hashes = {role: provenance[role]['candidate_sha256'] for role in parts}
    require(leak_review['candidate_sha256'] == expected_hashes and leak_review['pilot_gold_sha256'] == sha(PILOT), 'global leakage review input hashes')
    require(leak_review['reviewer_id'] not in {p['author_id'] for p in provenance.values()} | {p['reviewer_id'] for p in provenance.values()}, 'global reviewer must be independent of batch authors and reviewers')
    require_leakage_review(flags, leak_review, {q['intent_id'] for q in dev + evaluation})
    for sid in {a['source_id'] for q in dev + evaluation for a in q['atoms']}:
        require(sha(ROOT / inventory[sid]['source_path']) == inventory[sid]['sha256'], 'final source PDF changed')
        require(sha(ROOT / inventory[sid]['document_path']) == inventory[sid]['document_sha256'], 'final Adobe source changed')
    eval_provenance = set()
    for role in ('eval_a', 'eval_b'):
        eval_provenance.update(path for path in (directory / role).rglob('*') if path.is_file())
        for field in ('candidates', 'review', 'audit', 'author_log'):
            if config['parts'][role].get(field):
                eval_provenance.add(ROOT / config['parts'][role][field])
    eval_provenance.update(path for path in directory.iterdir() if path.is_file() and path.name.startswith(('eval-', 'review-eval-', 'leakage-', 'family-review-')))
    eval_provenance.add(leak_path)
    for relative in config.get('evaluation_related_extra_paths', []):
        eval_provenance.add(ROOT / relative)
    validate_eval_provenance(eval_provenance, directory)
    destination = output.resolve()
    output = destination.with_name(destination.name + '.staging')
    require(destination.is_relative_to((ROOT / 'outputs').resolve()) and output.is_relative_to((ROOT / 'outputs').resolve()), 'dataset publication paths must stay within workspace outputs')
    require(not output.exists(), f'incomplete staging run exists; preserve it and use a new run ID: {output}')
    now = datetime.now(timezone.utc).isoformat()
    output.mkdir(parents=True, exist_ok=False)
    filenames = {'dev': 'pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json',
                 'eval': 'pearl-retrieval-eval-200-adobe106-gold-20261003-r01.json'}
    actual_alternatives, profiles = {}, {}
    for split, rows in (('dev', dev), ('eval', evaluation)):
        used_sources = sorted({a['source_id'] for q in rows for a in q['atoms']})
        actual_alternatives[split] = {
            'alternative_bundle_intents': sum(any(len(r['support_bundles']) > 1 for r in q['requirements']) for q in rows),
            'extra_support_bundle_count': sum(len(r['support_bundles']) - 1 for q in rows for r in q['requirements']),
            'alternative_complete_group_intents': sum(len(q['evidence_groups']) > 1 for q in rows),
            'protocol_aspirational_alternative_group_target': 16 if split == 'dev' else 40,
            'alternative_group_target_met': sum(len(q['evidence_groups']) > 1 for q in rows) >= (16 if split == 'dev' else 40)}
        profiles[split] = {
            'source_count': len(used_sources),
            'atom_count': sum(len(q['atoms']) for q in rows),
            'requirement_count': sum(len(q['requirements']) for q in rows),
            'atom_locator_counts': dict(Counter(a['locator_type'] for q in rows for a in q['atoms'])),
            'multi_page_intents': sum(len({(a['source_id'], a['page']) for a in q['atoms']}) > 1 for q in rows),
            'intents_per_source': dict(sorted(Counter(sid for q in rows for sid in {a['source_id'] for a in q['atoms']}).items())),
            'difficulty_measure': 'Structural evidence demand only; no empirical difficulty label or retrieval outcome.'}
        gold = {'dataset_id': f'pearl-retrieval-{split}-{len(rows)}-adobe106-20261003-r01',
                'status': 'agent_reviewed_preliminary', 'gold_frozen': True,
                'split': 'development' if split == 'dev' else 'sealed_independent_evaluation',
                'query_language': 'en', 'corpus_language': 'en',
                'evaluation_executed': False, 'revision': {'number': 1, 'date': '2026-10-03', 'created_at_utc': now},
                'corpus_version': pilot['corpus_version'], 'corpus_manifest_sha256': sha(CORPUS),
                'frozen_child_library_sha256': pilot['revision']['frozen_child_library_sha256'],
                'source_allocation_sha256': sha(directory / 'source-allocation.json'),
                'source_bindings': [{'source_id': sid, 'source_path': inventory[sid]['source_path'],
                                     'source_sha256': inventory[sid]['sha256'],
                                     'adobe_document_sha256': inventory[sid]['document_sha256']} for sid in used_sources],
                'annotation_provenance': {'type': 'source_authoring_and_independent_subagent_review', 'parts': provenance,
                                          'original_pilot_gold_sha256': sha(PILOT) if split == 'dev' else None,
                                          'leakage_review_sha256': sha(leak_path), 'quality': 'Agent-reviewed; not human Gold'},
                'alternative_support_actual': actual_alternatives[split], 'intents': rows}
        write_json(output / filenames[split], gold)
    eval_path = output / filenames['eval']
    os.chmod(eval_path, stat.S_IREAD)
    require(not bool(eval_path.stat().st_mode & stat.S_IWRITE), 'evaluation file read-only seal failed')
    sealed_provenance = {}
    for path in sorted(eval_provenance):
        require(path.resolve().is_relative_to(directory.resolve()), 'evaluation provenance path outside current authoring run')
        os.chmod(path, stat.S_IREAD)
        require(not bool(path.stat().st_mode & stat.S_IWRITE), 'evaluation provenance seal failed')
        sealed_provenance[path.relative_to(ROOT).as_posix()] = sha(path)
    manifest = {'status': 'dev80_frozen_eval200_sealed', 'created_at_utc': now, 'date': '2026-10-03',
                'run_id': destination.name, 'development_count': 80, 'evaluation_count': 200,
                'query_language': 'en', 'corpus_language': 'en',
                'strata': {'dev': {key: 20 for key in STRATA}, 'eval': {key: 50 for key in STRATA}},
                'evaluation_executed': False, 'evaluation_content_readonly': True,
                'evaluation_access_policy': 'No developer tuning reads or changes after this seal. Independent evaluation requires frozen method configuration and a separately named run. Hash verification is allowed.',
                'source_partition': partition,
                'pilot_questions_preserved': True, 'pilot_gold_sha256': sha(PILOT),
                'alternative_support_actual': actual_alternatives,
                'dataset_profile': profiles,
                'leakage_flags_adjudicated': len(flags), 'leakage_review_sha256': sha(leak_path),
                'global_review_identity': {'reviewer_id': leak_review['reviewer_id'], 'model_id': leak_review['model_id']},
                'config_sha256': sha(config_path), 'code_sha256': {p.name: sha(p) for p in (Path(__file__), HERE / 'dataset_audit.py', HERE / 'prepare_authoring.py')},
                'source_packet_hashes_verified': len(allocation['packet_sha256']),
                'annotation_spec_sha256': sha(HERE / 'authoring-spec.md'),
                'model_config_sha256': {'reranker-config.json': sha(ROOT / 'experiments/pearl-index-106-adobe-20260929/reranker-config.json')},
                'artifacts': {split: {'path': name, 'sha256': sha(output / name)} for split, name in filenames.items()},
                'review_provenance': provenance,
                'sealed_evaluation_provenance_sha256': sealed_provenance,
                'limits': ['Agent-reviewed preliminary Gold; no human adjudication.',
                           'No formal retrieval scores for the 80/200 sets have been run.',
                           'Alternative complete-group coverage is reported as observed. An unmet aspirational target limits alternative-group analysis; equivalent groups are not fabricated.']}
    write_json(output / 'seal_manifest.json', manifest)
    os.chmod(output / 'seal_manifest.json', stat.S_IREAD)
    require(not bool((output / 'seal_manifest.json').stat().st_mode & stat.S_IWRITE), 'seal manifest read-only attribute failed')
    require(all(sha(output / artifact['path']) == artifact['sha256'] for artifact in manifest['artifacts'].values()), 'staged Gold hash verification failed')
    require(all(sha(ROOT / relative) == expected for relative, expected in sealed_provenance.items()), 'sealed provenance hash verification failed')
    # Publish only the completed manifest and verified artifacts, on the same filesystem.
    os.rename(output, destination)
    print(json.dumps({'output': str(destination), 'status': manifest['status'], 'gold_sha256': {key: value['sha256'] for key, value in manifest['artifacts'].items()}}, sort_keys=True))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    freeze(args.config.resolve(), args.output_dir.resolve())
