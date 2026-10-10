"""Coverage gates for adding the R4 review to a shared support map."""

import importlib.util
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location('score_r4_pilot', Path(__file__).with_name('score_r4_pilot.py'))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_new_front20_candidates_must_all_be_blind_reviewed_once():
    required = {'q1': {'a', 'b'}}
    valid = [{'intent_id': 'q1', 'decisions': [
        {'chunk_ids': ['a'], 'supports': [], 'reason': 'No answer.'},
        {'chunk_ids': ['b'], 'supports': ['x'], 'reason': 'Full fact.'},
    ], 'atom_paths_additions': {'x': [['b']]}, 'unresolved': []}]
    MODULE.validate_new_reviews(required, valid)
    with pytest.raises(ValueError, match='coverage'):
        MODULE.validate_new_reviews(required, [dict(valid[0], decisions=valid[0]['decisions'][:1])])
    with pytest.raises(ValueError, match='unresolved'):
        MODULE.validate_new_reviews(required, [dict(valid[0], unresolved=['b'])])
