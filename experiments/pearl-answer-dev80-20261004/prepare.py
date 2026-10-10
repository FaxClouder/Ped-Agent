"""Offline extraction of frozen Layer 2 inputs; no retrieval or model requests."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ARMS = {'C0-4096':'A0-4096','C0-8192':'A0-8192','C1-4096':'A1-4096','C1-8192':'A1-8192'}
PROMPT = '''Answer the research question in English using only the supplied context.
State the requested findings and retain the relevant experimental conditions,
numerical values and units. For comparisons, explicitly explain the relationship
between the findings rather than listing unrelated facts. Use the supplied
source labels for citations where possible. Do not invent missing evidence.
If the context does not establish part of the answer, state that limitation.

Question:
{query}

Context:
{exact_saved_context}'''
EVIDENCE = 'outputs/pearl-evidence-dev80-20261004-01'
PINNED = {
    EVIDENCE+'/delivery-manifest-r01.json':'021e20fc45909237a514a8356e65dbfaaf0e8054bcbdc7b0ed694134b656d8dc',
    EVIDENCE+'/stage80/contexts.jsonl':'2463a197f1bd2250eadaf09c4bc3667e3e5d022ca4bd0495303efc660177b49a',
    EVIDENCE+'/stage80/scores-r01.json':'136840ddd2ad6665733077bef4a321fa74c65fec18d98ee23f1f9e953ed81be5',
    'outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-r02.json':'7f64ac4559fbf604c0d4d6aca81e23685f1dcbf009853ee3c8637dc368ad29f5'
}

def sha_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def relpath(root, name):
    return root / name.replace('\\','/')

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def read_lines(path):
    with Path(path).open('rb') as stream:
        start=0
        for raw in stream:
            end=start+len(raw)
            if raw.strip():
                row=json.loads(raw)
                yield row, start, end
            start=end

def write_new_json(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2); stream.write('\n')

def write_new_lines(path, rows):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        for row in rows: stream.write(json.dumps(row,ensure_ascii=False)+'\n')

def audit_files(root, files):
    records=[]; changes=[]
    for record in files:
        name=record['path'].replace('\\','/')
        path=relpath(root,name)
        actual=sha_file(path) if path.is_file() else None
        item={'path':name,'expected_sha256':record['sha256'],'actual_sha256':actual,'matched':actual==record['sha256']}
        records.append(item)
        if not item['matched']:
            if name=='docs/README.md' and actual is not None: changes.append(item)
            else: raise ValueError('frozen file changed or missing: '+name)
    return {'checked':len(records),'matched':sum(x['matched'] for x in records),'navigation_changes':changes,'records':records}

def generation_row(row):
    context=row['serialized_context']
    if sha_text(context)!=row['text_sha256']: raise ValueError('context hash mismatch')
    arm=ARMS[row['configuration']]
    request=PROMPT.format(query=row['query'],exact_saved_context=context)
    return {'cell_id':row['intent_id']+'::'+arm,'intent_id':row['intent_id'],'arm':arm,'query':row['query'],'context':context,'context_sha256':sha_text(context),'request':request,'request_sha256':sha_text(request)}

def validate_cells(rows, intents):
    keys=[(r['intent_id'],r['arm']) for r in rows]
    expected={(i,a) for i in intents for a in ARMS.values()}
    if len(keys)!=len(set(keys)) or set(keys)!=expected: raise ValueError('missing, duplicate or unexpected intent/arm cell')

def reference_packet(intent, chunks, gold_sha):
    source_ids={a['source_id'] for a in intent['atoms']}
    allowed=('source_id','chunk_id','text','text_sha256','source_sha256','page_start','page_end','locator','title','version_id','parser_version','policy_version','jsonl_byte_start','jsonl_byte_end','source_library_path','source_library_sha256')
    sources=[{k:c[k] for k in allowed if k in c} for c in chunks if c['source_id'] in source_ids]
    if {s['source_id'] for s in sources}!=source_ids: raise ValueError('allowed source body missing')
    for s in sources:
        if sha_text(s['text'])!=s['text_sha256']: raise ValueError('source text hash mismatch')
    return {'schema_version':'pearl-answer-reference-build-v1','intent_id':intent['intent_id'],'query':intent['query'],'stratum':intent['main_stratum'],'requirements':intent['requirements'],'atoms':intent['atoms'],'evidence_groups':intent['evidence_groups'],'gold_sha256':gold_sha,'sources':sources,'reference_status':'independent_build_pending','source_scope':'all frozen parent text chunks of allowed sources; no retrieved ordering'}

def model_presence(root):
    sys.path.insert(0,str(root/'Agent/src'))
    from ped_research_agent.config import load_settings
    try:
        settings=load_settings(root/'.env')
    except Exception as exc:
        return {'configured':False,'error_type':type(exc).__name__,'api_key_present':False,'network_request_sent':False,'window_verified':False}
    answer=settings.answer
    return {'configured':True,'api_key_present':answer.api_key is not None,'protocol':answer.protocol,'requested_model':answer.model,'base_url_present':bool(answer.base_url),'timeout_seconds':answer.timeout_seconds,'configured_sdk_max_retries':answer.max_retries,'network_request_sent':False,'window_verified':False}

def prepare(root, output):
    root=Path(root).resolve(); output=Path(output).resolve()
    owned=['generation/inputs.jsonl','evaluation/l2-labels.json','evaluation/reference-build','input-manifest.json','entry-report.md']
    if any((output/n).exists() for n in owned): raise FileExistsError('prepare output already exists')
    audit_files(root,[{'path':k,'sha256':v} for k,v in PINNED.items()])
    delivery=read_json(root/EVIDENCE/'delivery-manifest-r01.json')
    if len(delivery['files'])!=734: raise ValueError('Evidence delivery manifest file count changed')
    audit=audit_files(root,delivery['files'])
    inputs=read_json(root/EVIDENCE/'stage80/input-manifest.json')
    for key in ['input_sha256','old_assets_sha256']:
        audit_files(root,[{'path':k,'sha256':v} for k,v in inputs[key].items()])
    frozen=inputs['input_sha256']
    def binding(suffix):
        hits=[k for k in frozen if k.replace('\\','/').endswith(suffix)]
        if len(hits)!=1: raise ValueError('ambiguous frozen input '+suffix)
        return hits[0]
    gold_path=binding('gold-r02.json'); gold=read_json(relpath(root,gold_path)); gold_sha=frozen[gold_path]
    intents={i['intent_id']:i for i in gold['intents']}
    if len(intents)!=80 or len(gold['intents'])!=80: raise ValueError('Gold intent identity not unique 80')
    queries={r['intent_id']:r['query'] for r,_,_ in read_lines(relpath(root,binding('queries.jsonl')))}
    if set(queries)!=set(intents): raise ValueError('query identity mismatch')
    rows=[r for r,_,_ in read_lines(root/EVIDENCE/'stage80/contexts.jsonl')]
    generated=[generation_row(r) for r in rows]; validate_cells(generated,intents)
    for r in generated:
        if r['query']!=queries[r['intent_id']] or r['query']!=intents[r['intent_id']]['query']: raise ValueError('query drift')
    scores=read_json(root/EVIDENCE/'stage80/scores-r01.json')['rows']
    mapped=[dict(r,arm=ARMS[r['configuration']]) for r in scores]; validate_cells(mapped,intents)
    source_scores={(r['intent_id'],r['arm']):r for r in mapped}
    labels=[]
    for row in generated:
        score=source_scores[(row['intent_id'],row['arm'])]
        if score['text_sha256']!=row['context_sha256']: raise ValueError('L2 context binding mismatch')
        labels.append({'cell_id':row['cell_id'],'intent_id':row['intent_id'],'arm':row['arm'],'context_sha256':row['context_sha256'],'sufficient':score['sufficient'],'question_type':score['question_type']})
    selection=read_json(root/EVIDENCE/'stage20/selection.json')
    ids=selection['intent_ids']
    if len(ids)!=20 or len(set(ids))!=20 or not set(ids)<=set(intents): raise ValueError('original20 identity mismatch')
    parent_path=binding('parent_chunks.jsonl'); parents=[]
    for chunk,start,end in read_lines(relpath(root,parent_path)):
        parents.append(dict(chunk,jsonl_byte_start=start,jsonl_byte_end=end,source_library_path=parent_path.replace('\\','/'),source_library_sha256=frozen[parent_path]))
    packets=[reference_packet(i,parents,gold_sha) for i in gold['intents']]
    # All validation precedes new writes.
    write_new_json(output/'evidence-sha-audit.json',audit)
    write_new_lines(output/'generation/inputs.jsonl',generated)
    write_new_json(output/'evaluation/l2-labels.json',{'rows':labels})
    write_new_json(output/'evaluation/selection20.json',selection)
    for packet in packets: write_new_json(output/'evaluation/reference-build'/f"{packet['intent_id']}.json",packet)
    write_new_json(output/'model-presence.json',model_presence(root))
    write_new_json(output/'input-manifest.json',{'schema_version':'pearl-answer-offline-input-v1','pinned_sha256':PINNED,'frozen_input_sha256':frozen,'intent_ids':sorted(intents),'original20':ids,'intent_n':80,'generation_cell_n':320,'reference_packet_n':80,'arms':list(ARMS.values()),'reference_status':'independent_build_pending','oracle_status':'not_built','prompt':PROMPT,'prompt_template_sha256':sha_text(PROMPT),'generation_sha256':sha_file(output/'generation/inputs.jsonl'),'l2_labels_sha256':sha_file(output/'evaluation/l2-labels.json'),'reference_packets_sha256':{p.name:sha_file(p) for p in sorted((output/'evaluation/reference-build').glob('*.json'))}})
    with (output/'entry-report.md').open('x',encoding='utf-8') as stream:
        stream.write('# PEARL Answer offline entry\n\n*Frozen-input extraction and isolation audit · status: current*\n\n80 unique intents, original 20, 320 exact generation inputs and 320 L2 bindings checked. 80 independent reference-building packets saved; reference and oracle remain pending. No retrieval, Evidence assembly or network calls.\n\nEvidence delivery audit: '+str(audit['checked'])+' files checked; '+str(audit['matched'])+' matched. Navigation exception: docs/README.md current hash differs from historical delivery snapshot, explicitly retained in evidence-sha-audit.json. All frozen scientific files match. Input manifest also checked all '+str(len(inputs['old_assets_sha256']))+' prior asset bindings.\n\nGeneration packets contain query, exact final context, uniform prompt and hashes only. Reference-building packets contain allowed requirements/atoms/groups and original frozen parent text of allowed sources, with source library SHA, source SHA, chunk text SHA and JSONL byte intervals; intervals identify serialized records, not PDF byte spans. They contain no historical reference answers, review notes, ranks, strategy, L2 labels or scores.\n\nTDD: initial 7 tests failed because prepare.py was absent; green evidence is recorded by the invoking session.\n')
    return {'intent_n':80,'generation_cell_n':320,'reference_packet_n':80,'audit_matched':audit['matched'],'audit_checked':audit['checked']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--root',default='.'); parser.add_argument('--output',default='outputs/pearl-answer-dev80-20261004-01'); args=parser.parse_args()
    print(json.dumps(prepare(args.root,args.output)))
