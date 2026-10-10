import copy
import pytest
import e3_integrate_reviews as i
from runtime import save_json,save_rows,sha

def fixture(tmp_path,monkeypatch,status='yes',exhaustive=False):
    monkeypatch.setattr(i,'ROOT',tmp_path)
    review=tmp_path/'base';review.mkdir();monkeypatch.setattr(i,'REVIEW',review)
    span=lambda a,b:dict(doc_id='d',source_version='v',element_id='e',start=a,end=b)
    q=dict(requirement_id='r1',description='all conditions',evidence_groups=[],visible_universe_review=dict(universe_spans=[span(0,10)],universe_status='no',alternatives=[],uncertain=[]))
    base=dict(records=[dict(intent_id='x',requirements=[q],groups=[['r1']])]);save_json(review/'common-support-map-e1-r07.json',base)
    out=tmp_path/'out';out.mkdir();pack=out/'review-packets-e3-r08';pack.mkdir();res=out/'review-results-e3-r08';res.mkdir()
    packet=pack/'x.json';save_json(packet,dict(requirements=[dict(requirement_id='r1')],segments=[dict(source_span=span(0,30))]))
    context=dict(context_id='c',intent_id='x',configuration_id='test',strategy='P1',budget=4096,panel_id='main',final=dict(text_sha256='t',units=[dict(spans=[span(0,30)])]))
    save_rows(out/'contexts-test.jsonl',[context])
    ref={k:context[k] for k in ('context_id','configuration_id','strategy','budget','panel_id')};ref['text_sha256']='t'
    save_json(pack/'x-binding.json',dict(packet_sha256=sha(packet),mapping_sha256=sha(review/'common-support-map-e1-r07.json'),visible_spans=[span(0,30)],contexts=[ref]))
    verdict=dict(requirement_id='r1',status=status,alternatives=[dict(source_spans=[span(20,25)],rationale='complete all conditions')],rationale='read supplied scope',coverage_complete=True,alternatives_exhaustive=exhaustive)
    result=dict(intent_id='x',human_verified=False,reviewer_id='test',requirements=[verdict])
    return out,res,result,base

def test_nonexhaustive_positive_does_not_expand_negative_scope(tmp_path,monkeypatch):
    out,res,result,base=fixture(tmp_path,monkeypatch);save_json(res/'x.json',result);i.run(out,'r08')
    new=i.load(out/'common-support-map-e3-r08.json')['records'][0]
    old=base['records'][0]
    assert new['groups']==old['groups'] and new['requirements'][0]['evidence_groups']==old['requirements'][0]['evidence_groups']
    assert new['requirements'][0]['visible_universe_review']['universe_spans']==old['requirements'][0]['visible_universe_review']['universe_spans']
    assert new['requirements'][0]['visible_universe_review']['alternatives'][0]['source_spans'][0]['start']==20

def test_negative_cannot_add_positive_alternative(tmp_path,monkeypatch):
    out,res,result,_=fixture(tmp_path,monkeypatch,status='no',exhaustive=True);save_json(res/'x.json',result)
    with pytest.raises(AssertionError):i.run(out,'r08')

def test_duplicate_verdicts_are_rejected(tmp_path,monkeypatch):
    out,res,result,_=fixture(tmp_path,monkeypatch);result['requirements']*=2;save_json(res/'x.json',result)
    with pytest.raises(AssertionError):i.run(out,'r08')

def test_unreviewed_negative_scope_is_rejected(tmp_path,monkeypatch):
    out,res,result,_=fixture(tmp_path,monkeypatch,status='no',exhaustive=True)
    result['requirements'][0]['alternatives']=[];save_json(res/'x.json',result)
    p=out/'review-packets-e3-r08'/'x-binding.json';value=i.load(p);value['visible_spans'][0]['end']=40
    p.write_text(__import__('json').dumps(value),encoding='utf8')
    with pytest.raises(AssertionError):i.run(out,'r08')

def test_conflicting_unknown_no_does_not_expand_negative_scope(tmp_path,monkeypatch):
    out,res,result,base=fixture(tmp_path,monkeypatch,status='unknown',exhaustive=False)
    result['requirements'][0]['alternatives']=[];save_json(res/'x.json',result)
    other=copy.deepcopy(result);other['requirements'][0].update(status='no',alternatives_exhaustive=True)
    save_json(res/'x-second.json',other);i.run(out,'r08')
    review=i.load(out/'common-support-map-e3-r08.json')['records'][0]['requirements'][0]['visible_universe_review']
    assert review['universe_spans']==base['records'][0]['requirements'][0]['visible_universe_review']['universe_spans']
    assert all(x['status']=='unknown' for x in review['review_extensions'])
