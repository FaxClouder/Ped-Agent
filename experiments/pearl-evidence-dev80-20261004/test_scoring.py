import importlib.util
from pathlib import Path
import pytest

HERE = Path(__file__).parent

def load(name):
    path = HERE / (name + '.py')
    assert path.exists(), 'implementation missing: ' + name
    spec = importlib.util.spec_from_file_location('evidence_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_three_value_or_and_and_best_group_coverage():
    s = load('score')
    groups = [['a','b'], ['c','d']]
    assert s.score_support(groups, {'a':'yes','b':'no','c':'yes','d':'no'}) == {'sufficient':'no','coverage_lower':.5,'coverage_upper':.5}
    assert s.score_support(groups, {'a':'yes','b':'unknown','c':'no','d':'no'})['sufficient'] == 'unknown'
    assert s.score_support(groups, {'a':'no','b':'unknown','c':'yes','d':'yes'})['sufficient'] == 'yes'
    with pytest.raises(ValueError):
        s.score_support([[]], {})

def test_denominator_keeps_unknown_and_empty_context_na():
    s = load('score')
    rows = [{'sufficient':v,'coverage_lower':float(v=='yes'),'coverage_upper':float(v!='no'),'unit_labels':[]} for v in ['yes','no','unknown']]
    out = s.aggregate(rows)
    assert out['n'] == 3
    assert out['complete_group_lower'] == 1/3
    assert out['complete_group_upper'] == 2/3
    assert out['relevance_applicable_n'] == 0

def test_noise_and_relevance_are_not_complements():
    s = load('score')
    row = dict(sufficient='no',coverage_lower=0,coverage_upper=0,unit_labels=['mixed','unknown'])
    out = s.aggregate([row])
    assert out['relevance_lower'] == .5
    assert out['noise_lower'] == .5
    assert out['noise_upper'] == 1

def test_exact_mcnemar_and_holm():
    s = load('score')
    assert s.exact_mcnemar(0,4) == .125
    assert s.exact_mcnemar(0,0) == 1
    assert s.holm([.01,.02,.03,.9]) == [.04,.06,.06,.9]

def fixture_context(text='body', cid='i::C0-4096'):
    r = load('review')
    original='[Source source-secret | page 1]\nTitle: Paper\n'+text
    return {'context_id':cid,'intent_id':'i','configuration':cid.split('::')[1], 'query':'Q','serialized_context':original,'text_sha256':r.sha_text(original),'units':[{'unit_id':'u1','source_id':'source-secret','text':text,'title':'Paper','locator':'page 1'}]}

def test_blind_packet_dedup_and_binding_no_gold_leakage():
    r = load('review')
    contexts = [fixture_context(),fixture_context(cid='i::C1-4096')]
    intents = [{'intent_id':'i','query':'Q','requirements':[{'requirement_id':'a','claim':'fact','scope':'scope','support_bundles':[['SECRET']]}],'evidence_groups':[{'requirements':['a']}], 'reference_answer':'SECRET ANSWER','atoms':[{'anchor_text':'SECRET'}]}]
    packets, bindings = r.build_packets(contexts,intents,include_steps=False)
    assert len(packets) == 1 and len(bindings) == 2
    text = str(packets)
    assert 'SECRET' not in text and 'C0' not in text and 'C1' not in text and 'source-secret' not in text
    assert packets[0]['serialized_context'].endswith('body')
    assert all(b['original_text_sha256'] == contexts[0]['text_sha256'] for b in bindings)

def test_review_import_rejects_wrong_hash_missing_requirement_and_bad_quote():
    r = load('review')
    packet = {'packet_id':'p','packet_sha256':'h','requirements':[{'requirement_id':'a'}], 'units':[{'unit_id':'U1'}], 'serialized_context':'support'}
    good = {'packet_id':'p','packet_sha256':'h','support':{'a':{'label':'yes','rationale':'support','quotes':['support']}}, 'unit_labels':{'U1':'relevant'}}
    r.validate_review(packet,good)
    for key,value in [('packet_sha256','wrong'),('support',{}),('support',{'a':{'label':'yes','rationale':'bad','quotes':['absent']}})]:
        bad = dict(good, **{key:value})
        with pytest.raises(ValueError):
            r.validate_review(packet,bad)

def test_anonymous_sources_stay_stable_across_texts_and_steps():
    r = load('review')
    one=fixture_context(text='z-source body')
    one['units'][0]['source_id']='z-source'
    one['serialized_context']=one['serialized_context'].replace('Source source-secret','Source z-source')
    one['text_sha256']=r.sha_text(one['serialized_context'])
    two=fixture_context(text='a-source body',cid='i::C1-4096')
    two['units'][0]['source_id']='a-source'
    two['serialized_context']=two['serialized_context'].replace('Source source-secret','Source a-source')
    two['text_sha256']=r.sha_text(two['serialized_context'])
    intents=[{'intent_id':'i','query':'Q','requirements':[{'requirement_id':'a','claim':'fact'}],'evidence_groups':[{'requirements':['a']}]}]
    _,bindings=r.build_packets([one,two],intents,False)
    assert bindings[0]['source_map']==bindings[1]['source_map']

def test_pair_unknown_bounds_and_four_configuration_score():
    s,r=load('score'),load('review')
    contexts=[fixture_context(text=c+' body',cid='i::'+c) for c in s.CONFIGS]
    intents=[{'intent_id':'i','query':'Q','requirements':[{'requirement_id':'a','claim':'fact'}],'evidence_groups':[{'requirements':['a']}]}]
    packets,bindings=r.build_packets(contexts,intents,False)
    reviews=[{'packet_id':p['packet_id'],'packet_sha256':p['packet_sha256'],
              'support':{'a':{'label':'unknown','rationale':'ambiguous','quotes':[]}},'unit_labels':{'U1':'unknown'}} for p in packets]
    out=s.score_records(contexts,packets,bindings,reviews)
    assert len(out['rows'])==4
    assert all(p['unknown_pairs']==1 and p['delta_lower']==-1 and p['delta_upper']==1 for p in out['paired'])
    reviews[0]['support']['a']['label']='made-up'
    with pytest.raises(ValueError):
        s.score_records(contexts,packets,bindings,reviews)

def test_steps_attribution_requires_exact_distinct_text_judgments():
    s=load('score')
    assert hasattr(s,'attribute_steps'), 'steps attribution missing'
    scored=[{'context_id':'i::C1-4096','stage':stage,'sufficient':label,'support':{'a':label}} for stage,label in [('raw','no'),('expanded','yes'),('deduplicated','yes'),('final','no')]]
    out=s.attribute_steps(scored)
    assert out[0]['requirement_gains']==['a']
    assert out[-1]['requirement_losses']==['a']

def test_header_only_anonymization_retains_body_ids_and_duplicate_occurrences():
    r=load('review')
    context=fixture_context(text='u1 source-secret are literal body content')
    context['units']*=2
    context['serialized_context']='\n\n'.join([context['serialized_context']]*2)
    context['text_sha256']=r.sha_text(context['serialized_context'])
    intents=[{'intent_id':'i','query':'Q','requirements':[{'requirement_id':'a','claim':'fact'}],'evidence_groups':[{'requirements':['a']}]}]
    packets,bindings=r.build_packets([context],intents,False)
    assert packets[0]['serialized_context'].count('u1 source-secret are literal body content')==2
    assert [u['unit_id'] for u in packets[0]['units']]==['U1','U2']
    assert len(bindings[0]['unit_map'])==2

def test_selected_review_requires_actual_provenance_and_full_read():
    r=load('review')
    assert hasattr(r,'validate_provenance'), 'review provenance validation missing'
    good={'full_read':True,'reviewer_id':'reviewer','model_id':'inherited Codex model, not exposed',
          'prompt_sha256':r.sha_text(r.PROMPT),'elapsed_seconds':None}
    r.validate_provenance(good)
    with pytest.raises(ValueError):
        r.validate_provenance(dict(good,full_read=False))
    with pytest.raises(ValueError):
        r.validate_provenance(dict(good,prompt_sha256='wrong'))

def bootstrap_fixture(unknown=False):
    s=load('score')
    return [{'intent_id':f't{t}-i{i}','question_type':f't{t}','configuration':c,
             'sufficient':'unknown' if unknown else ('yes' if c.startswith('C1') else 'no')}
            for t in range(4) for i in range(2) for c in s.CONFIGS]

def test_stratified_intent_bootstrap_constant_paired_reference():
    s=load('score')
    assert hasattr(s,'bootstrap_intervals'), 'bootstrap supplement missing'
    out=s.bootstrap_intervals(bootstrap_fixture())
    assert out['replicates']==10000 and out['seed']==20261004 and out['n']==8
    assert out['stratum_sizes']=={'t0':2,'t1':2,'t2':2,'t3':2}
    assert out['overall']['C0-4096']['envelope']==[0,0]
    assert out['overall']['C1-4096']['envelope']==[1,1]
    assert out['paired'][0]['envelope']==[1,1]
    assert out['paired'][2]['envelope']==[0,0]

def test_bootstrap_unknown_bounds_keep_all_intents():
    s=load('score')
    assert hasattr(s,'bootstrap_intervals'), 'bootstrap supplement missing'
    out=s.bootstrap_intervals(bootstrap_fixture(True))
    assert out['n']==8
    assert all(c['envelope']==[0,1] for c in out['overall'].values())
    assert all(p['envelope']==[-1,1] for p in out['paired'])

def test_bootstrap_shared_paired_draws_reproducible_order_invariant():
    s=load('score')
    assert hasattr(s,'bootstrap_intervals'), 'bootstrap supplement missing'
    rows=bootstrap_fixture()
    for r in rows:
        if r['intent_id'].endswith('i1'):
            r['sufficient']='no' if r['configuration'].startswith('C1') else 'yes'
    first=s.bootstrap_intervals(rows)
    assert first==s.bootstrap_intervals(list(reversed(rows)))
    assert first['paired'][0]['lower_bound_ci']==first['paired'][0]['upper_bound_ci']
    assert first['paired'][0]['lower_bound_point']==0
    assert first['paired'][0]['envelope'][0]<0<first['paired'][0]['envelope'][1]
    assert first['paired'][2]['envelope']==[0,0]

def test_bootstrap_rejects_inconsistent_cluster_type_and_incomplete_matrix():
    s=load('score')
    assert hasattr(s,'bootstrap_intervals'), 'bootstrap supplement missing'
    rows=bootstrap_fixture()
    with pytest.raises(ValueError):
        s.bootstrap_intervals(rows[:-1])
    rows[0]['question_type']='different'
    with pytest.raises(ValueError):
        s.bootstrap_intervals(rows)

def truncation_fixture():
    a,r,s=load('assemble'),load('review'),load('score')
    class CharacterCounter:
        fingerprint='synthetic-character-v1'
        def count(self,text):
            return len(text)
    text='Width=1m\n'+'synthetic unrelated padding '*200+'\nSpeed=3.2 m/s'
    child={'chunk_id':'synthetic-child','text':text,'text_sha256':r.sha_text(text),'source_id':'synthetic-source',
           'source_sha256':'synthetic-source-v1','version_id':'synthetic-v1','title':'Fixed synthetic measurement',
           'locator':'page 1','policy_version':'parent-child-v1','parser_version':'synthetic-parser-v1'}
    contexts=[a.assemble('synthetic-truncation','Which width and speed?', [child],{},CharacterCounter(),c.split('-')[0],int(c.split('-')[1])) for c in s.CONFIGS]
    for c in contexts:
        c['question_type']='synthetic'
        c.pop('assembly_seconds')
    intent={'intent_id':'synthetic-truncation','query':'Which width and speed?',
            'requirements':[{'requirement_id':'width','claim':'Width is 1m'},{'requirement_id':'speed','claim':'Speed is 3.2 m/s'}],
            'evidence_groups':[{'requirements':['width','speed']}]}
    packets,bindings=r.build_packets(contexts,[intent])
    reviews=[]
    for p in packets:
        judgments={}
        # These are deterministic constructed reference labels, not real Agent review.
        for rid,quote in [('width','Width=1m'),('speed','Speed=3.2 m/s')]:
            exists=quote in p['serialized_context']
            judgments[rid]={'label':'yes' if exists else 'no',
                            'rationale':'Fixed fixture literal value and unit retained' if exists else 'Fixed fixture value and unit absent after truncation',
                            'quotes':[quote] if exists else []}
        reviews.append({'packet_id':p['packet_id'],'packet_sha256':p['packet_sha256'],'support':judgments,
                        'unit_labels':{u['unit_id']:'mixed' for u in p['units']}})
    scores=s.score_records(contexts,packets,bindings,reviews)
    return contexts,packets,bindings,reviews,scores

def test_saved_synthetic_truncation_reference_end_to_end(tmp_path):
    import json
    a,r,s=load('assemble'),load('review'),load('score')
    contexts,packets,bindings,reviews,scores=truncation_fixture()
    for c in contexts:
        assert 'Width=1m' in c['serialized_context']
        assert 'Speed=3.2 m/s' in c['steps']['raw']['serialized_context']
        assert ('Speed=3.2 m/s' in c['serialized_context'])==(c['budget']==8192)
    actual={'review_source':'deterministic_constructed_fixture_not_semantic_Agent',
            'context_hashes':{c['configuration']:c['text_sha256'] for c in contexts},'scores':scores}
    fixed=HERE/'fixtures'/'synthetic-truncation-reference.json'
    assert fixed.exists(), 'saved synthetic scoring reference missing'
    expected=json.loads(fixed.read_text(encoding='utf-8'))
    assert actual==expected
    for name,rows in [('contexts',contexts),('packets',packets),('bindings',bindings),('reviews',reviews)]:
        r.write_jsonl(tmp_path/(name+'.jsonl'),rows)
    saved_scores=tmp_path/'scores.json'
    saved_scores.write_text(json.dumps(scores),encoding='utf-8')
    reread=s.score_records(*(r.read_jsonl(tmp_path/(n+'.jsonl')) for n in ('contexts','packets','bindings','reviews')))
    assert reread==json.loads(saved_scores.read_text(encoding='utf-8'))
    assert all(row['sufficient']==('no' if row['configuration'].endswith('4096') else 'yes') for row in reread['rows'])
    losses=[change for change in reread['attribution'] if change['requirement_losses']]
    assert len(losses)==2 and all(change['requirement_losses']==['speed'] and change['before_stage']=='deduplicated' and change['after_stage']=='final' for change in losses)

def test_blind_export_rejects_gold_query_mismatch():
    r=load('review')
    intent={'intent_id':'i','query':'wrong frozen query','requirements':[{'requirement_id':'a','claim':'fact'}],'evidence_groups':[{'requirements':['a']}]}
    with pytest.raises(ValueError,match='query'):
        r.build_packets([fixture_context()],[intent])

def export_input_fixture(tmp_path):
    import json
    r=load('review')
    contexts=tmp_path/'contexts.jsonl'
    r.write_jsonl(contexts,[fixture_context()])
    gold=tmp_path/'gold.json'
    intent={'intent_id':'i','query':'Q','requirements':[{'requirement_id':'a','claim':'fact'}],'evidence_groups':[{'requirements':['a']}]}
    gold.write_text(json.dumps({'intents':[intent]}),encoding='utf-8')
    inputs=tmp_path/'input-manifest.json'
    inputs.write_text(json.dumps({'gold_path':str(gold),'gold_sha256':r.file_sha(gold),'input_sha256':{str(gold):r.file_sha(gold)}}),encoding='utf-8')
    assembly=tmp_path/'assembly-manifest.json'
    assembly.write_text(json.dumps({'input_manifest_sha256':r.file_sha(inputs),'output_sha256':{'input-manifest.json':r.file_sha(inputs),'contexts.jsonl':r.file_sha(contexts)}}),encoding='utf-8')
    return contexts,gold,inputs,assembly

def test_export_frozen_input_gate_discovers_adjacent_manifests(tmp_path):
    r=load('review')
    assert hasattr(r,'validate_export_inputs'), 'Gold export binding gate missing'
    contexts,gold,inputs,assembly=export_input_fixture(tmp_path)
    proof=r.validate_export_inputs(contexts,gold)
    assert proof['input_manifest_sha256']==r.file_sha(inputs)
    assert proof['assembly_manifest_sha256']==r.file_sha(assembly)

@pytest.mark.parametrize('mutation',['gold','contexts','input_manifest','unfrozen_gold_path','missing_manifest'])
def test_export_rejects_unbound_input_before_output_creation(tmp_path,monkeypatch,mutation):
    import json
    import sys
    r=load('review')
    contexts,gold,inputs,assembly=export_input_fixture(tmp_path)
    if mutation=='gold':
        gold.write_text('{}',encoding='utf-8')
    elif mutation=='contexts':
        contexts.write_text('{}\n',encoding='utf-8')
    elif mutation=='input_manifest':
        inputs.write_text('{}',encoding='utf-8')
    elif mutation=='unfrozen_gold_path':
        alternate=tmp_path/'unfrozen.json'
        alternate.write_bytes(gold.read_bytes())
        gold=alternate
    else:
        assembly.unlink()
    output=tmp_path/'uncreated-output'
    monkeypatch.setattr(sys,'argv',['review.py','export','--contexts',str(contexts),'--gold',str(gold),'--output',str(output)])
    with pytest.raises((ValueError,FileNotFoundError)):
        r.main()
    assert not output.exists()
