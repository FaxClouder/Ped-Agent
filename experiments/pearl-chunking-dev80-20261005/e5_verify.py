"""Independent Session 6A verification: re-derive every E5 record from the frozen inputs without the
generation driver (own template copy, own hashing), and reconcile counts with the authorization ledger."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from runtime import ROOT, sha, save_json

TEMPLATE='''Answer the research question in English using only the supplied context.
State the requested findings and retain the relevant experimental conditions,
numerical values and units. For comparisons, explicitly explain the relationship
between the findings rather than listing unrelated facts. Use the supplied
source labels for citations where possible. Do not invent missing evidence.
If the context does not establish part of the answer, state that limitation.

Question:
{query}

Context:
{exact_saved_context}'''

def load(p):return json.loads(Path(p).read_text('utf8'))
def jsonl(p):return [json.loads(l) for l in Path(p).read_text('utf8').splitlines() if l.strip()]
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def h(v):return hashlib.sha256((v if isinstance(v,str) else canon(v)).encode('utf-8')).hexdigest()

def verify(out,revision):
    errors=[];add=errors.append
    m=load(out/'e5-run-manifest-r01.json');ms=sha(out/'e5-run-manifest-r01.json')
    plan=load(ROOT/m['upstream']['call_plan'])
    if sha(ROOT/m['upstream']['call_plan'])!=m['upstream']['call_plan_sha256']:add('call plan drift')
    if h(TEMPLATE)!=plan['prompt']['template_sha256']:add('independent template copy differs from frozen template')
    queries={q['intent_id']:q['query'] for q in jsonl(ROOT/plan['inputs']['queries'])}
    ctx={}
    for c in plan['inputs']['configurations']:
        if sha(ROOT/c['contexts'])!=c['contexts_sha256']:add('contexts drift '+c['configuration_id'])
        for r in jsonl(ROOT/c['contexts']):ctx[c['configuration_id'],r['intent_id']]=r['final']['serialized_context']
    spec={(r['configuration_id'],r['intent_id']):r for r in jsonl(ROOT/plan['inputs']['request_inputs'])}
    refs=[]
    for r in load(ROOT/m['generator']['prerequisite_gates']['reference_freeze']['path'].replace('reference-freeze-gate-r01.json','reference-freeze-r01.json'))['rows']:
        refs+=[r['reference_answer'],*r.get('target_definitions',{}).values(),*r.get('claim_definitions',{}).values()]
    refs=[t for t in refs if isinstance(t,str) and len(t)>=30]
    config=load(ROOT/m['generator']['config']);order=jsonl(ROOT/plan['interleaving']['cells_file'])
    counts=dict(cells=len(order),records=0,returned=0,failed=0,missing=0,attempts=0,retries=0,technical_failures=0,nonretryable_failures=0,reference_leaks=0,empty_answers=0,length_finish=0)
    starts=[];models=set()
    for o in order:
        p=out/'generation'/(o['cell_id'].replace(':','_')+'.json')
        if not p.exists():counts['missing']+=1;continue
        r=load(p);counts['records']+=1
        content=TEMPLATE.format(query=queries[o['intent_id']],exact_saved_context=ctx[o['configuration_id'],o['intent_id']])
        messages=[{'role':'user','content':content}];s=spec[o['configuration_id'],o['intent_id']]
        if r['record_sha256']!=h({k:v for k,v in r.items() if k!='record_sha256'}):add('record sha '+o['cell_id'])
        if (r['cell_id'],r['intent_id'],r['arm'])!=(o['cell_id'],o['intent_id'],o['configuration_id']):add('identity '+o['cell_id'])
        if r['request']!=content or r['messages']!=messages or h(content)!=o['request_sha256'] or r['request_sha256']!=s['request_sha256'] or h(messages)!=s['messages_sha256']:add('request '+o['cell_id'])
        if r['request_utf8_bytes']!=len(canon(messages).encode('utf-8')):add('recomputed bytes '+o['cell_id'])
        if r['context_sha256']!=s['context_sha256']:add('context '+o['cell_id'])
        if r['request_utf8_bytes']!=s['request_utf8_bytes'] or r['request_utf8_bytes']>config['provider_input_tokens']:add('bytes '+o['cell_id'])
        if any(t in content for t in refs):counts['reference_leaks']+=1
        if r['manifest_sha256']!=ms or r['config']!=config or r['config_sha256']!=h(config) or r['record_kind']!='real' or r['purpose']!='research':add('provenance '+o['cell_id'])
        if r['parameters']!={'max_tokens':2048,'temperature':0,'seed':None,'sdk_max_retries':0,'extra_body':{'thinking':{'type':'disabled'}}}:add('parameters '+o['cell_id'])
        a=r['attempts'];counts['attempts']+=len(a);counts['retries']+=max(0,len(a)-1)
        counts['technical_failures']+=sum(x['status']=='technical_failure' for x in a);counts['nonretryable_failures']+=sum(x['status']=='nonretryable_failure' for x in a)
        if len(a)>3 or any(x['status']!='technical_failure' for x in a[:-1]):add('retry chain '+o['cell_id'])
        if a:starts.append((a[0]['started_at'],o['cell_id']))
        if r['generation_status']=='returned':
            counts['returned']+=1;models.add(r.get('returned_model'))
            if h(r['raw_answer'])!=r['response_sha256'] or a[-1]['status']!='returned' or a[-1]['response_sha256']!=r['response_sha256']:add('answer sha '+o['cell_id'])
            if not (isinstance(r['raw_answer'],str) and r['raw_answer'].strip()):counts['empty_answers']+=1
            if r['finish_reason']=='length':counts['length_finish']+=1
            if r['usage'] is None:add('usage missing '+o['cell_id'])
        else:counts['failed']+=1
    seq=[c for _,c in sorted(starts)];expected=[o['cell_id'] for o in order if (out/'generation'/(o['cell_id'].replace(':','_')+'.json')).exists()]
    if seq!=expected:add('execution order differs from frozen interleaving')
    responses={}
    for o in order:
        p=out/'generation'/(o['cell_id'].replace(':','_')+'.json')
        if p.exists():
            r=load(p)
            if r.get('response_id'):responses.setdefault(r['response_id'],[]).append(o['cell_id'])
    dup=[v for v in responses.values() if len(v)>1]
    if dup:add(f'response id reused across cells: {dup[:3]}')
    if counts['reference_leaks']:add('reference text in requests')
    extra=sorted({p.name for p in (out/'generation').glob('*.json')}-{o['cell_id'].replace(':','_')+'.json' for o in order})
    if extra:add(f'unexpected records {extra[:3]}')
    cells_with_calls=sum(1 for o in order if (out/'generation'/(o['cell_id'].replace(':','_')+'.json')).exists())
    if cells_with_calls>720 or counts['retries']>144:add('authorization exceeded')
    by_request={}
    for o in order:by_request.setdefault(o['request_sha256'],set()).add(o['configuration_id'])
    shared=[k for k,v in by_request.items() if len(v)>1]
    if shared and plan['calls']['shared_request_cells']==0:add(f'identical requests across configurations not shared as planned: {len(shared)}')
    per_request={}
    for o in order:
        p=out/'generation'/(o['cell_id'].replace(':','_')+'.json')
        if p.exists():per_request.setdefault((o['configuration_id'],o['intent_id']),[]).append(load(p).get('response_id'))
    not_independent=[k for k,v in per_request.items() if len(v)!=3 or len(set(v))!=3 or None in v]
    if not_independent:add(f'replicates not three distinct real responses: {not_independent[:3]}')
    usage=dict(prompt_tokens=0,prompt_cache_hit_tokens=0,prompt_cache_miss_tokens=0,completion_tokens=0)
    for o in order:
        p=out/'generation'/(o['cell_id'].replace(':','_')+'.json')
        if p.exists():
            u=(load(p).get('provider_response_metadata') or {}).get('token_usage') or {}
            for k in usage:usage[k]+=u.get(k,0) or 0
    ledger=[json.loads(l) for l in (out/f'run-ledger-{revision}.jsonl').read_text('utf8').splitlines() if l.strip()]
    lcells={x['cell_id']:x for x in ledger if x.get('event')=='cell'}
    for o in order:
        p=out/'generation'/(o['cell_id'].replace(':','_')+'.json')
        if p.exists():
            r=load(p);x=lcells.get(o['cell_id'])
            if x is None or x['status']!=r['generation_status'] or x['attempts']!=len(r['attempts']) or x['usage']!=r['usage']:add('run ledger mismatch '+o['cell_id'])
    if [x['event'] for x in ledger if x['event'] in ('start','end')]!=['start','end'] or ledger[-1].get('stop_reason') is not None:add('run ledger start/end')
    summary=load(out/f'generation-summary-{revision}.json')
    if summary['usage']!=usage:add('summary usage mismatch')
    for k in ('returned','retries'):
        if summary[k]!=counts[k]:add('summary mismatch '+k)
    if summary['provider_attempts']!=counts['attempts']:add('summary attempts mismatch')
    result=dict(status='passed' if not errors else 'failed',revision=revision,manifest_sha256=ms,counts=counts,distinct_response_ids=len(responses),usage_recomputed=usage,identical_requests_across_configurations=len(shared),unique_requests=len(per_request),returned_models=sorted(map(str,models)),
        order_matches_frozen_interleaving=seq==expected,errors=errors[:50],error_count=len(errors),scoring='not performed',method='independent template copy and hashing; frozen inputs re-read from 5B/E3 outputs')
    save_json(out/f'verification-e5-{revision}.json',result);print(json.dumps({k:result[k] for k in ('status','counts','error_count')},ensure_ascii=False),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--revision',default='r01');a=p.parse_args()
    raise SystemExit(0 if verify(a.out.resolve(),a.revision)['status']=='passed' else 1)
