import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from e1_score import prefix_metrics, candidate_decision, merge_reviews

def span(a,b):
    return dict(doc_id='d',source_version='v',element_id='e',start=a,end=b)

def mapping():
    return {'intent_id':'q','groups':[['r']], 'requirements':[{'requirement_id':'r','evidence_groups':[{'status':'yes','necessary_spans':[span(2,5)],'reviewer_id':'reviewer','rationale':'Full necessary fact and condition.'}]}]}

def test_cross_child_complete_mrr_and_unknown_bounds():
    ranked=[{'core_spans':[span(2,3)],'overlap_spans':[]},{'core_spans':[span(3,5)],'overlap_spans':[]}]
    result=prefix_metrics(ranked,mapping(),2)
    assert result['sufficient']=='yes'
    assert result['complete_rr_lower']==.5 and result['complete_rr_upper']==1
    assert prefix_metrics(ranked,mapping(),1)['sufficient']=='unknown'

def test_unknown_can_reverse_candidate_order():
    metrics=[{'configuration_id':'A','cgc4_lower':.9,'cgc4_upper':1.,'cegr10_lower':.9,'cegr10_upper':1.,'retrieval_mean_seconds':1},
             {'configuration_id':'B','cgc4_lower':.8,'cgc4_upper':1.,'cegr10_lower':.8,'cegr10_upper':1.,'retrieval_mean_seconds':2}]
    assert candidate_decision(metrics)['selected']==[]
    assert candidate_decision(metrics)['status']=='pending_unknown'
    for r in metrics:r['cgc4_upper']=r['cgc4_lower'];r['cegr10_upper']=r['cegr10_lower']
    assert candidate_decision(metrics)['selected']==['A','B']

def test_missing_or_invisible_review_never_upgrades():
    packet={'intent_id':'q','packet_sha256':'p','requirements':[{'requirement_id':'r','bundles':[{'bundle_index':0,'sources':[dict(doc_id='d',source_version='v',element_id='e',text='hello')]}]}]}
    review={'reviewer_id':'agent','judgments':[dict(intent_id='q',packet_sha256='p',requirement_id='r',bundle_index=0,status='yes',necessary_spans=[span(0,6)],rationale='Claim.')]}
    with pytest.raises(ValueError):merge_reviews([mapping()], [packet], [review])
    review['judgments']=[]
    with pytest.raises(ValueError):merge_reviews([mapping()], [packet], [review])
