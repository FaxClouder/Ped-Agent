"""Session 6B judge calibration of deepseek-v4-pro on the frozen historical Layer 3 / Layer 4 anchors.

prepare - freeze the judge configuration, prompt assembly and comparison rules before any call
run     - judge the 40 Layer 3 and 160 Layer 4 anchor packets (judge never sees expected labels)
compare - program comparison against the frozen expected labels and original thresholds
Thresholds are the original ones: Layer 3 AC exact and claim micro agreement >= 0.90 on the 40
resolved anchors plus all five sentinels; Layer 4 each metric >= 0.95 plus all eight sentinels
(the frozen compare_calibration.py is imported unchanged).
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from runtime import ROOT, EXP, sha, save_json
import e6b_judge as J
import e6b_prompts as P

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-15'
CAL=OUT/'calibration'
L3CAL=ROOT/'outputs/pearl-answer-dev80-20261004-01/calibration'
L4CAL=ROOT/'outputs/pearl-layer4-dev80-20261004-01/calibration'
TASKS=('answerability','grounding','factuality','behavior')
CAL_CALL_CAP=300


def load(p):return json.loads(Path(p).read_text(encoding='utf8'))


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def jobs(revision):
    rows=[]
    for packet in load(L3CAL/'judge-blind-packets-r01.json')['rows']:
        rows.append((f'L3-{packet["packet_id"]}',P.layer3_messages(packet),CAL/f'judge-{revision}/layer3/{packet["packet_id"]}.json',
                     {'layer':'layer3','packet_id':packet['packet_id'],'packet_sha256':J.text_sha(J.canon(packet))}))
    for task in TASKS:
        for path in sorted((L4CAL/'judge-packets'/task).glob('cal-*.json')):
            packet=load(path)
            rows.append((f'L4-{task}-{path.stem}',P.layer4_messages(packet,task),CAL/f'judge-{revision}/layer4/{task}/{path.stem}.json',
                         {'layer':'layer4','task':task,'anchor_id':path.stem,'packet_path':path.relative_to(ROOT).as_posix(),'packet_sha256':sha(path)}))
    return rows


def prepare(revision):
    CAL.mkdir(parents=True,exist_ok=True)
    rows=jobs(revision)
    code={f:sha(EXP/f) for f in ('e6b_judge.py','e6b_prompts.py','e6b_calibrate.py','runtime.py')}
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in (P.L3_PROMPT,P.L3_RUBRIC,P.L4_PROMPT,P.L4_RUBRIC,P.L4_ADDENDUM,
            L3CAL/'judge-blind-packets-r01.json',L3CAL/'expected-freeze-r01.json',L4CAL/'expected-r01.json',
            ROOT/'experiments/pearl-layer4-dev80-20261004/compare_calibration.py',ROOT/'experiments/pearl-answer-dev80-20261004/score.py')}
    save_json(CAL/f'calibration-plan-{revision}.json',{
        'status':'frozen_before_calls','revision':revision,'judge':J.JUDGE,'price_usd_per_million':J.PRICE,'harness_version':P.HARNESS_VERSION,
        'calls_planned':len(rows),'call_cap':CAL_CALL_CAP,'retries':'counted inside the calibration call cap; per packet max 2',
        'packets':[{'job_id':j,'messages_sha256':J.text_sha(J.canon(m)),'out':o.relative_to(ROOT).as_posix(),**meta} for j,m,o,meta in rows],
        'system_prompt_sha256':{'layer3':J.text_sha(rows[0][1][0]['content']),
                                **{t:J.text_sha(next(r for r in rows if r[3].get('task')==t)[1][0]['content']) for t in TASKS}},
        'judge_reads_expected':False,'code_sha256':code,'frozen_inputs_sha256':frozen,
        'thresholds':{'layer3':{'resolved_anchors':40,'ac_exact_agreement_min':0.9,'claim_micro_agreement_min':0.9,'sentinels':'all 5 pass',
                                'source':'docs/superpowers/plans/2026-10-04-pearl-answer-next-session.md stage B; generate.py calibration gate'},
                      'layer4':{'each_metric_min':0.95,'sentinels':'all 8 pass','source':'experiments/pearl-layer4-dev80-20261004/protocol.md; compare_calibration.py'}},
        'layer3_comparison_rules':{'AC':'frozen score.py score_cell on judge decision vs stored expected AC (expected also recomputed)',
                                   'claims':'per claim ID in expected decision: judge label identical',
                                   'sentinel_pass':'AC match and every claim label of that anchor identical (conservative)',
                                   'strata':'reported separately, not a separate gate'},
        'layer4_comparison':'frozen compare_calibration.compare unchanged; offsets located mechanically from verbatim quotes (e6b_prompts.locate_grounding)',
        'on_failure':'write blocked; no threshold, rubric or prompt change; no research packets'})
    print(json.dumps({'planned':len(rows)}))


def run(revision):
    plan=load(CAL/f'calibration-plan-{revision}.json')
    rows=jobs(revision)
    if [J.text_sha(J.canon(m)) for _,m,_,_ in rows]!=[p['messages_sha256'] for p in plan['packets']]:raise ValueError('prompt drift after freeze')
    for _,_,o,_ in rows:o.parent.mkdir(parents=True,exist_ok=True)
    done=sum(o.exists() for _,_,o,_ in rows)
    prior=0
    ledger=CAL/f'judge-ledger-{revision}.jsonl'
    if ledger.exists():prior=sum(len(json.loads(l)['errors']) for l in ledger.read_text(encoding='utf8').splitlines() if l.strip())
    budget=J.Budget(retry_cap=CAL_CALL_CAP,call_cap=CAL_CALL_CAP-prior)
    result=J.run_jobs([r for r in rows if not r[2].exists()],ledger,budget,concurrency=4)
    counts=defaultdict(int)
    for v in result.values():counts[v]+=1
    print(json.dumps({'already_done':done,'results':counts,'calls_this_run':budget.calls,'retries_this_run':budget.retries,'stopped':budget.stopped}))


def compare(revision,out_name):
    score=module('l3score',ROOT/'experiments/pearl-answer-dev80-20261004/score.py')
    comp=module('l4compare',ROOT/'experiments/pearl-layer4-dev80-20261004/compare_calibration.py')
    expected=load(L3CAL/'expected-freeze-r01.json')['rows']
    rows=[];strata=defaultdict(lambda:{'N':0,'AC_matches':0,'claims_matched':0,'claim_N':0});sentinels=[];failed=[]
    for e in expected:
        path=CAL/f'judge-{revision}/layer3/{e["anchor_id"]}.json'
        rec=load(path) if path.exists() else None
        ref=dict(e['reference'],stratum=e['stratum'])
        exp_ac=score.score_cell(ref,{'intent_id':e['anchor_id'],'arm':'cal','generation_status':'returned','l2_sufficient':'unknown','decision':e['decision']})['ac']
        if exp_ac!=e['metrics']['ac']:raise ValueError('expected AC recomputation mismatch')
        decision=(rec or {}).get('parsed',{}) or {}
        decision=decision.get('decision') if isinstance(decision.get('decision'),dict) else None
        try:judge_ac=score.score_cell(ref,{'intent_id':e['anchor_id'],'arm':'cal','generation_status':'returned','l2_sufficient':'unknown','decision':decision})['ac'] if decision else 'no_decision'
        except ValueError as err:judge_ac=f'invalid:{err}'
        claims=e['decision']['claims'];matched=sum((decision or {}).get('claims',{}).get(k)==v for k,v in claims.items())
        s=strata[e['stratum']];s['N']+=1;s['AC_matches']+=int(judge_ac==exp_ac);s['claims_matched']+=matched;s['claim_N']+=len(claims)
        row={'anchor_id':e['anchor_id'],'stratum':e['stratum'],'expected_AC':exp_ac,'judge_AC':judge_ac,'AC_match':judge_ac==exp_ac,
             'claims_matched':matched,'claim_n':len(claims),'record_sha256':sha(path) if rec else None}
        rows.append(row)
        if not row['AC_match'] or matched!=len(claims):failed.append(row)
        if e.get('sentinel'):sentinels.append({'anchor_id':e['anchor_id'],'sentinel':e['sentinel'],'passed':row['AC_match'] and matched==len(claims)})
    n=len(rows);ac=sum(r['AC_match'] for r in rows)/n;cm=sum(r['claims_matched'] for r in rows)/sum(r['claim_n'] for r in rows)
    l3={'resolved_anchors':n,'ac_exact_agreement':ac,'claim_micro_agreement':cm,'claims_matched':sum(r['claims_matched'] for r in rows),
        'claim_N':sum(r['claim_n'] for r in rows),'strata':dict(strata),'sentinels':sentinels,'sentinels_passed':len(sentinels)==5 and all(s['passed'] for s in sentinels),
        'rows':rows,'disagreements':failed}
    l3['passed']=n==40 and ac>=.9 and cm>=.9 and l3['sentinels_passed']
    # Layer 4: locate offsets mechanically, then the frozen comparer.
    l4exp=load(L4CAL/'expected-r01.json')['expected'];results={};located={}
    for e in l4exp:
        ident=e['anchor_id'];results[ident]={}
        for task in TASKS:
            path=CAL/f'judge-{revision}/layer4/{task}/{ident}.json'
            if not path.exists():continue
            rec=load(path);parsed=rec.get('parsed')
            if not isinstance(parsed,dict):continue
            packet=load(L4CAL/'judge-packets'/task/f'{ident}.json')
            if task=='grounding':parsed=P.locate_grounding(parsed,packet['raw_answer']);located[ident]=parsed['location_problems']
            if task=='behavior':parsed=P.normalize_behavior(parsed)
            parsed['anchor_id']=ident  # identity is bound by the harness from the packet file, not trusted from model text
            results[ident][task]=parsed
    l4=comp.compare(l4exp,results);l4['location_problems']={k:v for k,v in located.items() if v}
    status='passed' if l3['passed'] and l4['status']=='passed' else 'failed'
    usage=defaultdict(int);costs=defaultdict(float);calls=0;retries=0
    for p in sorted((CAL/f'judge-{revision}').rglob('*.json')):
        rec=load(p);calls+=len([a for a in rec['attempts'] if 'skipped' not in a]);retries+=max(0,len(rec['attempts'])-1)
        for k,v in rec['usage_total'].items():usage[k]+=v
        for k,v in rec['cost_usd_total'].items():costs[k]+=v
    report={'status':status,'revision':revision,'judge_model':J.JUDGE['model'],'layer3':l3,'layer4':l4,
            'calls':calls,'retries':retries,'usage':dict(usage),'cost_usd':{k:round(v,6) for k,v in costs.items()},
            'plan_sha256':sha(CAL/f'calibration-plan-{revision}.json'),
            'note':'program comparison against frozen expected labels; the judge never received expected labels; thresholds unchanged'}
    save_json(CAL/out_name,report)
    print(json.dumps({'status':status,'L3':{k:l3[k] for k in ('ac_exact_agreement','claim_micro_agreement','sentinels_passed','passed')},
                      'L4':{k:v['agreement'] for k,v in l4['metrics'].items()},'L4_status':l4['status'],
                      'L4_sentinels':[s['passed'] for s in l4['sentinels']],'calls':calls,'cost':report['cost_usd']}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['prepare','run','compare']);ap.add_argument('--revision',default='r01')
    ap.add_argument('--out',default=None);a=ap.parse_args()
    if a.cmd=='prepare':prepare(a.revision)
    elif a.cmd=='run':run(a.revision)
    else:compare(a.revision,a.out or f'calibration-comparison-{a.revision}.json')
