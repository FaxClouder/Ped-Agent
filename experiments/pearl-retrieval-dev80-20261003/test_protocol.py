import importlib.util
from pathlib import Path
import pytest

HERE = Path(__file__).parent

def load():
    spec = importlib.util.spec_from_file_location('dev80_protocol', HERE / 'protocol.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def gold():
    return {'atoms': [{'atom_id': x} for x in 'ABCD'],
            'requirements': [{'requirement_id': x, 'support_bundles': [[x]]} for x in 'ABCD'],
            'evidence_groups': [{'group_id': 'g1', 'requirements': ['A', 'B']},
                                {'group_id': 'g2', 'requirements': ['C', 'D']}]}

def test_protocol_fixed_and_or_and_original_ranks():
    m = load()
    paths = {a: [[a]] for a in 'ABCD'}
    for ranks, k, expected in [(['A','D'],2,(0,.5,0)),(['A','x','B'],2,(0,.5,0)),
            (['A','x','B'],3,(1,1,1/3)),(['C','D'],2,(1,1,.5)),
            (['A','A','B'],2,(0,.5,0)),(['A','A','B'],3,(1,1,1/3)),(['x'],10,(0,0,0)),([],10,(0,0,0))]:
        s = m.score_prefix(gold(), paths, ranks, k)
        assert tuple(s[x] for x in ('CEGR','BestGroupCov','CompleteRR')) == expected

def test_joint_atom_bundle_and_conditions():
    m = load()
    g = {'atoms':[{'atom_id':a} for a in ['u','v','w']],
         'requirements':[{'requirement_id':'F','support_bundles':[['u','v'],['w']]}],
         'evidence_groups':[{'group_id':'g','requirements':['F']}]}
    p = {'u':[['number']], 'v':[['condition']], 'w':[['left','right'],['complete']]}
    for ranks, expected in [(['number'],0),(['number','wrong-experiment'],0),
                             (['number','condition'],1),(['left'],0),(['left','right'],1),(['complete'],1)]:
        assert m.score_prefix(g,p,ranks,20)['CEGR'] == expected

def test_empty_gold_and_bundle_rejected():
    m = load()
    g = gold()
    for field in ['atoms','requirements','evidence_groups']:
        invalid = dict(g, **{field:[]})
        with pytest.raises(ValueError): m.validate_gold(invalid)
    g['requirements'][0]['support_bundles'] = [[]]
    with pytest.raises(ValueError): m.validate_gold(g)

def test_unresolved_scoring_prefix_rejected_and_deep_allowed():
    m = load()
    with pytest.raises(ValueError, match='unresolved'):
        m.require_reviewed(['a','b'], {'a'}, 20)
    m.require_reviewed(['a']*20+['unknown'], {'a'}, 20)

def test_partial_requirement_denominator_not_atoms():
    m = load()
    g=gold();g['evidence_groups']=[{'group_id':'g','requirements':['A','B','C']}]
    assert m.score_prefix(g,{a:[[a]] for a in 'ABCD'},['A','B'],2)['BestGroupCov']==2/3
