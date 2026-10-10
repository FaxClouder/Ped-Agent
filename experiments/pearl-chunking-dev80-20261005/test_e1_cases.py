import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from e1_cases import certificate_gaps, validate_detail_bindings
from runtime import cache_identity

def test_missing_condition_is_an_audit_gap_and_never_a_false_judgment():
    need=dict(doc_id='d',source_version='v',element_id='e',start=0,end=12)
    mapping={'requirements':[{'requirement_id':'r','description':'fact plus condition','evidence_groups':[{'status':'yes','necessary_spans':[need],'reviewer_id':'reviewer','rationale':'complete fact and condition'}]}]}
    result=certificate_gaps(mapping,[dict(need,end=8)])
    assert result[0]['alternatives'][0]['missing_spans']==[dict(need,start=8)]
    assert result[0]['semantic_status']=='unknown'
    assert certificate_gaps(mapping,[need])==[]


def test_reviewed_no_is_preserved_and_never_relabelled_unknown():
    contradicted=dict(doc_id='d',source_version='v',element_id='e',start=0,end=1)
    missing=dict(doc_id='d',source_version='v',element_id='e',start=2,end=3)
    mapping={'requirements':[
        {'requirement_id':'r_no','description':'reviewed contradiction','evidence_groups':[{'status':'no','necessary_spans':[contradicted],'reviewer_id':'reviewer','rationale':'source contradicts requirement'}]},
        {'requirement_id':'r_missing','description':'missing positive support','evidence_groups':[{'status':'yes','necessary_spans':[missing],'reviewer_id':'reviewer','rationale':'source supports requirement'}]},
    ]}

    result=certificate_gaps(mapping,[contradicted],expected_support={'r_no':'no','r_missing':'unknown'})

    assert [r['requirement_id'] for r in result]==['r_missing']
    assert result[0]['semantic_status']=='unknown'


def test_detail_bindings_require_actual_ranking_and_context_identity():
    ranking={'intent_id':'q','status':'success'}
    context={'intent_id':'q','budget':4096,'context_id':'ctx','final':{'units':[]}}
    details=[
        {'kind':'layer1_raw','intent_id':'q','ranking_sha256':cache_identity(ranking)},
        {'kind':'context','intent_id':'q','budget':4096,'context_id':'ctx','context_sha256':cache_identity(context)},
    ]

    assert validate_detail_bindings(details,{'q':ranking},{('q',4096):context})

    details[1]['context_sha256']='drift'
    with pytest.raises(ValueError,match='detail/context'):
        validate_detail_bindings(details,{'q':ranking},{('q',4096):context})
