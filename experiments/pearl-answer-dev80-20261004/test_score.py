import copy
import importlib.util
from pathlib import Path

import pytest


def load(name):
    path = Path(__file__).with_name(name + '.py')
    assert path.exists(), f'{name} implementation missing'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference():
    return dict(intent_id='i1', stratum='numeric', resolved=True,
                key_targets=['t1'], required_conditions=['age'],
                allowed_claim_groups=[['c1', 'c2'], ['c3', 'c4']],
                integration_applicable=False, oracle_eligible=False,
                numeric_targets=[dict(id='speed', value=1.2, unit='m/s', dimension='speed', tolerance=0)])


def cell():
    return dict(intent_id='i1', arm='A0-4096', generation_status='returned', record_kind='synthetic',
                l2_sufficient='yes', decision=dict(targets={'t1': 'correct'},
                conditions={'age': 'correct'}, claims={'c1': 'correct', 'c2': 'missing',
                'c3': 'missing', 'c4': 'correct'}, contradiction=False, refusal=False,
                integration='no', numeric={'speed': {'status': 'parsed', 'value': 120, 'unit': 'cm/s'}}))


def bundle():
    refs = [reference()]
    cells = []
    for arm in ['A0-4096', 'A1-4096', 'A0-8192', 'A1-8192']:
        row = cell(); row['arm'] = arm; cells.append(row)
    return dict(schema_version='pearl-answer-score-input-v1', references=refs, cells=cells,
                expected_cells=[{'intent_id': c['intent_id'], 'arm': c['arm']} for c in cells])


def test_required_synthetic_semantics():
    s = load('score'); r = reference(); c = cell()
    out = s.score_cell(r, c)
    assert out['coverage_lower'] == out['coverage_upper'] == .5
    assert not out['complete_claim_group']
    assert out['ac'] == 1 and out['integration'] == 'na'
    assert out['numeric'][0]['absolute_error'] == 0
    c['decision']['claims'].update(c3='correct')
    assert s.score_cell(r, c)['complete_claim_group']
    c['decision']['contradiction'] = True
    assert s.score_cell(r, c)['ac'] == 0
    assert s.score_cell(r, c)['coverage_lower'] == 1
    c['decision']['contradiction'] = False
    c['decision']['conditions']['age'] = 'missing'
    assert s.score_cell(r, c)['ac'] == .5
    r['integration_applicable'] = True
    c['decision']['conditions']['age'] = 'correct'
    assert s.score_cell(r, c)['ac'] == .5
    assert s.score_cell(r, c)['integration'] == 'no'


def test_unknown_refusal_failure_and_zero_reference():
    s = load('score'); r = reference(); c = cell()
    c['decision']['claims']['c2'] = 'unknown'
    c['decision']['targets']['t1'] = 'unknown'
    out = s.score_cell(r, c)
    assert out['ac'] is None and out['strict'] == 'unknown'
    assert (out['coverage_lower'], out['coverage_upper']) == (.5, 1)
    c['decision']['refusal'] = True
    assert s.score_cell(r, c)['failure_kind'] == 'refusal'
    c['generation_status'] = 'generation_failed'; c.pop('decision')
    out = s.score_cell(r, c)
    assert out['ac'] == 0 and out['failure_kind'] == 'generation_failed'
    r['resolved'] = False
    assert s.score_cell(r, c)['ac'] is None
    r['resolved'] = True; r['numeric_targets'][0]['value'] = 0
    c = cell()
    assert s.score_cell(r, c)['numeric'][0]['relative_error'] is None
    c['decision']['numeric']['speed']['unit'] = 'people'
    assert s.score_cell(r, c)['numeric'][0]['status'] == 'wrong_unit'


def test_whole_bundle_stats_and_pairing():
    s = load('score'); b = bundle()
    out = s.score_bundle(b)
    assert out['bootstrap']['iterations'] == 10000
    assert out['bootstrap']['seed'] == 20261004
    assert len(out['comparisons']) == 5
    assert all(p['holm_p'] == 1 for p in out['comparisons'])
    assert out['comparisons'][-1]['testable'] is False
    assert out['arms']['A0-4096']['N'] == 1
    assert out['arms']['A0-4096']['four_state']['n11'] == 1
    assert out['comparisons'][0]['ac_delta_ci'] == [0, 0]
    b['cells'][1]['decision']['targets']['t1'] = 'unknown'
    out = s.score_bundle(b)
    p = out['comparisons'][0]
    assert p['unknown_pairs'] == 1 and p['strict_delta_bounds'] == [-1, 0]
    assert s.exact_mcnemar(4, 0) == .125
    assert s.holm([.01, .02, .3, .8, 1]) == pytest.approx([.05, .08, .9, 1, 1])
    assert p['ac_delta_ci_bounds'] == [[-1, -1], [0, 0]]


def test_numeric_dimensions_and_technical_four_state():
    s = load('score'); b = bundle()
    b['cells'][0]['generation_status'] = 'generation_failed'
    b['references'][0]['numeric_targets'].append(dict(id='count', value=50, unit='people', dimension='count', tolerance=0))
    for c in b['cells']:
        c['decision']['numeric']['count'] = {'status':'parsed', 'value':55, 'unit':'people'}
    out = s.score_bundle(b)
    summary = out['arms']['A0-4096']
    assert summary['four_state']['sufficient_technical_failures'] == 1
    assert summary['four_state']['sufficient_semantic_failures'] == 0
    assert out['arms']['A1-4096']['numeric']['count:people']['MAE'] == 5
    assert out['arms']['A1-4096']['numeric']['speed:m/s']['MAE'] == 0


def test_both_arm_unknown_bootstrap_difference_bounds():
    s = load('score'); b = bundle()
    for c in b['cells']: c['decision']['targets']['t1'] = 'unknown'
    assert s.score_bundle(b)['comparisons'][0]['ac_delta_ci_bounds'] == [[-1, -1], [1, 1]]


def test_reported_age_is_not_tolerance():
    s = load('score')
    target = {'id':'mean_age','value':66.8,'unit':'years','dimension':'age','tolerance':0}
    assert s.numeric_error(target, {'status':'parsed','value':66.8,'unit':'years'})['absolute_error'] == 0
    assert s.numeric_error(target, {'status':'parsed','value':65,'unit':'years'})['within_tolerance'] is False


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'mock'])
def test_cell_integrity(change):
    s = load('score'); b = bundle()
    if change == 'missing': b['cells'].pop()
    if change == 'duplicate': b['cells'].append(copy.deepcopy(b['cells'][0]))
    if change == 'mock': b['cells'][0]['record_kind'] = 'mock'
    with pytest.raises(ValueError): s.score_bundle(b, require_real=True)


def test_unknown_bad_label_rejected():
    s = load('score'); b = bundle()
    b['cells'][0]['decision']['targets']['t1'] = 'unread'
    with pytest.raises(ValueError): s.score_bundle(b)

def test_exact_reviewed_numeric_alternatives_are_not_continuous_tolerance():
    s=load('score'); v=load('verify'); b=bundle()
    target=b['references'][0]['numeric_targets'][0]
    target.update(value=6,allowed_values=[6,6.25],tolerance=0,tolerance_basis='Reported nominal 6 or direct 1/0.16 derivation')
    for c in b['cells']: c['decision']['numeric']['speed'].update(value=6.25,unit='m/s')
    result=s.score_bundle(b)
    assert result['rows'][0]['numeric'][0]['within_tolerance'] is True
    assert result['rows'][0]['numeric'][0]['absolute_error']==.25
    assert v.recompute(b)==result
    for c in b['cells']: c['decision']['numeric']['speed']['value']=6.15
    result=s.score_bundle(b)
    assert result['rows'][0]['numeric'][0]['within_tolerance'] is False
    assert v.recompute(b)==result

@pytest.mark.parametrize('dimension,target_unit,answer_value,answer_unit,target_value',[
    ('density','people/m2',2,'ped/m2',2),
    ('density','people/m2',2,'pedestrians/m²',2),
    ('density','people/m2',2,'persons/m²',2),
    ('linear_density','people/m',3,'ped/m',3),
    ('linear_density','people/m',3,'pedestrians/m',3),
    ('flow','people/s',120,'ped/min',2),
    ('flow','people/s',2,'ped/s',2),
    ('area_per_pedestrian','m2/person',12000,'cm²/ped',1.2),
    ('area_per_pedestrian','m2/person',1.2,'m2/ped',1.2),
    ('angle','degrees',45,'degree',45),
    ('count','people',2,'pedestrians',2),
    ('percentage','%',.2,'proportion',20),
    ('dimensionless','dimensionless',2,'integer',2),
    ('proportion','%',.2,'fraction',20),
    ('relative_time_improvement','%',20,'%',20),
    ('integer','dimensionless',2,'integer',2),
    ('count_per_width','ped/m',3,'people/m',3),
])
def test_reference_numeric_unit_alias_conversions(dimension,target_unit,answer_value,answer_unit,target_value):
    s=load('score'); v=load('verify'); b=bundle()
    target=b['references'][0]['numeric_targets'][0]
    target.update(value=target_value,unit=target_unit,dimension=dimension,tolerance=0)
    for c in b['cells']: c['decision']['numeric']['speed'].update(value=answer_value,unit=answer_unit)
    result=s.score_bundle(b)
    assert all(r['numeric'][0]['absolute_error']==0 and r['numeric'][0]['within_tolerance'] is True for r in result['rows'])
    assert v.recompute(b)==result
