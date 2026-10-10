"""Scientific safeguards and finite-depth diagnostic reference examples."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import pytest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

def module(name):
    path = HERE / (name + '.py')
    assert path.exists(), 'missing implementation: ' + name
    spec = importlib.util.spec_from_file_location('dev80_' + name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def fixture():
    g = {'intent_id':'q', 'query':'question', 'main_stratum':'single',
         'atoms':[{'atom_id':'a','source_id':'s'}],
         'requirements':[{'requirement_id':'r','support_bundles':[['a']]}],
         'evidence_groups':[{'group_id':'g','requirements':['r']}]}
    def child(cid, text):
        return {'chunk_id':cid,'text':text,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),
                'source_id':'s','source_sha256':'sourcehash','title':'title','page_start':1,'page_end':1,'locator':{}}
    packet = {'intent':g, 'candidates':[child('x','fact and condition')],
              'supplementary_candidates':[child('y','unknown deeper fact')]}
    decision = {'review_type':'subagent_blind_content','intent_id':'q','packet_sha256':'packet-hash',
                'reviewer_id':'separate-agent','atom_paths':{'a':[['x']]},
                'reviewed_ids':['x'],'unresolved_ids':['y'],
                'path_evidence':[{'atom_id':'a','chunk_ids':['x'],'reason':'exact fact with condition',
                                  'excerpts':[{'chunk_id':'x','text':'fact and condition'}]}],
                'rejection_summary':'Other candidates not assessed','notes':'deep unresolved'}
    return g, packet, decision

def test_deep_unresolved_preserved_and_valid_path():
    s = module('score'); g,p,d = fixture()
    validated = s.validate_decision(g,p,d,'packet-hash')
    assert validated['unresolved_ids'] == ['y']
    assert validated['atom_paths'] == {'a':[['x']]}

@pytest.mark.parametrize('corrupt,match',[
    (lambda d:d.update(packet_sha256='wrong'),'packet'),
    (lambda d:d.update(reviewed_ids=['y']),'required'),
    (lambda d:d.update(unresolved_ids=['x','y']),'unresolved'),
    (lambda d:d.update(atom_paths={'a':[[]]}),'path'),
    (lambda d:d.update(atom_paths={'a':[['missing']]}),'path'),
    (lambda d:d['path_evidence'][0]['excerpts'][0].update(text='invented'),'excerpt'),
    (lambda d:d['path_evidence'][0].update(reason=''),'reason'),
    (lambda d:d.update(path_evidence=[]),'evidence'),
    (lambda d:d.update(reviewed_ids=['x','ghost']),'identity'),
    (lambda d:d.update(unresolved_ids=[]),'partition'),
])
def test_review_fails_closed(corrupt,match):
    s = module('score'); g,p,d = fixture(); corrupt(d)
    with pytest.raises(ValueError,match=match):s.validate_decision(g,p,d,'packet-hash')

def test_child_hash_and_gold_identity_rejected():
    s = module('score'); g,p,d = fixture()
    p['candidates'][0]['text_sha256']='wrong'
    with pytest.raises(ValueError,match='hash'):s.validate_decision(g,p,d,'packet-hash')
    g,p,d=fixture();p['intent']['query']='changed'
    # Construct independent expected Gold to avoid shared fixture object alias.
    gold=copy.deepcopy(g);gold['query']='question'
    with pytest.raises(ValueError,match='Gold'):s.validate_decision(gold,p,d,'packet-hash')

def test_valid_empty_and_short_are_not_execution_errors():
    s=module('score');g,p,d=fixture();children={c['chunk_id']:c for c in p['candidates']}
    row={'intent_id':'q','method':'R1','query':'question','status':'success','returned':0,
         'return_reason':'no lexical match','results':[]}
    assert s.validate_ranking(row,g,children)==[]
    row.update(status='error')
    with pytest.raises(ValueError,match='execution'):s.validate_ranking(row,g,children)

def test_duplicate_original_ranks_are_preserved():
    s=module('score');g,p,d=fixture();child=p['candidates'][0]
    results=[dict(child,rank=i) for i in [1,2]]
    row={'intent_id':'q','method':'R1','query':'question','status':'success','returned':2,
         'return_reason':'valid short list','results':results}
    assert s.validate_ranking(row,g,{'x':child})==['x','x']

def test_exact_mcnemar_and_holm_reference():
    a=module('analyze')
    assert a.exact_mcnemar(0,0)==1
    assert a.exact_mcnemar(6,0)==pytest.approx(0.03125)
    assert a.holm([.01,.04,.03])==pytest.approx([.03,.06,.06])

def test_source_components_cross_strata():
    a=module('analyze')
    gold=[{'intent_id':'a','main_stratum':'h1','atoms':[{'source_id':'s'}]},
          {'intent_id':'b','main_stratum':'h2','atoms':[{'source_id':'s'},{'source_id':'t'}]},
          {'intent_id':'c','main_stratum':'h1','atoms':[{'source_id':'t'}]},
          {'intent_id':'d','main_stratum':'h2','atoms':[{'source_id':'u'}]}]
    assert sorted(map(sorted,a.source_components(gold)))==[['a','b','c'],['d']]

def test_paired_bootstrap_preserves_exact_constant_difference():
    a=module('analyze')
    import numpy as np
    values=np.array([[0.,1.],[0.,1.],[0.,1.],[0.,1.]])
    dist=a.stratified_bootstrap(values,['h1','h1','h2','h2'],100,20260929)
    assert dist.shape==(100,2)
    assert np.all(dist[:,1]-dist[:,0]==1)

def test_unresolved_deep_blocks_negative_not_known_positive():
    a=module('analyze');g,p,d=fixture()
    # Known complete path at 27 proves Top-K failure even if other deeper IDs unresolved.
    ranks=['noise']*26+['x']+['y']
    state=a.depth_state(g,d,ranks,100)
    assert state['complete'] is True
    assert state['first_complete_rank_upper_bound']==27
    # First completion remains an upper bound when earlier unreviewed records exist.
    assert state['first_complete_rank'] is None
    state=a.depth_state(g,d,['noise','y'],100)
    assert state['complete'] is None
    assert state['state']=='unresolved'

def frozen_fixture(tmp_path):
    s=module('score');g,p,d=fixture()
    index=tmp_path/'index';index.mkdir()
    run=tmp_path/'run';run.mkdir()
    children=p['candidates']+p['supplementary_candidates']
    (index/'child_chunks.jsonl').write_text(''.join(__import__('json').dumps(c)+'\n' for c in children),encoding='utf8')
    s.write(index/'build_manifest.json',{'status':'frozen'})
    q2=copy.deepcopy(g);q2['intent_id']='q2'
    gold={'intents':[g,q2],'frozen_child_library_sha256':s.sha(index/'child_chunks.jsonl')}
    gold_path=tmp_path/'gold.json';s.write(gold_path,gold)
    pre=dict(index_dir=str(index),gold_sha256=s.sha(gold_path),frozen_child_sha256=s.sha(index/'child_chunks.jsonl'),
             index_build_manifest_sha256=s.sha(index/'build_manifest.json'))
    s.write(run/'preflight.json',pre)
    rank_rows=[]
    for q in gold['intents']:
        for m in s.METHODS:
            rank_rows.append(dict(intent_id=q['intent_id'],query=q['query'],method=m,status='success',returned=1,
                                 short_result_reason='one candidate',results=[dict(children[0],rank=1)]))
    (run/'rankings.jsonl').write_text(''.join(__import__('json').dumps(r)+'\n' for r in rank_rows),encoding='utf8')
    s.write(run/'run_manifest.json',dict(run_id='run',status='retrieval_complete_support_review_pending',
           input_binding=pre,preflight_sha256=s.sha(run/'preflight.json'),methods_executed=list(s.METHODS),
           execution_failures=[],output_sha256={'rankings.jsonl':s.sha(run/'rankings.jsonl')}))
    packets=run/'review/packets';packets.mkdir(parents=True)
    reviews=[]
    for q in gold['intents']:
        pack=copy.deepcopy(p);pack['intent']=q;s.write(packets/(q['intent_id']+'.json'),pack)
        dec=copy.deepcopy(d);dec.update(intent_id=q['intent_id'],packet_sha256=s.sha(packets/(q['intent_id']+'.json')))
        reviews.append(dec)
    batch=tmp_path/'arbitrary-review-batch.json';s.write(batch,{'review_type':'subagent_blind_content','intents':reviews})
    return s,run,gold_path,batch

def test_arbitrary_batch_full_matrix_and_independent_reload(tmp_path):
    s,run,gold,batch=frozen_fixture(tmp_path)
    mapping=run/'map.json';s.combine(run,mapping,gold,[batch],expected_count=2)
    report=s.score(run,mapping,run/'score.json',gold,expected_count=2,csv_output=run/'scores.csv')
    assert len(report['details'])==8
    assert all(report['summary'][m]['10']['CEGR']==1 for m in s.METHODS)
    assert len((run/'scores.csv').read_text().splitlines())==9
    reloaded=s.score(run,mapping,run/'recomputed.json',gold,expected_count=2)
    assert reloaded['details']==report['details']
    with pytest.raises(FileExistsError):s.score(run,mapping,run/'score.json',gold,expected_count=2)

def test_missing_matrix_cell_rejected_before_scoring(tmp_path):
    s,run,gold,batch=frozen_fixture(tmp_path)
    path=run/'rankings.jsonl';lines=path.read_text().splitlines();path.write_text('\n'.join(lines[:-1])+'\n')
    manifest=s.read(run/'run_manifest.json');manifest['output_sha256']['rankings.jsonl']=s.sha(path)
    (run/'run_manifest.json').write_text(__import__('json').dumps(manifest))
    with pytest.raises(ValueError,match='missing ranking matrix'):s.combine(run,run/'map.json',gold,[batch],expected_count=2)

def test_corrupted_frozen_rank_and_review_files_rejected(tmp_path):
    s,run,gold,batch=frozen_fixture(tmp_path)
    mapping=run/'map.json';s.combine(run,mapping,gold,[batch],expected_count=2)
    with batch.open('a') as f:f.write(' ')
    with pytest.raises(ValueError,match='hash mismatch'):s.score(run,mapping,run/'score.json',gold,expected_count=2)

def test_stripped_semantic_packet_retains_gold_identity():
    s=module('score');g,p,d=fixture()
    p['intent']=copy.deepcopy(p['intent']);p['intent'].pop('main_stratum')
    assert s.validate_decision(g,p,d,'packet-hash')['intent_id']=='q'

@pytest.mark.parametrize('change',['decision','empty_binding'])
def test_mapping_cannot_diverge_from_selected_review(tmp_path,change):
    s,run,gold,batch=frozen_fixture(tmp_path)
    mapping=run/'map.json';value=s.combine(run,mapping,gold,[batch],expected_count=2)
    if change=='decision':
        value['intents'][0]['atom_paths']['a']=[]
        value['intents'][0]['path_evidence']=[]
    else:value['review_sha256']={}
    mapping.write_text(__import__('json').dumps(value),encoding='utf8')
    with pytest.raises(ValueError,match='selected review'):
        s.score(run,mapping,run/'score.json',gold,expected_count=2)
