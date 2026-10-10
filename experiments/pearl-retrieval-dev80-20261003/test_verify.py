import importlib.util
from pathlib import Path
import pytest

def verifier():
    path=Path(__file__).with_name('verify.py')
    assert path.exists(), 'independent frozen-input verification implementation absent'
    spec=importlib.util.spec_from_file_location('independent_verify',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_independent_oracle_group_and_joint_atom():
    m=verifier()
    q={'requirements':[{'requirement_id':'F','support_bundles':[['a','b'],['w']]},
                       {'requirement_id':'G','support_bundles':[['g']]}],
       'evidence_groups':[{'requirements':['F','G']}]}
    paths={'a':[['a-left','a-right']],'b':[['condition']],'w':[['equivalent']],'g':[['other']]}
    result=m.oracle(q,paths,['a-left','a-right','condition','noise','other'],5)
    assert result == {'CEGR':1,'BestGroupCov':1,'CompleteRR':.2,'first_complete_rank':5}
    assert m.oracle(q,paths,['a-left','other'],5)['BestGroupCov']==.5
    assert m.oracle(q,paths,['equivalent','other'],2)['CompleteRR']==.5

def test_independent_oracle_no_cross_group_union_or_rank_compression():
    m=verifier()
    q={'requirements':[{'requirement_id':a,'support_bundles':[[a]]} for a in 'ABCD'],
       'evidence_groups':[{'requirements':['A','B']},{'requirements':['C','D']}]}
    paths={a:[[a]] for a in 'ABCD'}
    assert m.oracle(q,paths,['A','D'],2)['CEGR']==0
    assert m.oracle(q,paths,['A','A','B'],3)['CompleteRR']==pytest.approx(1/3)

def test_repeated_rankings_reject_score_change_and_missing_cell(tmp_path):
    import json
    m=verifier()
    first=[{'intent_id':'q','method':'R1','status':'success','query':'query',
            'results':[{'chunk_id':'c','score':1.0}]}]
    for p in (1,2,3):
        folder=tmp_path/f'pass-{p}';folder.mkdir()
        (folder/'query_vectors.npy').write_bytes(b'fixed-vector-bytes')
        (folder/'query_vector_ids.json').write_text('["q"]')
    for p in (2,3):
        (tmp_path/f'pass-{p}/rankings.jsonl').write_text(json.dumps(first[0])+'\n')
    assert m.verify_repeated_outputs(tmp_path,first)['ranking_scores_exact']
    changed=json.loads(json.dumps(first[0]));changed['results'][0]['score']=1.1
    (tmp_path/'pass-2/rankings.jsonl').write_text(json.dumps(changed)+'\n')
    with pytest.raises(ValueError,match='repeated ranking'):m.verify_repeated_outputs(tmp_path,first)
    (tmp_path/'pass-2/rankings.jsonl').write_text('')
    with pytest.raises(ValueError,match='repeated ranking'):m.verify_repeated_outputs(tmp_path,first)

def test_independent_review_binding_rejects_map_edits_and_empty_sources(tmp_path):
    import json
    m=verifier();p=tmp_path/'review.json'
    d={'intent_id':'q','review_type':'subagent_blind_content','atom_paths':{'a':[['c']]}}
    p.write_text(json.dumps(d),encoding='utf8')
    mapping={'review_sha256':{str(p):m.sha(p)},'intents':[dict(d)]}
    assert m.verify_review_bindings(mapping)==1
    mapping['intents'][0]['atom_paths']={'a':[]}
    with pytest.raises(ValueError,match='selected review'):m.verify_review_bindings(mapping)
    mapping['review_sha256']={}
    with pytest.raises(ValueError,match='selected review'):m.verify_review_bindings(mapping)
