import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from e1_visible_review import requirement_basis, support_r06, prefix_metrics_r06, validate_review

def span(a,b,e='e'):
    return dict(doc_id='d',source_version='v',element_id=e,start=a,end=b)

def mapping(review=None):
    req={'requirement_id':'r','evidence_groups':[{'status':'yes','necessary_spans':[span(0,50)],'reviewer_id':'x','rationale':'Conservative certificate.'}]}
    if review is not None:req['visible_universe_review']=review
    return {'intent_id':'q','groups':[['r']],'requirements':[req]}

def review(status='yes',alts=((10,30),),unc=(),universe=((0,100),)):
    return dict(universe_status=status,alternatives=[dict(source_spans=[span(*a)]) for a in alts],uncertain=[dict(source_spans=[span(*u)]) for u in unc],universe_spans=[span(*u) for u in universe])

def test_certificate_yes_is_unchanged_and_no_review_stays_unknown():
    assert support_r06([span(0,60)],mapping(review()))[0]=={'r':'yes'}
    assert support_r06([span(0,20)],mapping())[0]=={'r':'unknown'}

def test_visible_minimal_alternative_resolves_yes():
    s,b,base=support_r06([span(5,35)],mapping(review()))
    assert s=={'r':'yes'} and b=={'r':'reviewed_visible_alternative'} and base=={'r':'unknown'}

def test_partial_alternative_inside_universe_is_no_but_outside_is_unknown():
    assert support_r06([span(15,40)],mapping(review()))[0]=={'r':'no'}
    assert support_r06([span(15,40),span(0,5,'other')],mapping(review()))[0]=={'r':'unknown'}

def test_uncertain_and_unresolved_universe_stay_unknown():
    assert support_r06([span(60,70)],mapping(review(unc=((65,90),))))[0]=={'r':'unknown'}
    assert support_r06([span(60,70)],mapping(review(status='unknown',alts=())))[0]=={'r':'unknown'}
    assert support_r06([span(60,70)],mapping(review(status='no',alts=())))[0]=={'r':'no'}

def test_cross_child_alternative_rank():
    m=mapping(review())
    ranked=[{'core_spans':[span(10,20)],'overlap_spans':[]},{'core_spans':[span(20,30)],'overlap_spans':[]}]
    r=prefix_metrics_r06(ranked,m,2)
    assert r['sufficient']=='yes' and r['complete_rr_lower']==.5 and r['complete_rr_upper']==.5
    assert prefix_metrics_r06(ranked,m,1)['sufficient']=='no'

def _packet():
    return {'intent_id':'q','packet_sha256':'p','segments':[{'segment_id':'S1','text':'hello world'}]}
def _entry():
    return {'requirement_ids':['r'],'universe_spans':[span(100,111)],'segment_bindings':[{'segment_id':'S1','span':span(100,111)}]}

def test_review_quotes_map_to_source_offsets():
    r={'intent_id':'q','packet_sha256':'p','reviewer_id':'blind','requirements':[{'requirement_id':'r','universe_status':'yes','exhaustive':True,'rationale':'ok','alternatives':[{'spans':[{'segment_id':'S1','start':6,'end':11,'quote':'world'}],'rationale':'states it'}],'uncertain':[]}]}
    out=validate_review(_packet(),_entry(),r)
    assert out['r']['alternatives'][0]['source_spans']==[span(106,111)]

@pytest.mark.parametrize('mutate',[
    lambda r:r['requirements'][0]['alternatives'][0]['spans'][0].update(quote='World'),
    lambda r:r['requirements'][0].update(exhaustive=False),
    lambda r:r['requirements'][0].update(universe_status='no'),
    lambda r:r.update(packet_sha256='drift'),
    lambda r:r.update(requirements=[]),
    lambda r:r['requirements'][0]['alternatives'][0]['spans'][0].update(end=12),
])
def test_invalid_reviews_rejected(mutate):
    r={'intent_id':'q','packet_sha256':'p','reviewer_id':'blind','requirements':[{'requirement_id':'r','universe_status':'yes','exhaustive':True,'rationale':'ok','alternatives':[{'spans':[{'segment_id':'S1','start':6,'end':11,'quote':'world'}],'rationale':'states it'}],'uncertain':[]}]}
    mutate(r)
    with pytest.raises(ValueError):validate_review(_packet(),_entry(),r)

def _adj_review(status='yes',verdicts=()):
    r=review(status=status,alts=((10,30),) if status=='yes' else (),unc=((60,90),))
    r['uncertain'][0]['adjudicated_variants']=[dict(source_spans=[span(*v[0])],verdict=v[1]) for v in verdicts]
    return r

def test_adjudicated_supports_variant_resolves_yes_only_when_visible():
    m=mapping(_adj_review(verdicts=(((60,80),'supports'),)))
    assert support_r06([span(55,85)],m)[:2]==({'r':'yes'},{'r':'adjudicated_visible_variant'})
    assert support_r06([span(65,85)],m)[0]=={'r':'unknown'}

def test_does_not_support_variant_unblocks_only_its_subportions():
    m=mapping(_adj_review(verdicts=(((60,75),'does_not_support'),)))
    assert support_r06([span(55,70)],m)[0]=={'r':'no'}
    assert support_r06([span(55,80)],m)[0]=={'r':'unknown'}
    m=mapping(_adj_review(verdicts=(((60,75),'uncertain'),)))
    assert support_r06([span(55,70)],m)[0]=={'r':'unknown'}

def test_unresolved_universe_becomes_decidable_only_after_full_adjudication():
    r=_adj_review(status='unknown',verdicts=(((60,90),'does_not_support'),))
    assert support_r06([span(55,95)],mapping(r))[0]=={'r':'no'}
    del r['uncertain'][0]['adjudicated_variants']
    assert support_r06([span(55,95)],mapping(r))[0]=={'r':'unknown'}
