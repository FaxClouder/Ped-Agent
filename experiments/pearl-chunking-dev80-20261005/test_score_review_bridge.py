"""Regression: saved r07 judgments must reach the legacy E3 scoring entrypoints."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from test_e1_visible_review import span, mapping, review
from score import score_context
from evaluate import run


def context(spans):
    stage = {'units': [{'spans': spans}]}
    return dict(intent_id='q', context_id='c', panel_id='fixed_budget_main',
                strategy='P0', budget=4096, raw=stage, expanded=stage, final=stage)


def test_context_reuses_visible_alternative_and_outside_universe():
    assert score_context(context([span(10,30)]), mapping(review()))['sufficient']=='yes'
    assert score_context(context([span(15,25)]), mapping(review()))['sufficient']=='no'
    assert score_context(context([span(101,110)]), mapping(review()))['sufficient']=='unknown'


def test_context_reuses_r07_adjudicated_variant():
    rv=review(status='unknown',alts=(),unc=((10,30),))
    rv['uncertain'][0]['adjudicated_variants']=[dict(verdict='supports',source_spans=[span(10,20)])]
    assert score_context(context([span(10,20)]),mapping(rv))['sufficient']=='yes'


def test_evaluate_uses_same_review_for_ranking_and_context(tmp_path):
    m=mapping(review()); m['main_stratum']='single_source'
    mp=tmp_path/'map.json'; mp.write_text(json.dumps({'records':[m]}),encoding='utf8')
    (tmp_path/'contexts.jsonl').write_text(json.dumps(context([span(10,30)]))+'\n',encoding='utf8')
    child={'core_spans':[span(10,30)],'overlap_spans':[]}
    (tmp_path/'rankings.jsonl').write_text(json.dumps({'intent_id':'q','status':'success','results':{k:[child] for k in ('R1','R2','R3','R4')}})+'\n',encoding='utf8')
    result=run(tmp_path,mp)
    assert len(result['details'])==19
    assert {r['k'] for r in result['details'] if r['kind']=='layer1_raw'}=={1,5,10,20}
    assert all(r['sufficient']=='yes' for r in result['details'])
    assert result['source_reviewed_intents']==1
    assert result['source_review_pending_intents']==0


def test_explicit_failure_cannot_be_quality_success():
    assert score_context(context([span(0,60)]), mapping(review()), failure='assembly_failed')['sufficient']=='unknown'
