"""Session 6A close-out after the completed E5 run: offline summary, delivery package and chain status.

Makes no provider call of any kind (no generation, no balance probe): the 6A continuation forbids it.
summarize - counts, usage and source-bound cost estimate from the saved records and run ledger.
package   - delivery manifest over the run directory, code, documents and frozen external inputs.
verify    - delivery verification (artifact drift, unlisted files, links, independent E5 verification).
chain-status - exclusive chain status file for the requested attempt.
"""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from runtime import ROOT, sha, save_json, save_rows

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-14'
EXP=ROOT/'experiments/pearl-chunking-dev80-20261005'
CHAIN=ROOT/'outputs/pearl-chunking-chain-20261006'
L3OUT=ROOT/'outputs/pearl-answer-dev80-20261004-01'
REVISION='r01'
SELF={'delivery-manifest.json','delivery-verification-r01.json'}
CODE=['e5_generate.py','e5_verify.py','e5_closeout.py','e5_plan.py','capture_command.py','runtime.py']
DOCS=['outputs/pearl-chunking-dev80-20261006-14/handoff.md']
EXTERNAL=['experiments/pearl-answer-dev80-20261004/generate.py','experiments/pearl-answer-dev80-20261004/generator-config-r01.json',
          'outputs/pearl-chunking-chain-20261006/authorization-e5-r01.json','outputs/pearl-chunking-dev80-20261006-13/delivery-manifest.json',
          'outputs/pearl-chunking-dev80-20261006-13/e5-call-plan-r01.json','outputs/pearl-chunking-dev80-20261006-13/e5-cell-order-r01.jsonl',
          'outputs/pearl-chunking-dev80-20261006-13/e5-request-inputs-r01.jsonl','outputs/pearl-answer-dev80-20261004-01/provider-pricing-observed-r01.json']
PRICE_USD_PER_M={'off_peak':{'input_cache_hit':0.003,'input_cache_miss':0.15,'output':0.6},'peak':{'input_cache_hit':0.006,'input_cache_miss':0.3,'output':1.2}}

def load(p):return json.loads(Path(p).read_text('utf8'))
def jsonl(p):return [json.loads(l) for l in Path(p).read_text('utf8').splitlines() if l.strip()]
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def record_path(cell_id):return OUT/'generation'/(cell_id.replace(':','_')+'.json')

def summarize():
    manifest=load(OUT/'e5-run-manifest-r01.json');order=jsonl(ROOT/manifest['cell_order'])
    rows=[];tot=dict(prompt_tokens=0,prompt_cache_hit_tokens=0,prompt_cache_miss_tokens=0,completion_tokens=0);latency=[]
    for o in order:
        p=record_path(o['cell_id'])
        if not p.exists():rows.append(dict(cell_id=o['cell_id'],status='not_attempted',attempts=0,retries=0));continue
        r=load(p);u=(r.get('provider_response_metadata') or {}).get('token_usage') or {}
        for k in tot:tot[k]+=u.get(k,0) or 0
        if r.get('latency_seconds') is not None:latency.append(r['latency_seconds'])
        rows.append(dict(cell_id=o['cell_id'],configuration_id=o['configuration_id'],intent_id=o['intent_id'],replicate_id=o['replicate_id'],status=r['generation_status'],
            attempts=len(r['attempts']),retries=max(0,len(r['attempts'])-1),attempt_status=[a['status'] for a in r['attempts']],
            errors=[a.get('error_category') for a in r['attempts'] if a.get('error_category')],first_started_utc=r['attempts'][0]['started_at'] if r['attempts'] else None,
            latency_seconds=r.get('latency_seconds'),finish_reason=r['finish_reason'],returned_model=r.get('returned_model'),response_id=r.get('response_id'),
            prompt_tokens=u.get('prompt_tokens'),cache_hit_tokens=u.get('prompt_cache_hit_tokens'),cache_miss_tokens=u.get('prompt_cache_miss_tokens'),completion_tokens=u.get('completion_tokens'),
            request_sha256=r['request_sha256'],response_sha256=r['response_sha256'],record_sha256=r['record_sha256']))
    save_rows(OUT/f'generation-ledger-{REVISION}.jsonl',rows)
    est={k:round((tot['prompt_cache_hit_tokens']*p['input_cache_hit']+tot['prompt_cache_miss_tokens']*p['input_cache_miss']+tot['completion_tokens']*p['output'])/1e6,6) for k,p in PRICE_USD_PER_M.items()}
    by_config={}
    for r in rows:
        if r['status']=='not_attempted':continue
        c=by_config.setdefault(r['configuration_id'],dict(cells=0,returned=0,prompt_tokens=0,completion_tokens=0))
        c['cells']+=1;c['returned']+=r['status']=='returned';c['prompt_tokens']+=r['prompt_tokens'] or 0;c['completion_tokens']+=r['completion_tokens'] or 0
    ledger=jsonl(OUT/f'run-ledger-{REVISION}.jsonl');start=ledger[0]['time_utc'];end=ledger[-1]['time_utc']
    pre=load(OUT/'provider-probe-pre-r01.json')
    count=lambda s:sum(r['status']==s for r in rows)
    calls=sum(r['attempts'] for r in rows);retries=sum(r['retries'] for r in rows);cells_called=sum(1 for r in rows if r['attempts'])
    summary=dict(stage='E5 generation summary',session='6A',revision=REVISION,created_utc=datetime.now(timezone.utc).isoformat(),planned_cells=len(order),planned_provider_calls=720,
        returned=count('returned'),generation_failed=count('generation_failed'),not_attempted=count('not_attempted'),
        generation_calls=cells_called,provider_attempts=calls,retries=retries,retry_cap=144,shared_request_cells=0,
        nonreturned_cells=[r['cell_id'] for r in rows if r['status']!='returned'],
        finish_reasons={str(k):sum(r.get('finish_reason')==k for r in rows) for k in sorted({str(r.get('finish_reason')) for r in rows})},
        returned_models=sorted({str(r.get('returned_model')) for r in rows if r['status']=='returned'}),
        usage=tot,by_configuration=by_config,
        latency_seconds=dict(n=len(latency),total=round(sum(latency),3),mean=round(sum(latency)/len(latency),3) if latency else None,max=round(max(latency),3) if latency else None,
            note='per-call provider latency measured by the frozen generator; sequential run, concurrency 1'),
        run_window_utc=dict(start=start,end=end,note='2026-10-06 17:21-17:55 UTC = 2026-10-07 01:21-01:55 Beijing time (Wednesday)'),
        cost=dict(estimated_usd=est,pricing_record=rel(L3OUT/'provider-pricing-observed-r01.json'),
            pricing_note='source-bound estimate from the 2026-10-04 observed DeepSeek price table; the run was on a weekday, so the record\'s weekend off-peak basis does not establish which tier applied: report the off-peak/peak pair as bounds, not an invoice',
            balance_before_cny=float(pre['balance']['balance_infos'][0]['total_balance']),balance_after_cny=None,
            balance_note='post-run balance not probed: the 6A continuation forbids any provider call, including non-generating balance endpoints'),
        authorization=dict(record=rel(CHAIN/'authorization-e5-r01.json'),generation_max=720,retry_cap=144,used_generation_cells=cells_called,used_retries=retries,
            within=cells_called<=720 and retries<=144,remaining_generation=720-cells_called,remaining_retries=144-retries),
        ledger=rel(OUT/f'generation-ledger-{REVISION}.jsonl'),ledger_sha256=sha(OUT/f'generation-ledger-{REVISION}.jsonl'),scoring='not performed in 6A')
    save_json(OUT/f'generation-summary-{REVISION}.json',summary)
    print(json.dumps({k:summary[k] for k in ('returned','generation_failed','not_attempted','provider_attempts','retries','usage','cost')},ensure_ascii=False),flush=True)

def artifacts():
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in SELF and '__pycache__' not in p.parts]
    out={rel(p):sha(p) for p in files}
    out.update({rel(EXP/c):sha(EXP/c) for c in CODE})
    out.update({d:sha(ROOT/d) for d in DOCS+EXTERNAL})
    return out

def links(doc):
    bad=[];text=(ROOT/doc).read_text('utf8')
    for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)',text):
        if target.startswith(('http://','https://','mailto:')) or Path(target).name in SELF:continue
        if not ((ROOT/doc).parent/target).exists():bad.append(target)
    return bad

def package():
    target=OUT/'delivery-manifest.json'
    if target.exists():raise FileExistsError(target)
    a=artifacts();s=load(OUT/f'generation-summary-{REVISION}.json');v=load(OUT/f'verification-e5-{REVISION}.json')
    save_json(target,dict(stage='E5 generation',session='6A',status='verified',artifact_count=len(a),artifacts_sha256=a,
        run_manifest_sha256=sha(OUT/'e5-run-manifest-r01.json'),upstream_delivery_manifest_sha256=load(OUT/'e5-run-manifest-r01.json')['upstream']['delivery_manifest_sha256'],
        records=len(list((OUT/'generation').glob('*.json'))),returned=s['returned'],generation_failed=s['generation_failed'],not_attempted=s['not_attempted'],
        generation_calls=s['generation_calls'],provider_attempts=s['provider_attempts'],retries=s['retries'],judge_calls=0,usage=s['usage'],cost=s['cost'],
        summary_sha256=sha(OUT/f'generation-summary-{REVISION}.json'),verification_sha256=sha(OUT/f'verification-e5-{REVISION}.json'),verification_status=v['status'],
        scoring='not performed',generation_8k=False,E6_started=False,human_verified=False))
    print('packaged',len(a),flush=True)

def verify():
    target=OUT/'delivery-verification-r01.json'
    if target.exists():raise FileExistsError(target)
    m=load(OUT/'delivery-manifest.json')
    drift=[n for n,h in m['artifacts_sha256'].items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    unlisted=sorted(set(artifacts())-set(m['artifacts_sha256']))
    bad={d:links(d) for d in DOCS};bad={k:v for k,v in bad.items() if v}
    v=load(OUT/f'verification-e5-{REVISION}.json');s=load(OUT/f'generation-summary-{REVISION}.json')
    counts_ok=(m['records']==720 and s['returned']+s['generation_failed']+s['not_attempted']==720 and v['counts']['returned']==s['returned'] and s['authorization']['within'])
    ok=not drift and not unlisted and not bad and v['status']=='passed' and counts_ok and m['judge_calls']==0
    save_json(target,dict(status='passed' if ok else 'failed',manifest_sha256=sha(OUT/'delivery-manifest.json'),artifact_count=m['artifact_count'],artifact_drift=drift,
        unlisted_artifacts=unlisted,broken_links=bad,documents_link_checked=DOCS,independent_verification=v['status'],counts_consistent=counts_ok,
        generation_calls=s['generation_calls'],retries=s['retries'],judge_calls=0,scoring='not performed',E6_started=False,self_excluded=sorted(SELF)))
    print('delivery verification','passed' if ok else 'FAILED',drift[:3],unlisted[:3],bad,flush=True)
    return ok

def chain_status(name):
    target=CHAIN/name
    if target.exists():raise FileExistsError(target)
    dv=load(OUT/'delivery-verification-r01.json');s=load(OUT/f'generation-summary-{REVISION}.json')
    status='passed' if dv['status']=='passed' else 'failed'
    save_json(target,dict(stage='6A',status=status,reason=None if status=='passed' else 'delivery verification failed',run_dir=rel(OUT),handoff=rel(OUT/'handoff.md'),
        delivery_manifest=rel(OUT/'delivery-manifest.json'),delivery_manifest_sha256=sha(OUT/'delivery-manifest.json'),delivery_verification=rel(OUT/'delivery-verification-r01.json'),
        generation_calls=s['generation_calls'],judge_calls=0,retries=s['retries'],
        cost_summary=dict(provider_attempts=s['provider_attempts'],usage=s['usage'],estimated_usd=s['cost']['estimated_usd'],monetary_cost_note=s['cost']['pricing_note'],
            balance_before_cny=s['cost']['balance_before_cny'],balance_after_cny=None),
        notes=f"E5 r01 (attempt 1, separate window): {s['returned']}/720 returned, {s['generation_failed']} failed, {s['retries']} retries; deepseek-flash, 4K main budget. "
              "Attempt 3 (continuation) made no provider calls: verification, summary, handoff and delivery only. Not scored; no 8K; E6 not started. "
              "6B entry: outputs/pearl-chunking-dev80-20261006-14/handoff.md"))
    print('chain status',status,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('step',choices=['summarize','package','verify','chain-status']);p.add_argument('--status-name',default='status-6A-a3.json')
    a=p.parse_args()
    if a.step=='chain-status':chain_status(a.status_name)
    elif a.step=='verify':raise SystemExit(0 if verify() else 1)
    else:{'summarize':summarize,'package':package}[a.step]()
