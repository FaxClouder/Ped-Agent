"""Validated PEARL DNF scorer; reuse the current Adobe pilot numerical functions."""
import importlib.util
from pathlib import Path

PILOT = Path(__file__).resolve().parents[1] / 'pearl-index-106-adobe-20260929/score_pilot.py'
spec = importlib.util.spec_from_file_location('pearl_adobe_pilot_score', PILOT)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)

def validate_gold(g):
    for field in ('atoms','requirements','evidence_groups'):
        if not g.get(field): raise ValueError('empty Gold '+field)
    atoms=[a['atom_id'] for a in g['atoms']]
    reqs=[r['requirement_id'] for r in g['requirements']]
    groups=[r['group_id'] for r in g['evidence_groups']]
    if any(len(x)!=len(set(x)) for x in (atoms,reqs,groups)): raise ValueError('duplicate Gold ID')
    for r in g['requirements']:
        bundles=r['support_bundles']
        if not bundles or any(not b or len(b)!=len(set(b)) or not set(b)<=set(atoms) for b in bundles):
            raise ValueError('invalid or empty bundle')
    for group in g['evidence_groups']:
        rs=group['requirements']
        if not rs or len(rs)!=len(set(rs)) or not set(rs)<=set(reqs): raise ValueError('invalid or empty group')

def score_prefix(g, paths, ranking, k):
    validate_gold(g)
    if set(paths)!={a['atom_id'] for a in g['atoms']}: raise ValueError('missing atom paths')
    if any(not p for ps in paths.values() for p in ps): raise ValueError('empty support path')
    return pilot.score_prefix(g, paths, ranking, k)

def require_reviewed(ranking, reviewed_ids, k):
    if not set(ranking[:k])<=set(reviewed_ids): raise ValueError('unresolved support in scoring prefix')
