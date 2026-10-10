from e3_scope_revision import active_requirement, support_revision, independent_status
from e1_visible_review_verify import intervals

S=dict(doc_id='d',source_version='v',element_id='e',start=0,end=10)

def fixture():
    return dict(requirement_id='r',evidence_groups=[dict(status='yes',necessary_spans=[S],reviewer_id='old',rationale='old')],visible_universe_review=dict(universe_status='unknown',universe_spans=[],alternatives=[dict(source_spans=[S])],uncertain=[],scope_revision=dict(excluded_certificate_indices=[0],excluded_alternative_indices=[0],negative_scopes=[])))

def test_invalid_positive_is_unknown_without_reviewed_negative_scope():
    q=fixture();m=dict(requirements=[q]);s,_,_=support_revision([S],m)
    assert s=={'r':'unknown'} and independent_status(q,[S],intervals([S]))=='unknown'
    assert q['evidence_groups'][0]['status']=='yes' and len(q['visible_universe_review']['alternatives'])==1

def test_exhaustive_actual_negative_scope_is_no():
    q=fixture();q['visible_universe_review']['scope_revision']['negative_scopes']=[[S]]
    assert support_revision([S],dict(requirements=[q]))[0]=={'r':'no'}
    assert independent_status(q,[S],intervals([S]))=='no'
    outside=dict(S,end=11)
    assert independent_status(q,[outside],intervals([outside]))=='unknown'

def test_valid_certificate_remains_yes():
    q=fixture();q['visible_universe_review']['scope_revision']['excluded_certificate_indices']=[]
    q['visible_universe_review']['scope_revision']['negative_scopes']=[[S]]
    assert support_revision([S],dict(requirements=[q]))[0]=={'r':'yes'}
    assert independent_status(q,[S],intervals([S]))=='yes'
