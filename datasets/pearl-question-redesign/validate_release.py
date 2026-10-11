"""Read-only release verification. Requires Python 3.10+, standard library only."""
from pathlib import Path
import argparse
import collections
import hashlib
import json


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(release):
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    manifest_bytes = (release / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    require(manifest['release_id'] == release.name, 'release directory identity mismatch')
    names = [f['path'] for f in manifest['files']]
    require(len(names) == len(set(names)), 'duplicate manifest paths')
    for entry in manifest['files']:
        path = release / entry['path']
        require(path.resolve().parent == release.resolve(), 'manifest path outside release root')
        if path.resolve().parent != release.resolve():
            continue
        require(path.is_file(), f'missing file: {entry["path"]}')
        if path.is_file():
            raw = path.read_bytes()
            require(digest(raw) == entry['sha256'], f'hash mismatch: {entry["path"]}')
            require(len(raw) == entry['bytes'], f'byte size mismatch: {entry["path"]}')
    expected = set(names) | {'manifest.json', 'validation.json'}
    require({p.name for p in release.iterdir() if p.is_file()} <= expected,
            'unlisted release files')
    contract_path = (release / manifest['contract_path']).resolve()
    require(contract_path.parent == release.parent.parent.resolve() / 'contracts',
            'unexpected contract location')
    if errors:
        return {'status': 'failed', 'errors': errors}
    contract_raw = contract_path.read_bytes()
    require(digest(contract_raw) == manifest['contract_sha256'], 'contract hash mismatch')
    contract = json.loads(contract_raw)
    tables = {}
    for name, required in contract['files'].items():
        rows = [json.loads(s) for s in (release / name).read_text(encoding='utf-8').splitlines() if s.strip()]
        ids = [row['candidate_id'] for row in rows]
        require(len(rows) == manifest['question_count'], f'{name}: record count')
        require(len(ids) == len(set(ids)), f'{name}: duplicate IDs')
        for row in rows:
            require(set(required) <= row.keys(), f'{name}: missing required keys {row["candidate_id"]}')
        tables[name] = {row['candidate_id']: row for row in rows}
    candidates = tables['candidates.jsonl']
    for name, table in tables.items():
        require(set(table) == set(candidates), f'{name}: mismatched ID set')
    if errors:
        return {'status': 'failed', 'errors': errors}
    sources = {s['source_id'] for s in json.loads((release / 'source_catalog.json').read_text(encoding='utf-8'))}
    bindings = tables['bindings.jsonl']
    atoms_count = requirements_count = 0
    for cid, c in candidates.items():
        a = tables['answers.jsonl'][cid]
        q = tables['qa.jsonl'][cid]
        b = bindings[cid]
        require(c['question_revision'] == a['question_revision'] == q['question_revision'] == b['question_revision'], f'{cid}: question revision')
        require(a['answer_revision'] == q['answer_revision'], f'{cid}: answer revision')
        require(q['decision'] in contract['allowed_decisions'], f'{cid}: decision')
        for key in ('question_revision',):
            require(type(c[key]) is int and c[key] > 0, f'{cid}: positive revision')
        for key in ('is_blind', 'human_verified', 'gold_frozen'):
            require(q[key] is False, f'{cid}: imported candidate review/freeze flag changed')
        for name, record in [('candidate', c), ('answer', a), ('qa', q)]:
            require(digest(canonical(record)) == b[f'{name}_record_sha256'], f'{cid}: local {name} binding')
        require(digest(canonical(c)) == q['candidate_record_sha256'], f'{cid}: upstream candidate record hash')
        require(digest(canonical(a)) == q['answer_record_sha256'], f'{cid}: upstream answer record hash')
        atom_ids = [x['atom_id'] for x in a['atoms']]
        req_ids = [x['requirement_id'] for x in a['requirements']]
        require(len(atom_ids) == len(set(atom_ids)), f'{cid}: duplicate atoms')
        require(len(req_ids) == len(set(req_ids)), f'{cid}: duplicate requirements')
        for atom in a['atoms']:
            require(atom['source_id'] in sources, f'{cid}: unknown source')
            require(set(atom.get('supports_requirement_ids', [])) <= set(req_ids), f'{cid}: dangling requirement')
        for req in a['requirements']:
            for bundle in req.get('support_bundles', []):
                require(set(bundle) <= set(atom_ids), f'{cid}: dangling atom in local bundle')
        for bundle in a['answer_support_bundles']:
            require(set(bundle) <= set(atom_ids), f'{cid}: dangling atom in answer bundle')
        require(set(a.get('gap_requirements', [])) <= set(req_ids), f'{cid}: dangling gap requirement')
        atoms_count += len(atom_ids)
        requirements_count += len(req_ids)
    decisions = dict(collections.Counter(q['decision'] for q in tables['qa.jsonl'].values()))
    require(decisions == manifest['expected_decisions'], 'decision totals mismatch')
    metadata = json.loads((release / 'metadata.json').read_text(encoding='utf-8'))
    require(atoms_count == metadata['revised_atoms'], 'atom totals mismatch')
    require(requirements_count == metadata['revised_requirements'], 'requirement totals mismatch')
    return {'status': 'passed' if not errors else 'failed', 'errors': errors,
            'release_id': manifest['release_id'], 'manifest_sha256': digest(manifest_bytes),
            'validator_sha256': digest(Path(__file__).read_bytes()),
            'question_count': len(candidates), 'decisions': decisions,
            'atoms': atoms_count, 'requirements': requirements_count,
            'scope': 'file hashes, contracts, record identity/version/hash bindings and reference integrity only',
            'not_verified': ['PDF semantic support', 'independent blind review', 'upstream standalone files and contract hash reproduction', 'Gold freeze eligibility', 'system performance']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('release', type=Path)
    args = parser.parse_args()
    try:
        result = check(args.release.resolve())
    except (OSError, KeyError, TypeError, ValueError) as exc:
        result = {'status': 'failed', 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'passed' else 1)
