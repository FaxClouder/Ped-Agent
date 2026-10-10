import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from e1_verify import verify_ranking, verify_totals, verify_final_prefix,verify_candidate_order
from assemble import unit,views_by_id,prefix_unit,serialize

def test_self_consistent_shorter_or_reordered_final_is_rejected():
    class Count:
        def count(self,text):return len(text)
    views=views_by_id([dict(doc_id='d',source_version='v',elements=[dict(element_id='e',text='abcdefg')])])
    u=unit([dict(doc_id='d',source_version='v',element_id='e',start=0,end=7)],views,'c',1)
    correct=prefix_unit(u,5,views);budget=len(serialize([correct]))
    assert verify_final_prefix([u],[correct],views,budget,Count())
    with pytest.raises(ValueError,match='maximal'):
        verify_final_prefix([u],[prefix_unit(u,3,views)],views,budget,Count())
    other=dict(u,seed_chunk_id='other',rank=2)
    with pytest.raises(ValueError,match='order'):
        verify_final_prefix([u,other],[other,u],views,10000,Count())

def test_unknown_can_prevent_freezing_even_when_lower_rate_is_largest():
    a=dict(configuration_id='A',cgc4_lower=.8,cgc4_upper=1.,cegr10_lower=.7,cegr10_upper=1.,retrieval_mean_seconds=1.)
    b=dict(configuration_id='B',cgc4_lower=.7,cgc4_upper=1.,cegr10_lower=.6,cegr10_upper=1.,retrieval_mean_seconds=2.)
    decision=dict(nonduplicate_metrics=[a,b],selected=[],status='pending_unknown',provisional_lower_bound_order=['A','B'])
    assert verify_candidate_order(decision)
    decision['selected']=['A']
    with pytest.raises(ValueError,match='candidate'):
        verify_candidate_order(decision)

def test_aggregate_tamper_and_fixed_denominator():
    details=[dict(cell='x',sufficient='yes',failure=None,coverage_lower=1.,coverage_upper=1.),dict(cell='x',sufficient='unknown',failure=None,coverage_lower=0.,coverage_upper=1.)]
    summary=dict(cell='x',n=2,yes=1,no=0,unknown=1,failure_n=0,complete_group_lower=.5,complete_group_upper=1.,coverage_lower_mean=.5,coverage_upper_mean=1.)
    assert verify_totals(details,[summary])
    summary['n']=1
    with pytest.raises(ValueError):verify_totals(details,[summary])

def test_changed_ranked_source_never_passes_library_check():
    child={'chunk_id':'c','text':'fact','core_spans':[],'overlap_spans':[]}
    rank={'results':{m:[dict(child,score=1.)] for m in ('R1','R2','R3','R4')},'rrf_union':[]}
    rank['results']['R4'][0]['text']='invented'
    with pytest.raises(ValueError,match='library'):verify_ranking(rank,{'c':child})
