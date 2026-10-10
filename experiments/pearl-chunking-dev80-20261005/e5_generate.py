"""Session 6A: E5 real repeated answer generation with the frozen 5B call plan.

prepare  - verify the 5B delivery, rebuild every frozen request from query + saved 4K context,
           check identity/length/no Gold or reference text, bind gates, record availability.
run      - interleaved sequential generation through the frozen generate.run_cell (exclusive
           record per cell, no hidden retries); stops before the global retry cap could be exceeded.
summarize- counts, usage and cost ledger from the saved records (no scoring).
"""
from __future__ import annotations
import argparse
import asyncio
import importlib.util
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from runtime import ROOT, sha, save_json, save_rows, load_queries

S5B=ROOT/'outputs/pearl-chunking-dev80-20261006-13'
CHAIN=ROOT/'outputs/pearl-chunking-chain-20261006'
ANSWER=ROOT/'experiments/pearl-answer-dev80-20261004'
L3OUT=ROOT/'outputs/pearl-answer-dev80-20261004-01'
S5B_MANIFEST_SHA='0d40503211f806d36c92a0598063d73ffe66a84df22dcedaa0ecd92ab396fb99'
GATES={'provider_capabilities':L3OUT/'provider-capabilities-r01.json','preflight':L3OUT/'preflight-gate-r01.json',
       'reference_freeze':L3OUT/'reference-freeze-gate-r01.json','calibration':L3OUT/'calibration/calibration-gate-r01.json'}
STOP_AFTER_CONSECUTIVE_FAILURES=3

def load(p):return json.loads(Path(p).read_text('utf8'))
def jsonl(p):
    with Path(p).open(encoding='utf8') as f:return [json.loads(l) for l in f if l.strip()]
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()

def generator():
    spec=importlib.util.spec_from_file_location('_pearl_answer_generate_frozen',ANSWER/'generate.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def provider_probe():
    """Non-generating availability/balance probe; the key is read privately and never stored."""
    import httpx
    from ped_research_agent.config import load_settings
    a=load_settings().answer;h={'Authorization':'Bearer '+a.api_key.get_secret_value()}
    models=httpx.get(a.base_url+'/models',headers=h,timeout=30);balance=httpx.get(a.base_url+'/user/balance',headers=h,timeout=30)
    return dict(time_utc=now(),configured=dict(model=a.model,protocol=a.protocol,base_url=a.base_url),models_status=models.status_code,
        models=[{k:m.get(k) for k in ('id','name','context_window','max_output_tokens')} for m in models.json().get('data',[])],
        balance_status=balance.status_code,balance=balance.json() if balance.status_code==200 else None)

def reference_texts():
    texts=[]
    for r in load(L3OUT/'reference-freeze-r01.json')['rows']:
        texts.append(r['reference_answer']);texts+=list(r.get('target_definitions',{}).values())+list(r.get('claim_definitions',{}).values())
    return [t for t in texts if isinstance(t,str) and len(t)>=30]

def prepare(out):
    if out.exists() and any(not x.name.startswith('command-prepare-') for x in out.iterdir()):raise FileExistsError(out)
    if sha(S5B/'delivery-manifest.json')!=S5B_MANIFEST_SHA:raise ValueError('5B delivery manifest drift')
    manifest=load(S5B/'delivery-manifest.json');drift=[p for p,h in manifest['artifacts_sha256'].items() if sha(ROOT/p)!=h]
    if drift or load(S5B/'delivery-verification-r01.json')['status']!='passed':raise ValueError(f'5B delivery drift: {drift[:5]}')
    plan=load(S5B/'e5-call-plan-r01.json');freeze=load(S5B/'final-config-freeze-r01.json');evaluation=load(S5B/'evaluation-versions-r01.json')
    if sha(S5B/'e5-call-plan-r01.json')!=manifest['e5_call_plan_sha256'] or plan['status']!='frozen' or not freeze['e5_allowed']:raise ValueError('call plan not frozen')
    auth=CHAIN/'authorization-e5-r01.json'
    if sha(auth)!=plan['authorization']['record_sha256']:raise ValueError('authorization record drift')
    if plan['calls']['planned_provider_calls']>720 or plan['retries']['global_retry_cap']!=144:raise ValueError('plan exceeds authorization')
    gen=generator();config=gen.validate_config(load(ANSWER/'generator-config-r01.json'))
    checks={'generate_py':(sha(ANSWER/'generate.py'),plan['model']['generate_py_sha256']),'generator_config':(sha(ANSWER/'generator-config-r01.json'),plan['model']['generator_config_sha256']),
        'prompt_template':(gen.sha(gen.PROMPT),plan['prompt']['template_sha256']),'request_inputs':(sha(S5B/'e5-request-inputs-r01.jsonl'),plan['inputs']['request_inputs_sha256']),
        'queries':(sha(S5B/'queries.jsonl'),plan['inputs']['queries_sha256']),'cell_order':(sha(S5B/'e5-cell-order-r01.jsonl'),plan['interleaving']['cells_file_sha256'])}
    for c in plan['inputs']['configurations']:checks['contexts:'+c['configuration_id']]=(sha(ROOT/c['contexts']),c['contexts_sha256'])
    for k,v in evaluation['layer3'].items():
        if k.endswith('_sha256') and k[:-7] in evaluation['layer3']:checks['layer3:'+k]=(sha(ROOT/evaluation['layer3'][k[:-7]]),v)
    for k,v in evaluation['layer4'].items():
        if k.endswith('_sha256') and k[:-7] in evaluation['layer4']:checks['layer4:'+k]=(sha(ROOT/evaluation['layer4'][k[:-7]]),v)
    bad={k:v for k,v in checks.items() if v[0]!=v[1]}
    if bad:raise ValueError(f'frozen identity mismatch: {bad}')
    if (config['model'],config['protocol'],config['base_url'])!=(plan['model']['model'],plan['model']['protocol'],plan['model']['base_url']):raise ValueError('model/provider differs from plan')
    probe=provider_probe()
    if probe['configured']!=dict(model=plan['model']['model'],protocol=plan['model']['protocol'],base_url=plan['model']['base_url']):raise ValueError('configured direct model differs from plan')
    if probe['models_status']!=200 or plan['model']['model'] not in {m['id'] for m in probe['models']}:raise ValueError('model unavailable')
    queries={q['intent_id']:q['query'] for q in load_queries(S5B/'queries.jsonl',80)}
    inputs={(r['configuration_id'],r['intent_id']):r for r in jsonl(S5B/'e5-request-inputs-r01.jsonl')}
    refs=reference_texts();cells=[];bound=config['provider_input_tokens']
    for c in plan['inputs']['configurations']:
        for row in jsonl(ROOT/c['contexts']):
            spec=inputs[c['configuration_id'],row['intent_id']];text=row['final']['serialized_context']
            cell=dict(intent_id=row['intent_id'],arm=c['configuration_id'],query=queries[row['intent_id']],context=text,context_sha256=gen.sha(text),request_sha256=spec['request_sha256'])
            messages=gen.build_request(dict(cell,cell_id='x'));nbytes=len(gen.canonical(messages).encode('utf-8'))
            if (row['context_id'],gen.sha(text),gen.sha(messages),nbytes)!=(spec['context_id'],spec['context_sha256'],spec['messages_sha256'],spec['request_utf8_bytes']):raise ValueError('request rebuild mismatch')
            if nbytes>bound or row['final']['token_count']>4096:raise ValueError('request exceeds admission bound')
            if any(t in messages[0]['content'] for t in refs):raise ValueError('reference text inside generation input')
            cells.append(dict(cell,config_id=c['config_id'],context_id=row['context_id'],request_utf8_bytes=nbytes,messages_sha256=spec['messages_sha256']))
    if len(cells)!=240:raise ValueError('expected 240 unique (configuration, intent) requests')
    order=jsonl(S5B/'e5-cell-order-r01.jsonl')
    if len(order)!=720 or len({o['cell_id'] for o in order})!=720 or not all(o['provider_call'] for o in order):raise ValueError('cell order')
    out.mkdir(parents=True,exist_ok=True)
    save_rows(out/'e5-cells-r01.jsonl',cells)
    gates={k:dict(path=rel(p),sha256=sha(p)) for k,p in GATES.items()}
    save_json(out/'provider-probe-pre-r01.json',dict(probe,purpose='availability and balance before E5; non-generating endpoints, not billed',secrets='not recorded'))
    run=dict(stage='E5 generation run manifest',session='6A',status='frozen_before_calls',created_utc=now(),
        upstream=dict(delivery_manifest=rel(S5B/'delivery-manifest.json'),delivery_manifest_sha256=S5B_MANIFEST_SHA,artifacts_rechecked=len(manifest['artifacts_sha256']),drift=0,
            call_plan=rel(S5B/'e5-call-plan-r01.json'),call_plan_sha256=sha(S5B/'e5-call-plan-r01.json'),final_freeze=rel(S5B/'final-config-freeze-r01.json'),final_freeze_sha256=sha(S5B/'final-config-freeze-r01.json'),
            evaluation_versions=rel(S5B/'evaluation-versions-r01.json'),evaluation_versions_sha256=sha(S5B/'evaluation-versions-r01.json'),identity_checks={k:v[0] for k,v in checks.items()}),
        authorization=dict(record=rel(auth),sha256=sha(auth),generation_max=720,global_retry_cap=144),
        generator=dict(generate_py=rel(ANSWER/'generate.py'),generate_py_sha256=sha(ANSWER/'generate.py'),config=rel(ANSWER/'generator-config-r01.json'),config_sha256=gen.sha(config),
            prerequisite_gates=gates,gate_note='gates required by the frozen run_cell; same generator config SHA as the historical Layer 3 run'),
        cells=rel(out/'e5-cells-r01.jsonl'),cells_sha256=sha(out/'e5-cells-r01.jsonl'),cell_order=rel(S5B/'e5-cell-order-r01.jsonl'),cell_order_sha256=sha(S5B/'e5-cell-order-r01.jsonl'),
        checks=dict(unique_requests=len(cells),max_request_utf8_bytes=max(c['request_utf8_bytes'] for c in cells),admission_bound_utf8_bytes=bound,reference_strings_checked=len(refs),reference_in_request=0,
            fields='query + exact saved 4K final context only'),
        execution=dict(concurrency=1,stop_after_consecutive_failures=STOP_AFTER_CONSECUTIVE_FAILURES,retry_rule='before each cell require used_retries + 2 <= 144'),
        probe=rel(out/'provider-probe-pre-r01.json'))
    save_json(out/'e5-run-manifest-r01.json',run)
    print(json.dumps(dict(prepared=rel(out),unique_requests=len(cells),cells=len(order),max_bytes=run['checks']['max_request_utf8_bytes'],balance=probe['balance']),ensure_ascii=False),flush=True)

def retries_of(record):return max(0,len(record['attempts'])-1)

async def run(out,revision):
    gen=generator();manifest_path=out/'e5-run-manifest-r01.json';manifest=load(manifest_path);manifest_sha=sha(manifest_path)
    if sha(ROOT/manifest['cells'])!=manifest['cells_sha256'] or sha(ROOT/manifest['cell_order'])!=manifest['cell_order_sha256']:raise ValueError('cells drift')
    if sha(ROOT/manifest['generator']['generate_py'])!=manifest['generator']['generate_py_sha256']:raise ValueError('generator drift')
    config=gen.validate_config(load(ROOT/manifest['generator']['config']))
    if gen.sha(config)!=manifest['generator']['config_sha256']:raise ValueError('config drift')
    prerequisites={k:dict(path=str(ROOT/v['path']),sha256=v['sha256']) for k,v in manifest['generator']['prerequisite_gates'].items()}
    cells={(c['arm'],c['intent_id']):c for c in jsonl(ROOT/manifest['cells'])};order=jsonl(ROOT/manifest['cell_order'])
    dest=out/'generation';dest.mkdir(exist_ok=True);ledger=out/f'run-ledger-{revision}.jsonl'
    with ledger.open('x',encoding='utf8',newline='\n') as log:
        def note(**row):log.write(json.dumps(dict(time_utc=now(),**row),ensure_ascii=False,sort_keys=True)+'\n');log.flush();print(json.dumps(row,ensure_ascii=False),flush=True)
        existing={p.stem for p in dest.glob('*.json')}
        used=sum(retries_of(load(p)) for p in dest.glob('*.json'));consecutive=0;stop=None
        note(event='start',revision=revision,manifest_sha256=manifest_sha,existing_records=len(existing),used_retries=used)
        for n,o in enumerate(order,1):
            stem=o['cell_id'].replace(':','_')
            if stem in existing:note(event='skip_existing',cell_id=o['cell_id']);continue
            if used+2>manifest['authorization']['global_retry_cap']:stop='global retry cap could be exceeded';break
            c=cells[o['configuration_id'],o['intent_id']]
            if c['request_sha256']!=o['request_sha256']:raise ValueError('order/request mismatch')
            if len(gen.canonical(gen.build_request(dict(cell_id='x',query=c['query'],context=c['context']))).encode('utf-8'))>config['provider_input_tokens']:raise ValueError('request bound')
            cell=dict(cell_id=o['cell_id'],intent_id=c['intent_id'],arm=c['arm'],query=c['query'],context=c['context'],context_sha256=c['context_sha256'],request_sha256=c['request_sha256'])
            try:record=await gen.run_cell(cell,config,manifest_sha,dest,prerequisites=prerequisites)
            except ValueError as exc:note(event='cell_error',cell_id=o['cell_id'],error=str(exc));stop='client construction failure';break
            used+=retries_of(record)
            consecutive=0 if record['generation_status']=='returned' else consecutive+1
            note(event='cell',n=n,cell_id=o['cell_id'],status=record['generation_status'],attempts=len(record['attempts']),used_retries=used,
                 errors=[a.get('error_category') for a in record['attempts'] if a.get('error_category')],usage=record['usage'],finish_reason=record['finish_reason'])
            if consecutive>=STOP_AFTER_CONSECUTIVE_FAILURES:stop=f'{consecutive} consecutive failed cells';break
        note(event='end',revision=revision,stop_reason=stop,records=len(list(dest.glob('*.json'))),used_retries=used)

PRICE_USD_PER_M={'off_peak':{'input_cache_hit':0.003,'input_cache_miss':0.15,'output':0.6},'peak':{'input_cache_hit':0.006,'input_cache_miss':0.3,'output':1.2}}

def summarize(out,revision):
    manifest=load(out/'e5-run-manifest-r01.json');order=jsonl(ROOT/manifest['cell_order']);dest=out/'generation'
    records={o['cell_id']:load(dest/(o['cell_id'].replace(':','_')+'.json')) for o in order if (dest/(o['cell_id'].replace(':','_')+'.json')).exists()}
    rows=[];tot=dict(prompt=0,hit=0,miss=0,completion=0)
    for o in order:
        r=records.get(o['cell_id'])
        if r is None:rows.append(dict(cell_id=o['cell_id'],status='not_attempted'));continue
        u=(r.get('provider_response_metadata') or {}).get('token_usage') or {}
        hit=u.get('prompt_cache_hit_tokens',0) or 0;miss=u.get('prompt_cache_miss_tokens',0) or 0;comp=u.get('completion_tokens',0) or 0
        tot['prompt']+=u.get('prompt_tokens',0) or 0;tot['hit']+=hit;tot['miss']+=miss;tot['completion']+=comp
        rows.append(dict(cell_id=o['cell_id'],configuration_id=o['configuration_id'],intent_id=o['intent_id'],replicate_id=o['replicate_id'],status=r['generation_status'],attempts=len(r['attempts']),
            retries=retries_of(r),attempt_status=[a['status'] for a in r['attempts']],errors=[a.get('error_category') for a in r['attempts'] if a.get('error_category')],
            first_started_utc=r['attempts'][0]['started_at'] if r['attempts'] else None,latency_seconds=r.get('latency_seconds'),finish_reason=r['finish_reason'],returned_model=r.get('returned_model'),
            response_id=r.get('response_id'),prompt_tokens=u.get('prompt_tokens'),cache_hit_tokens=hit,cache_miss_tokens=miss,completion_tokens=comp,
            request_sha256=r['request_sha256'],response_sha256=r['response_sha256'],record_sha256=r['record_sha256']))
    save_rows(out/f'generation-ledger-{revision}.jsonl',rows)
    est={k:round((tot['hit']*p['input_cache_hit']+tot['miss']*p['input_cache_miss']+tot['completion']*p['output'])/1e6,6) for k,p in PRICE_USD_PER_M.items()}
    probe_post=provider_probe();save_json(out/f'provider-probe-post-{revision}.json',dict(probe_post,purpose='balance after E5; non-generating endpoints',secrets='not recorded'))
    pre=load(out/'provider-probe-pre-r01.json')
    def bal(p):
        try:return float(p['balance']['balance_infos'][0]['total_balance'])
        except Exception:return None
    b0,b1=bal(pre),bal(probe_post)
    status=lambda s:sum(r['status']==s for r in rows)
    calls=sum(r.get('attempts',0) for r in rows);retries=sum(r.get('retries',0) for r in rows)
    summary=dict(stage='E5 generation summary',session='6A',revision=revision,created_utc=now(),planned_cells=len(order),planned_provider_calls=720,
        returned=status('returned'),generation_failed=status('generation_failed'),not_attempted=status('not_attempted'),
        generation_calls=sum(1 for r in rows if r.get('attempts')),provider_attempts=calls,retries=retries,retry_cap=144,shared_request_cells=0,
        nonreturned_cells=[r['cell_id'] for r in rows if r['status']!='returned'],finish_reasons={k:sum(r.get('finish_reason')==k for r in rows) for k in {r.get('finish_reason') for r in rows}},
        returned_models=sorted({str(r.get('returned_model')) for r in rows if r['status']=='returned'}),
        usage=dict(prompt_tokens=tot['prompt'],prompt_cache_hit_tokens=tot['hit'],prompt_cache_miss_tokens=tot['miss'],completion_tokens=tot['completion']),
        cost=dict(estimated_usd=est,pricing_record=rel(L3OUT/'provider-pricing-observed-r01.json'),pricing_note='source-bound estimate from the 2026-10-04 observed DeepSeek price table; peak/off-peak bounds, not an invoice',
            balance_before_cny=b0,balance_after_cny=b1,balance_delta_cny=None if b0 is None or b1 is None else round(b0-b1,4),
            balance_note='account balance difference over the run window; may include any other use of the same key in that window'),
        authorization=dict(generation_max=720,within=sum(1 for r in rows if r.get('attempts'))<=720 and retries<=144),
        ledger=rel(out/f'generation-ledger-{revision}.jsonl'),scoring='not performed in 6A')
    save_json(out/f'generation-summary-{revision}.json',summary)
    print(json.dumps({k:summary[k] for k in ('returned','generation_failed','not_attempted','provider_attempts','retries','usage','cost')},ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('step',choices=['prepare','run','summarize']);p.add_argument('--out',type=Path,required=True);p.add_argument('--revision',default='r01')
    a=p.parse_args();out=a.out.resolve()
    if a.step=='prepare':prepare(out)
    elif a.step=='run':asyncio.run(run(out,a.revision))
    else:summarize(out,a.revision)
