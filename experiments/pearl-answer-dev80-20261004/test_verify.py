import copy
import hashlib
import json

import pytest
from test_score import load, bundle


def test_independent_recomputation():
    s = load('score'); v = load('verify'); b = bundle()
    result = s.score_bundle(b)
    assert v.recompute(b) == result
    b['cells'][0]['generation_status'] = 'generation_failed'
    b['cells'][1]['decision']['targets']['t1'] = 'unknown'
    assert v.recompute(b) == s.score_bundle(b)
    assert 'import score' not in __import__('pathlib').Path(v.__file__).read_text()


def digest(value):
    raw=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def saved_fixture(tmp_path):
    s=load('score'); v=load('verify'); b=bundle()
    template='{query}\n{exact_saved_context}'
    config={'model':'synthetic','protocol':'synthetic'}
    answer=[]; context=[]; decisions=[]; labels=[]
    for c in b['cells']:
        identity=c['intent_id']+'::'+c['arm']; query='Synthetic Q'; body='Synthetic C'
        request=template.format(query=query,exact_saved_context=body)
        source={'cell_id':identity,'intent_id':c['intent_id'],'arm':c['arm'],'record_kind':'synthetic','generation_status':'returned','query':query,'request':request,'request_sha256':digest(request),'context_sha256':digest(body),'config':config,'config_sha256':digest(config),'raw_answer':'Synthetic A','response_sha256':digest('Synthetic A')}
        source['record_sha256']=digest(source)
        c.update({k:source[k] for k in ['request_sha256','context_sha256','config_sha256','response_sha256']},generation_record_sha256=source['record_sha256'])
        answer.append(source)
        context.append({'cell_id':identity,'intent_id':c['intent_id'],'arm':c['arm'],'query':query,'context':body,'request':request,'request_sha256':digest(request),'context_sha256':digest(body)})
        decisions.append({'intent_id':c['intent_id'],'arm':c['arm'],'decision':c['decision']})
        labels.append({'intent_id':c['intent_id'],'arm':c['arm'],'sufficient':c['l2_sufficient'],'context_sha256':digest(body)})
    data={'answer':{'rows':answer},'context':{'rows':context},'reference':{'rows':b['references']},'decision':{'rows':decisions},'l2':{'rows':labels},'config':config,'prompt':{'prompt_template':template},'input':b,'result':s.score_bundle(b)}
    binding={'schema_version':'pearl-answer-score-bindings-v1','mode':'synthetic','input_path':str(tmp_path/'input.json'),'result_path':str(tmp_path/'result.json'),'artifacts':[]}
    for role,value in data.items():
        path=tmp_path/(role+'.json'); path.write_text(json.dumps(value),encoding='utf-8')
        binding['artifacts'].append({'role':role,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return b,binding


def test_saved_provenance_recomputed_and_changed_input_rejected(tmp_path):
    v=load('verify'); b,binding=saved_fixture(tmp_path)
    assert v.verify_saved(binding)['verified']
    for artifact in binding['artifacts']:
        path=__import__('pathlib').Path(artifact['path']); original=path.read_bytes(); path.write_bytes(original+b'changed')
        with pytest.raises(ValueError): v.verify_saved(binding)
        path.write_bytes(original)
    bad=copy.deepcopy(binding); bad['mode']='real'
    with pytest.raises(ValueError): v.verify_saved(bad)


@pytest.mark.parametrize('change',['reference','decision','l2','request'])
def test_crossmanifest_rejects_recomputed_tampered_input(tmp_path,change):
    s=load('score'); v=load('verify'); b,binding=saved_fixture(tmp_path)
    if change=='reference': b['references'][0]['numeric_targets'][0]['tolerance']=999
    elif change=='decision': b['cells'][0]['decision']['targets']['t1']='incorrect'
    elif change=='l2': b['cells'][0]['l2_sufficient']='no'
    else: b['cells'][0]['request_sha256']='changed'
    for role,value in [('input',b),('result',s.score_bundle(b))]:
        artifact=next(a for a in binding['artifacts'] if a['role']==role)
        path=__import__('pathlib').Path(artifact['path']); path.write_text(json.dumps(value),encoding='utf-8')
        artifact['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError,match='cross-binding'): v.verify_saved(binding)
