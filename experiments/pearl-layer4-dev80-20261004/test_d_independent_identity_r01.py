import json
import pytest
import verify_d400_r01 as verify

def test_independent_rejects_wrong_response_even_with_self_consistent_blind(tmp_path):
    p=tmp_path/'packet.json';p.write_text(json.dumps({'response_sha256':'wrong','raw_answer':'other','context':'actual'}))
    decision={'blind_id':'grounding-0001','provenance':{'packet_path':str(p)}}
    with pytest.raises(ValueError,match='cell input'):
        verify.validate_chain_cell(decision,{'response_sha256':'right','raw_answer':'answer','context':'actual'},'grounding-0001')

def test_independent_rejects_wrong_blind():
    with pytest.raises(ValueError,match='blind identity'):
        verify.validate_chain_cell({'blind_id':'grounding-0002'},{},'grounding-0001')

def test_independent_reuse_requires_all_frozen_C100():
    with pytest.raises(ValueError,match='C100 reuse'):
        verify.validate_reuse_coverage({'reuse':[]},{'C100_cell_ids':['c'+str(i) for i in range(100)]})

def test_empty_packet_cannot_pass_by_omitting_input_fields(tmp_path):
    from assemble_c100_r01 import sha
    p=tmp_path/'empty';p.write_text('{}')
    with pytest.raises(ValueError,match='required packet fields'):
        verify.validate_chain_cell({'blind_id':'grounding-0001','provenance':{'packet_path':str(p),'packet_sha256':sha(p)}},{},'grounding-0001')

def test_full_answer_cannot_have_a_refusal_reason():
    with pytest.raises(ValueError,match='full answer reason'):
        verify.validate_decision_vocabulary([{'behavior':'full_answer','abstain':False,'unsupported_completion':False,'reason':'correct'}])

def test_bounded_answer_requires_actual_reason_judgment():
    with pytest.raises(ValueError,match='refusal reason'):
        verify.validate_decision_vocabulary([{'behavior':'bounded_partial','abstain':True,'unsupported_completion':False,'reason':'na'}])


def test_independent_rejects_bounded_answer_with_partial_claim():
    row={'behavior':'bounded_partial','reason':'correct','abstain':True,'unsupported_completion':False,'claims':[{'grounding':{'label':'partial'}}]}
    with pytest.raises(ValueError,match='bounded answer claim support'):
        verify.validate_decision_vocabulary([row])
