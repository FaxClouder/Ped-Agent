import importlib.util
from pathlib import Path


def test_source_assignment_is_disjoint_and_contains_original_pilot_sources():
    path = Path(__file__).with_name('prepare_authoring.py')
    spec = importlib.util.spec_from_file_location('prepare_authoring', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [{'source_id': f's{i:03}'} for i in range(106)]
    pilot = {rows[i]['source_id'] for i in module.PILOT_SOURCE_INDICES}
    assignment = module.assign_sources(rows, pilot)
    sets = [{r['source_id'] for r in assignment[key]} for key in ('dev', 'eval_a', 'eval_b')]
    assert [len(s) for s in sets] == [32, 37, 37]
    assert pilot <= sets[0]
    assert sets[0].isdisjoint(sets[1]) and sets[0].isdisjoint(sets[2]) and sets[1].isdisjoint(sets[2])
    assert set.union(*sets) == {r['source_id'] for r in rows}
    assert assignment == module.assign_sources(rows, pilot)
