import copy
import importlib.util
from pathlib import Path
import pytest


def module():
    p=Path(__file__).with_name('validate_references.py')
    assert p.exists(), 'reference structural validator missing'
    s=importlib.util.spec_from_file_location('ref_validator',p)
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def fixture(m):
    text='α experimental speed 1.2 m/s under condition X.'
    source={'source_id':'s','chunk_id':'p','text':text,'text_sha256':m.sha_text(text),'source_sha256':'pdfhash','title':'Title','locator':'p.1','source_library_path':'parents.jsonl','source_library_sha256':'libhash'}
    packet={'intent_id':'i','query':'Q','stratum':'numeric','sources':[source],'atoms':[{'source_id':'s'}]}
    segment={'source_id':'s','chunk_id':'p','text_start_byte':0,'text_end_byte':len(text.encode()),'exact_text':text,'text_sha256':m.sha_text(text)}
    c={'intent_id':'i','stratum':'numeric','resolved':True,'reference_answer':'1.2 m/s under X','key_targets':['t'],'target_definitions':{'t':'Speed is 1.2 m/s'},'required_conditions':['x'],'condition_definitions':{'x':'condition X'},'allowed_claim_groups':[['c']],'claim_definitions':{'c':'Speed is 1.2 m/s under X'},'integration_applicable':False,'integration_rule':None,'numeric_targets':[{'id':'n','value':1.2,'unit':'m/s','dimension':'speed','tolerance':0,'tolerance_basis':'reported literal value'}],'citations':[{'source_id':'s','chunk_id':'p','text_sha256':source['text_sha256'],'quote':'1.2 m/s'}],'oracle':{'segments':[segment],'serialized_context':'[Source s | p.1]\nTitle: Title\n'+text,'token_count':12,'budget':8192,'construction_status':'candidate'},'provenance':{'agent_id':'builder','role':'builder','fork_turns':'none'}}
    return c,packet


def test_exact_citation_and_utf8_oracle_validate():
    m=module(); c,p=fixture(m)
    assert m.validate_candidate(c,p,lambda s:12)['oracle_structurally_valid']
    for field in ['quote','text_sha256']:
        altered=copy.deepcopy(c); altered['citations'][0][field]='invented'
        with pytest.raises(ValueError): m.validate_candidate(altered,p,lambda s:12)


def test_oracle_wrong_byte_boundary_context_and_budget_rejected():
    m=module(); c,p=fixture(m)
    variations=[]
    b=copy.deepcopy(c); b['oracle']['segments'][0]['text_start_byte']=1; variations.append(b)
    b=copy.deepcopy(c); b['oracle']['serialized_context']+='fabricated'; variations.append(b)
    b=copy.deepcopy(c); b['oracle']['token_count']=8193; variations.append(b)
    for b in variations:
        with pytest.raises(ValueError): m.validate_candidate(b,p,lambda s:b['oracle']['token_count'])


def test_dangling_groups_and_invalid_numeric_tolerance_rejected():
    m=module(); c,p=fixture(m)
    for tolerance in [-1,float('nan'),float('inf')]:
        b=copy.deepcopy(c); b['numeric_targets'][0]['tolerance']=tolerance
        with pytest.raises(ValueError): m.validate_candidate(b,p,lambda s:12)
    b=copy.deepcopy(c); b['numeric_targets'][0].pop('tolerance_basis')
    with pytest.raises(ValueError): m.validate_candidate(b,p,lambda s:12)
    b=copy.deepcopy(c); b['allowed_claim_groups']=[['missing']]
    with pytest.raises(ValueError): m.validate_candidate(b,p,lambda s:12)


def test_reviewer_must_independently_read_exact_candidate_and_oracle():
    m=module(); c,p=fixture(m)
    review={'intent_id':'i','candidate_sha256':'candidatehash','reference_verdict':'yes','oracle_verdict':'yes','actual_read':True,'actual_read_oracle':True,'rationale':'Read exact source and checked conclusion','citation_checks':'Quotes exact and support target','numeric_review':'1.2 m/s is reported literal, tolerance zero','provenance':{'agent_id':'reviewer','role':'reviewer','fork_turns':'none','independent':True}}
    assert m.validate_review(review,c,'candidatehash')['oracle_eligible']
    for field,value in [('candidate_sha256','changed'),('actual_read',False),('actual_read_oracle',False)]:
        b=copy.deepcopy(review); b[field]=value
        with pytest.raises(ValueError): m.validate_review(b,c,'candidatehash')
    b=copy.deepcopy(review); b['provenance']['agent_id']='builder'
    with pytest.raises(ValueError): m.validate_review(b,c,'candidatehash')
    revised=copy.deepcopy(c); revised['semantic_revision']={'reviewer':'reviewer','original_candidate_sha256':'oldhash','reason':'wording repair'}
    with pytest.raises(ValueError): m.validate_review(review,revised,'candidatehash')


def test_freeze_missing_expected_reference_or_duplicate_fails():
    m=module()
    with pytest.raises(ValueError): m.validate_identity_set(['i'],['i','j'])
    with pytest.raises(ValueError): m.validate_identity_set(['i','i'],['i'])


def test_numeric_revision_requires_reviewer_distinct_from_numeric_author():
    m=module(); c,p=fixture(m)
    c['review_revision_provenance']={'agent_id':'numeric_author','source_actual_read':True,'basis':'Source nominal and exact reciprocal'}
    review={'intent_id':'i','candidate_sha256':'candidatehash','reference_verdict':'yes','oracle_verdict':'yes','actual_read':True,'actual_read_oracle':True,'rationale':'Reviewed the independently authored numeric revision','citation_checks':'Source exact','numeric_review':'Discrete nominal alternatives checked','base_original_candidate_sha256':'oldhash','original_review_sha256':'oldreview','provenance':{'agent_id':'builder','role':'reviewer','fork_turns':'none','independent':True}}
    assert m.validate_review(review,c,'candidatehash')['resolved']
    review['provenance']['agent_id']='numeric_author'
    with pytest.raises(ValueError): m.validate_review(review,c,'candidatehash')
