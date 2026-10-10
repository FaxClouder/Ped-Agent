"""Synthetic 80-intent fail-closed revision reference; no sealed evaluation access."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).parent
BASE = HERE.parent / 'pearl-retrieval-dev80-20261003'
sys.path.insert(0, str(BASE))
import score


def engine():
    path = HERE / 'revision.py'
    assert path.exists(), 'missing explicit revision loader'
    spec = importlib.util.spec_from_file_location('revision_engine', path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding='utf8')


def fixture(tmp):
    run = tmp / 'run'; run.mkdir()
    index = tmp / 'index'; index.mkdir()
    child = dict(chunk_id='x', text='literal fact', text_sha256=hashlib.sha256(b'literal fact').hexdigest(),
                 source_id='s', source_sha256='source', title='title', page_start=1, page_end=1, locator={})
    (index/'child_chunks.jsonl').write_text(json.dumps(child)+'\n', encoding='utf8')
    save(index/'build_manifest.json', {})
    intents = [dict(intent_id=f'pearl-dev-{i:03}', query=f'question {i}', reference_answer='answer',
                    main_stratum=str((i-1)//20), atoms=[dict(atom_id=a, source_id='s',page=1,locator_type='text_anchor',anchor_text='literal fact',supports='fact') for a in ('a1','a2')],
                    requirements=[dict(requirement_id=r,claim='original claim',scope='original scope',support_bundles=[[a]]) for r,a in (('r1','a1'),('r2','a2'))],
                    evidence_groups=[dict(group_id='g1', requirements=['r1','r2'])]) for i in range(1,81)]
    gold = dict(intents=intents, frozen_child_library_sha256=score.sha(index/'child_chunks.jsonl'), status='agent_reviewed_preliminary')
    original = tmp/'base.json'; save(original,gold)
    pre = dict(gold_sha256=score.sha(original), index_dir=str(index), frozen_child_sha256=gold['frozen_child_library_sha256'], index_build_manifest_sha256=score.sha(index/'build_manifest.json'))
    save(run/'preflight.json',pre)
    ranks=[dict(intent_id=q['intent_id'], query=q['query'], method=m, status='success', returned=1, short_result_reason='synthetic', results=[dict(child,rank=1)]) for q in intents for m in score.METHODS]
    (run/'rankings.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in ranks), encoding='utf8')
    unions=[dict(intent_id=q['intent_id'],query=q['query'],union=[child]) for q in intents]
    (run/'rrf_union.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in unions), encoding='utf8')
    save(run/'run_manifest.json',dict(run_id='synthetic',status='retrieval_complete',input_binding=pre, preflight_sha256=score.sha(run/'preflight.json'),methods_executed=list(score.METHODS),execution_failures=[],output_sha256={n:score.sha(run/n) for n in ('rankings.jsonl','rrf_union.jsonl')}))
    revised=copy.deepcopy(gold); changes=[]
    revisions=[(['intents',11,'requirements',0,'scope'],'revised scope'),
               (['intents',49,'reference_answer'],'revised answer'),
               (['intents',79,'reference_answer'],'revised answer'),
               (['intents',79,'requirements',1,'claim'],'revised claim'),
               (['intents',79,'requirements',1,'scope'],'revised scope'),
               (['intents',79,'requirements',1,'support_bundles'],[['a2','a3']]),
               (['intents',79,'atoms'],intents[79]['atoms']+[dict(atom_id='a3',source_id='s',page=1,locator_type='text_anchor',anchor_text='numerically verified behavior',supports='numerical verification')])]
    for path,value in revisions:
        parent=revised
        for part in path[:-1]:parent=parent[part]
        changes.append(dict(path=path,old_value=copy.deepcopy(parent[path[-1]]),new_value=value))
        parent[path[-1]]=copy.deepcopy(value)
    revised_path=tmp/'revised.json';save(revised_path,revised)
    diff=tmp/'diff.json';save(diff,dict(changes=changes))
    old_decisions=[]; files=[]
    for q,new in zip(intents,revised['intents']):
        packet=run/'review/packets'/f"{q['intent_id']}.json"
        save(packet,dict(intent=q,candidates=[child]))
        d=dict(review_type='subagent_blind_content',intent_id=q['intent_id'],reviewer_id='independent',packet_sha256=score.sha(packet),reviewed_ids=['x'],unresolved_ids=[],atom_paths={a['atom_id']:[['x']] for a in q['atoms']},path_evidence=[dict(atom_id=a['atom_id'],chunk_ids=['x'],reason='literal',excerpts=[dict(chunk_id='x',text='literal fact')]) for a in q['atoms']],rejection_summary='none',notes='synthetic')
        old_path=tmp/'old'/f"{q['intent_id']}.json";save(old_path,d);old_decisions.append(old_path)
        if q!=new:
            packet=tmp/'packets'/packet.name;save(packet,dict(intent=new,candidates=[child]))
            d=copy.deepcopy(d);d['packet_sha256']=score.sha(packet)
            if q['intent_id']=='pearl-dev-080':
                d['atom_paths']['a3']=[['x']]
                d['path_evidence'].append(dict(atom_id='a3',chunk_ids=['x'],reason='literal',excerpts=[dict(chunk_id='x',text='literal fact')]))
            path=tmp/'new'/old_path.name;save(path,d)
        else:path=old_path
        files.append(dict(intent_id=q['intent_id'],path=str(path),sha256=score.sha(path),packet_path=str(packet),packet_sha256=score.sha(packet)))
    mapping=tmp/'original-map.json';score.combine(run,mapping,original,old_decisions)
    original_selection=run/'review/selected-review-files.json'
    save(original_selection,dict(files=[dict(intent_id=score.read(p)['intent_id'],path=str(p),sha256=score.sha(p)) for p in old_decisions]))
    selection=tmp/'selection.json';save(selection,dict(files=files,base_selection_sha256=score.sha(original_selection)))
    manifest=tmp/'revision-manifest.json'
    save(manifest,dict(schema_version='pearl-gold-revision-r02-v1',status='agent_reviewed_preliminary',human_verified=False,base=dict(gold_sha256=score.sha(original),rankings_sha256=score.sha(run/'rankings.jsonl'),run_manifest_sha256=score.sha(run/'run_manifest.json'),preflight_sha256=score.sha(run/'preflight.json'),mapping_path=str(mapping),mapping_sha256=score.sha(mapping)),revised_gold_sha256=score.sha(revised_path),selected_review_manifest_sha256=score.sha(selection),diff_path=str(diff),diff_sha256=score.sha(diff),changed_intent_ids=['pearl-dev-012','pearl-dev-050','pearl-dev-080']))
    return dict(base_directory=run,base_gold_path=original,revised_gold_path=revised_path,selected_review_manifest=selection,revision_manifest=manifest)


@pytest.mark.parametrize('corruption',['gold_sha','query','unchanged','duplicate','missing','decision','child','unreviewed','ranking','unauthorized_delta'])
def test_revision_rejects_corrupt_inputs(tmp_path,corruption):
    args=fixture(tmp_path);r=engine(); manifest=score.read(args['revision_manifest']);selection=score.read(args['selected_review_manifest'])
    if corruption in ('query','unchanged','unauthorized_delta'):
        g=score.read(args['revised_gold_path']);i=11 if corruption!='unchanged' else 0
        g['intents'][i]['query' if corruption=='query' else 'reference_answer']='unexpected'
        save(args['revised_gold_path'],g);manifest['revised_gold_sha256']=score.sha(args['revised_gold_path'])
    elif corruption=='gold_sha':manifest['base']['gold_sha256']='wrong'
    elif corruption=='ranking':manifest['base']['rankings_sha256']='wrong'
    elif corruption=='duplicate':selection['files'][-1]=selection['files'][0]
    elif corruption=='missing':selection['files'].pop()
    elif corruption=='decision':
        with Path(selection['files'][0]['path']).open('a') as f:f.write(' ')
    elif corruption in ('child','unreviewed'):
        entry=selection['files'][11]
        if corruption=='child':
            p=score.read(entry['packet_path']);p['candidates'][0]['text']='different';save(Path(entry['packet_path']),p)
            entry['packet_sha256']=score.sha(entry['packet_path'])
        else:
            d=score.read(entry['path']);d.update(reviewed_ids=[],unresolved_ids=['x']);save(Path(entry['path']),d);entry['sha256']=score.sha(entry['path'])
    save(args['selected_review_manifest'],selection);manifest['selected_review_manifest_sha256']=score.sha(args['selected_review_manifest']);save(args['revision_manifest'],manifest)
    with pytest.raises(ValueError):r.load_revision(**args)


def test_revision_preserves_base_identity_and_independent_oracle(tmp_path):
    args=fixture(tmp_path);r=engine();inputs=r.load_revision(**args)
    assert inputs['run']['input_binding']['gold_sha256']==score.sha(args['base_gold_path'])
    assert inputs['q_by']['pearl-dev-012']['requirements'][0]['scope']=='revised scope'
    details=score.build_details(inputs);scored=dict(details=details,summary=score.aggregate(details))
    result=r.independent_verification(inputs,scored)
    assert result['independent_formula_prefixes']==1280
    assert result['independent_aggregates']==48
    scored['details'][0]['scores']['10']['CEGR']=0
    with pytest.raises(ValueError):r.independent_verification(inputs,scored)


def test_delivery_outputs_and_no_overwrite(tmp_path):
    args=fixture(tmp_path);r=engine();out=tmp_path/'delivery'
    result=r.deliver(**args,output_directory=out)
    assert result['verification']['status']=='passed'
    assert set(result['statistics']['comparisons'])=={'R2-R1','R3-R2','R4-R3'}
    assert len(score.read(out/'delta-vs-r01.json')['details'])==320
    assert len((out/'scores.csv').read_text().splitlines())==321
    with pytest.raises(FileExistsError):r.deliver(**args,output_directory=out)


def test_saved_output_binding_rejects_tampering(tmp_path):
    args=fixture(tmp_path);r=engine();out=tmp_path/'delivery'
    r.deliver(**args,output_directory=out)
    assert r.verify_saved_outputs(**args,output_directory=out)['status']=='passed'
    mapping=score.read(out/'support-map.json');mapping['intents'][0]['notes']='changed saved decision'
    save(out/'support-map.json',mapping)
    with pytest.raises(ValueError):r.verify_saved_outputs(**args,output_directory=out)


def test_numerical_verification_atom_is_mandatory_for_completion(tmp_path):
    args=fixture(tmp_path);r=engine();inputs=r.load_revision(**args)
    q=inputs['q_by']['pearl-dev-080']
    inputs['decisions'][q['intent_id']]['atom_paths']['a3']=[]
    details=score.build_details(inputs)
    cells=[d for d in details if d['intent_id']==q['intent_id']]
    assert all(d['scores']['20']['CEGR']==0 for d in cells)
    assert r.independent_verification(inputs,dict(details=details,summary=score.aggregate(details)))['status']=='passed'


@pytest.mark.parametrize('change',['source','field','no_a3','weakened_bundle','old_atom','metadata'])
def test_consistently_rebound_forbidden_gold_delta(tmp_path,change):
    args=fixture(tmp_path);r=engine();manifest=score.read(args['revision_manifest']);g=score.read(args['revised_gold_path']);diff=score.read(manifest['diff_path'])
    if change=='source':path=['intents',11,'atoms',0,'source_id'];value='different-source'
    elif change=='field':path=['intents',11,'reference_answer'];value='unexpected change'
    elif change=='no_a3':path=['intents',79,'atoms'];value=g['intents'][79]['atoms'][:2]
    elif change=='old_atom':path=['intents',79,'atoms'];value=copy.deepcopy(g['intents'][79]['atoms']);value[0]['supports']='drift'
    elif change=='metadata':path=['annotation_provenance'];g['annotation_provenance']='new';value='changed'
    else:path=['intents',79,'requirements',1,'support_bundles'];value=[['a2']]
    parent=g
    for part in path[:-1]:parent=parent[part]
    for item in diff['changes']:
        if item['path']==path:item['new_value']=value;break
    else:diff['changes'].append(dict(path=path,old_value=parent[path[-1]],new_value=value))
    parent[path[-1]]=value
    if change=='no_a3':
        g['intents'][79]['requirements'][1]['support_bundles']=[['a2']]
        next(c for c in diff['changes'] if c['path']==['intents',79,'requirements',1,'support_bundles'])['new_value']=[['a2']]
    if change=='metadata':
        # Add a new disallowed root key with an explicitly rebound addition.
        diff['changes'][-1].update(op='add',old_value=None)
    save(args['revised_gold_path'],g);save(Path(manifest['diff_path']),diff)
    selection=score.read(args['selected_review_manifest'])
    for entry in selection['files']:
        if entry['intent_id'] not in ('pearl-dev-012','pearl-dev-050','pearl-dev-080'):continue
        q=next(q for q in g['intents'] if q['intent_id']==entry['intent_id'])
        packet=score.read(entry['packet_path']);packet['intent']=q;save(Path(entry['packet_path']),packet)
        entry['packet_sha256']=score.sha(entry['packet_path'])
        decision=score.read(entry['path']);decision['packet_sha256']=entry['packet_sha256']
        decision['atom_paths']={a['atom_id']:[['x']] for a in q['atoms']}
        decision['path_evidence']=[dict(atom_id=a['atom_id'],chunk_ids=['x'],reason='literal',excerpts=[dict(chunk_id='x',text='literal fact')]) for a in q['atoms']]
        save(Path(entry['path']),decision);entry['sha256']=score.sha(entry['path'])
    save(args['selected_review_manifest'],selection);manifest['selected_review_manifest_sha256']=score.sha(args['selected_review_manifest'])
    manifest.update(revised_gold_sha256=score.sha(args['revised_gold_path']),diff_sha256=score.sha(manifest['diff_path']));save(args['revision_manifest'],manifest)
    with pytest.raises(ValueError,match='authorized|preserved|a3|bundle|metadata'):
        r.load_revision(**args)


def test_inherited_decision_same_parsed_content_different_whole_file(tmp_path):
    args=fixture(tmp_path);r=engine();selection=score.read(args['selected_review_manifest']);entry=selection['files'][0]
    original=Path(entry['path']);copy_path=tmp_path/'copied-review.json'
    copy_path.write_bytes(original.read_bytes()+b' ')
    assert score.read(original)==score.read(copy_path)
    entry.update(path=str(copy_path),sha256=score.sha(copy_path));save(args['selected_review_manifest'],selection)
    manifest=score.read(args['revision_manifest']);manifest['selected_review_manifest_sha256']=score.sha(args['selected_review_manifest']);save(args['revision_manifest'],manifest)
    with pytest.raises(ValueError,match='inherited.*file'):
        r.load_revision(**args)
