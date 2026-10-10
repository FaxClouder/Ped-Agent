"""E1 counterexamples: source loss, stale calibration, cross-config reuse."""
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from e1 import configurations, conservation, verify_frozen, verify_input_copies, assert_bindings, record_stage

def test_grid_has_separate_baseline():
    grid=configurations()
    assert len(grid)==13 and len(set(grid))==13
    assert grid['B0-regex320-overlap48-M0']==('B0',320)
    assert grid['C4-L512-O0-M0']==('C4',512)

def test_conservation_detects_gap_overlap_and_records_baseline_gap():
    view={'doc_id':'d','source_version':'v','elements':[{'element_id':'e','text':'abcde'}],'barrier_runs':[['e']]}
    def row(a,b):return {'core_spans':[dict(doc_id='d',source_version='v',element_id='e',start=a,end=b)],'overlap_spans':[]}
    assert conservation([view],[row(0,5)],False)['status']=='passed'
    with pytest.raises(ValueError):conservation([view],[row(0,2),row(3,5)],False)
    with pytest.raises(ValueError):conservation([view],[row(0,3),row(2,5)],False)
    assert conservation([view],[row(1,5)],True)['missing_characters']==1

def test_frozen_missing_or_changed_file_blocks(tmp_path):
    p=tmp_path/'a';p.write_text('x')
    from runtime import sha
    manifest=tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'artifacts_sha256':{'a':sha(p)}}))
    assert verify_frozen(manifest,tmp_path)['status']=='passed'
    p.write_text('y')
    with pytest.raises(ValueError):verify_frozen(manifest,tmp_path)

def test_query_and_index_binding_blocks_cross_configuration():
    bindings={'configuration_id':'C1','index_sha256':'a','query_sha256':'q'}
    assert_bindings(dict(bindings),bindings)
    with pytest.raises(ValueError):assert_bindings(dict(bindings,configuration_id='C2'),bindings)


def test_copied_runtime_inputs_must_match_both_copy_receipt_and_e0(tmp_path):
    from runtime import sha
    e0=tmp_path/'e0';out=tmp_path/'e1';e0.mkdir();out.mkdir()
    names=('source-views-prepared.json','table-snapshot.json','public-parent-graph.json',
           'calibration-r02/semantic-threshold.json','queries.jsonl')
    for name in names:
        original=e0/name;copied=out/name
        original.parent.mkdir(exist_ok=True);copied.parent.mkdir(exist_ok=True)
        original.write_text(name,encoding='utf8');copied.write_bytes(original.read_bytes())
    (e0/'delivery-manifest.json').write_text('{}',encoding='utf8')
    receipt={'E0_sha256':sha(e0/'delivery-manifest.json'),
             'copied_sha256':{name:sha(out/name) for name in names}}
    (out/'input-copy-manifest.json').write_text(json.dumps(receipt),encoding='utf8')
    assert verify_input_copies(e0,out)['status']=='passed'
    (out/'table-snapshot.json').write_text('changed',encoding='utf8')
    with pytest.raises(ValueError,match='copy'):verify_input_copies(e0,out)


def test_stage_ledger_appends_terminal_failure_without_erasing_prior_events(tmp_path):
    p=tmp_path/'config-ledger.jsonl'
    record_stage(p,'C1-L256-O0-M0','build','running')
    record_stage(p,'C1-L256-O0-M0','build','failed',error='synthetic failure')
    events=[json.loads(line) for line in p.read_text('utf8').splitlines()]
    assert [e['status'] for e in events]==['running','failed']
    assert events[-1]['error']=='synthetic failure'
