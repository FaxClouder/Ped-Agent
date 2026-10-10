"""Session 6B API judge client: deepseek-v4-pro, temperature 0, JSON output, per-packet exclusive records.

The key is read privately through the repository settings loader and never stored or printed.
Each job is (job_id, messages, out_path, meta). An existing out_path is a completed unit and is
never re-requested (resume after interruption). Technical retries: at most 2 per packet, and a
shared global budget. HTTP 402 (insufficient balance) stops all further remote calls.
"""
from __future__ import annotations
import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

JUDGE={'provider':'DeepSeek','base_url':'https://api.deepseek.com','protocol':'openai_compatible_chat_completions',
       'model':'deepseek-v4-pro','temperature':0,'response_format':{'type':'json_object'},
       'thinking':{'type':'disabled'},'max_tokens':8192,'timeout_seconds':300,'concurrency_max':4,
       'technical_retries_per_packet_max':2,'sdk_retries':0,'seed_sent':False,
       'thinking_note':'thinking disabled so that temperature=0 takes effect (provider docs: temperature has no effect in thinking mode)'}
# Official pricing page fetched 2026-10-07 (pricing-observed-r01.json); USD per 1M tokens.
PRICE={'off_peak':{'input_cache_hit':0.022,'input_cache_miss':0.66,'output':1.98},
       'peak':{'input_cache_hit':0.044,'input_cache_miss':1.32,'output':3.96}}
TECHNICAL_STATUS={408,409,425,429,500,502,503,504}


def now():return datetime.now(timezone.utc).isoformat()
def text_sha(s):return hashlib.sha256(s.encode('utf8')).hexdigest()
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def rule_tier(ts:datetime):
    """Published weekday peak windows; Chinese public holidays are off peak but are not modelled here."""
    if ts.weekday()<5 and (1<=ts.hour<4 or 6<=ts.hour<10):return 'peak'
    return 'off_peak'


def cost(usage):
    if not usage:return None
    hit=usage.get('prompt_cache_hit_tokens') or 0
    miss=usage.get('prompt_cache_miss_tokens')
    if miss is None:miss=(usage.get('prompt_tokens') or 0)-hit
    out=usage.get('completion_tokens') or 0
    return {tier:round((hit*p['input_cache_hit']+miss*p['input_cache_miss']+out*p['output'])/1e6,8) for tier,p in PRICE.items()}


class Stop(Exception):
    pass


class Budget:
    def __init__(self,retry_cap,call_cap):
        self.retry_cap,self.call_cap=retry_cap,call_cap;self.retries=0;self.calls=0;self.lock=threading.Lock();self.stopped=None
    def take_call(self):
        with self.lock:
            if self.stopped:raise Stop(self.stopped)
            if self.calls>=self.call_cap:self.stopped='call cap reached';raise Stop(self.stopped)
            self.calls+=1
    def take_retry(self):
        with self.lock:
            if self.retries>=self.retry_cap:return False
            self.retries+=1;return True
    def stop(self,reason):
        with self.lock:self.stopped=self.stopped or reason


def _key():
    from ped_research_agent.config import load_settings
    a=load_settings().answer
    if a.base_url.rstrip('/')!=JUDGE['base_url']:raise ValueError('configured provider base_url differs from frozen judge provider')
    return a.api_key.get_secret_value()


def request_body(messages):
    return {'model':JUDGE['model'],'messages':messages,'temperature':JUDGE['temperature'],'max_tokens':JUDGE['max_tokens'],
            'response_format':JUDGE['response_format'],'thinking':JUDGE['thinking'],'stream':False}


def run_one(job,client,key,budget,ledger,lock):
    job_id,messages,out_path,meta=job
    out_path=Path(out_path)
    if out_path.exists():return 'exists'
    body=request_body(messages);body_text=canon(body);attempts=[];parsed=None;content=None;raw=None;usage=None
    for number in range(1,2+JUDGE['technical_retries_per_packet_max']):
        if number>1 and not budget.take_retry():
            attempts.append({'number':number,'skipped':'global retry cap reached'});break
        budget.take_call();start=time.perf_counter();ts=datetime.now(timezone.utc);att={'number':number,'start_utc':ts.isoformat(),'rule_tier':rule_tier(ts)}
        try:
            r=client.post(JUDGE['base_url']+'/chat/completions',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
                          content=body_text.encode('utf8'),timeout=JUDGE['timeout_seconds'])
            att['latency_seconds']=time.perf_counter()-start;att['http_status']=r.status_code
            raw=r.text;att['response_sha256']=text_sha(raw)
            if r.status_code==402:
                att['error']='insufficient_balance';attempts.append(att);budget.stop('HTTP 402 insufficient balance');break
            if r.status_code in TECHNICAL_STATUS:
                att['error']=f'technical_http_{r.status_code}';attempts.append(att);continue
            if r.status_code!=200:
                att['error']=f'http_{r.status_code}';att['body_excerpt']=raw[:500];attempts.append(att);budget.stop(f'non-technical HTTP {r.status_code}');break
            data=r.json();usage=data.get('usage');att['usage']=usage;att['cost_usd']=cost(usage)
            choice=data['choices'][0];content=choice['message'].get('content') or ''
            att.update(response_id=data.get('id'),returned_model=data.get('model'),finish_reason=choice.get('finish_reason'),
                       system_fingerprint=data.get('system_fingerprint'),content_sha256=text_sha(content))
            if choice.get('finish_reason')!='stop':
                att['error']='technical_finish_'+str(choice.get('finish_reason'));attempts.append(att);continue
            try:parsed=json.loads(content)
            except json.JSONDecodeError as e:
                att['error']='technical_json_parse:'+str(e)[:100];attempts.append(att);parsed=None;continue
            if not isinstance(parsed,dict):
                att['error']='technical_json_not_object';attempts.append(att);parsed=None;continue
            att['error']=None;attempts.append(att);break
        except Stop:raise
        except Exception as e:  # connection, timeout and decoding failures are technical
            att['latency_seconds']=time.perf_counter()-start;att['error']='technical_'+type(e).__name__+':'+str(e)[:200];attempts.append(att)
    status='judged' if parsed is not None else 'judge_failed'
    record={'schema_version':'pearl-e6b-judge-record-v1','job_id':job_id,'status':status,'meta':meta,'judge':JUDGE,
            'request_sha256':text_sha(body_text),'messages_sha256':text_sha(canon(messages)),'request_body':body,
            'attempts':attempts,'final_response_raw':raw if status=='judged' else None,
            'final_response_sha256':text_sha(raw) if status=='judged' and raw is not None else None,
            'content':content if status=='judged' else None,'parsed':parsed,
            'usage_total':_sum_usage(attempts),'cost_usd_total':_sum_cost(attempts),
            'human_verified':False,'identity_note':'independent stateless request to the same API model; not a different model, not a human'}
    if status=='judged' or not budget.stopped:
        with out_path.open('x',encoding='utf8',newline='\n') as f:json.dump(record,f,ensure_ascii=False,indent=1);f.write('\n')
    with lock:
        with Path(ledger).open('a',encoding='utf8',newline='\n') as f:
            f.write(canon({'time_utc':now(),'job_id':job_id,'status':status,'attempts':len(attempts),'errors':[a.get('error') for a in attempts],
                           'usage':record['usage_total'],'cost_usd':record['cost_usd_total'],'out':out_path.name,
                           'saved':out_path.exists()})+'\n')
    return status


def _sum_usage(attempts):
    keys=('prompt_tokens','completion_tokens','prompt_cache_hit_tokens','prompt_cache_miss_tokens')
    total={k:0 for k in keys}
    for a in attempts:
        for k in keys:total[k]+=(a.get('usage') or {}).get(k) or 0
    return total


def _sum_cost(attempts):
    total={'off_peak':0.0,'peak':0.0,'rule_tier':0.0}
    for a in attempts:
        c=a.get('cost_usd')
        if c:
            total['off_peak']+=c['off_peak'];total['peak']+=c['peak'];total['rule_tier']+=c[a['rule_tier']]
    return {k:round(v,8) for k,v in total.items()}


def run_jobs(jobs,ledger,budget,concurrency=4):
    import httpx
    if concurrency>JUDGE['concurrency_max']:raise ValueError('concurrency above frozen maximum')
    key=_key();lock=threading.Lock();results={}
    with httpx.Client() as client, ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures={pool.submit(run_one,job,client,key,budget,ledger,lock):job[0] for job in jobs}
        for fut,job_id in futures.items():
            try:results[job_id]=fut.result()
            except Stop as e:results[job_id]='stopped:'+str(e)
    return results
