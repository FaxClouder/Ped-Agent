"""Saved E3 paired contrasts, unknown bounds, frozen choice and factual cases."""
import argparse
import collections
import csv
import json
import random
from pathlib import Path
import numpy as np
from runtime import ROOT, sha, save_json, save_rows
from e3 import rows,load,CONFIGS,PANELS,choose_recovery
from e1_closeout import exact_mcnemar,holm

def robust_choice(table):
    order=sorted(table,key=lambda r:(-r['yes'],r['mean_seconds'],r['strategy']))
    best=order[0];tie=lambda r:(r['mean_seconds'],r['strategy'])
    threats=[r['strategy'] for r in order[1:] if r['yes']+r['unknown']>best['yes'] or (r['yes']+r['unknown']==best['yes'] and tie(r)<tie(best))]
    result=dict(status='pending_review' if threats else 'frozen',selected=None if threats else best['strategy'],threats=threats,order=[r['strategy'] for r in order])
    result['rule']='4K confirmed CGC descending, comparable cold-reference mean seconds for ties, strategy id; freeze only when competitor unknown upper bounds cannot change order. Leading strategy unknown may remain if choice is robust.'
    return result

def run(out,revision):
    scores=load(out/f'scores-e3-{revision}.json');mp=Path(scores['mapping_path']);maps={r['intent_id']:r for r in load(mp)['records']}
    ids=sorted(maps);pos={i:j for j,i in enumerate(ids)};strata={}
    for i in ids:strata.setdefault(maps[i]['main_stratum'],[]).append(i)
    rng=random.Random(20261005)
    draws=np.asarray([[pos[rng.choice(strata[t])] for t in sorted(strata) for _ in strata[t]] for _ in range(10000)])
    details=list(rows(out/f'score-details-e3-{revision}.jsonl'))
    lookup={(r['configuration_id'],r['panel_id'],r['strategy'],r['budget'],r['intent_id'],r['stage']):r for r in details}
    transitions=list(rows(out/f'transitions-e3-{revision}.jsonl'));paired=[];within=[]
    for config in CONFIGS:
        for panel in PANELS:
            for B in (4096,8192):
                for P in ('P0','P1','P2'):
                    cell=[r for r in transitions if all(r[k]==v for k,v in [('configuration_id',config),('panel_id',panel),('budget',B),('strategy',P)])]
                    for comparison in sorted({r['comparison'] for r in cell}):
                        subset=[r for r in cell if r['comparison']==comparison];assert len(subset)==80
                        within.append(dict(configuration_id=config,panel_id=panel,strategy=P,budget=B,comparison=comparison,n=80,transitions=dict(collections.Counter(r['transition'] for r in subset))))
                    if P=='P0':continue
                    a=[lookup[config,panel,P,B,i,'final']['sufficient'] for i in ids]
                    b=[lookup[config,panel,'P0',B,i,'final']['sufficient'] for i in ids]
                    lo=np.asarray([int(x=='yes')-int(y!='no') for x,y in zip(a,b)],dtype=float)
                    hi=np.asarray([int(x!='no')-int(y=='yes') for x,y in zip(a,b)],dtype=float)
                    measured=np.asarray([int(x=='yes')-int(y=='yes') for x,y in zip(a,b)],dtype=float)
                    binary='unknown' not in a+b;gain=sum(x=='yes' and y=='no' for x,y in zip(a,b));loss=sum(x=='no' and y=='yes' for x,y in zip(a,b))
                    paired.append(dict(configuration_id=config,panel_id=panel,strategy=P,budget=B,n=80,confirmed_gain=gain,confirmed_loss=loss,confirmed_yes_delta=float(measured.mean()),confirmed_yes_delta_descriptive_ci=np.quantile(measured[draws].mean(axis=1),[.025,.975],method='linear').tolist(),possible_delta_interval=[float(lo.mean()),float(hi.mean())],binary=binary,mcnemar_p=exact_mcnemar(gain,loss) if binary else None))
    tested=[r for r in paired if r['binary']]
    for r,p in zip(tested,holm([r['mcnemar_p'] for r in tested])):r.update(holm_p=p,holm_family_size=len(tested))
    baseline=[]
    for config in CONFIGS[1:]:
        for panel in PANELS:
            for B in (4096,8192):
                for P in ('P0','P1','P2'):
                    a=[lookup[config,panel,P,B,i,'final']['sufficient'] for i in ids];b=[lookup[CONFIGS[0],panel,P,B,i,'final']['sufficient'] for i in ids]
                    delta=np.asarray([int(x=='yes')-int(y=='yes') for x,y in zip(a,b)],dtype=float)
                    baseline.append(dict(configuration_id=config,reference_configuration=CONFIGS[0],panel_id=panel,strategy=P,budget=B,n=80,confirmed_gain=sum(x=='yes' and y=='no' for x,y in zip(a,b)),confirmed_loss=sum(x=='no' and y=='yes' for x,y in zip(a,b)),confirmed_yes_delta=float(delta.mean()),confirmed_yes_delta_descriptive_ci=np.quantile(delta[draws].mean(axis=1),[.025,.975],method='linear').tolist(),possible_delta_interval=[sum(int(x=='yes')-int(y!='no') for x,y in zip(a,b))/80,sum(int(x!='no')-int(y=='yes') for x,y in zip(a,b))/80],scope='Same strategy/budget/panel paired vs B0; descriptive only, no additional hypothesis-test family.'))
    save_json(out/f'statistics-e3-{revision}.json',dict(independent_intents=80,seed=20261005,bootstrap_replicates=10000,unit='paired intent within main_stratum; shared draws',scope='development descriptive results; unknown interval is not a confidence interval; binary exact tests only, exploratory joint E3 restoration contrasts with Holm',paired=paired,baseline_paired=baseline,stage_transitions=within))
    costs=load(out/'cost-e3-r01.json')['cells'];profiles=load(out/'context-profiles-e3-r01.json')['cells']
    table=[]
    for r in scores['summary']:
        match=lambda a:all(a[k]==r[k] for k in ('configuration_id','panel_id','strategy','budget'))
        cost=next(a for a in costs if match(a));profile=next(a for a in profiles if match(a))
        table.append(dict(r,**{k:v for k,v in cost.items() if k in ('mean_seconds','median_seconds','wall_seconds')},**{k:v for k,v in profile.items() if k not in ('configuration_id','panel_id','strategy','budget','n')}))
    with (out/f'comparison-e3-{revision}.csv').open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    # Choice is primarily for the E1 first-ranked core candidate; B0 and C3
    # separate decisions and sensitivity are retained. No pooled weighted metric.
    cold=load(out/'cost-reference-e3-r02.json')
    choices={}
    for config in CONFIGS:
        measured={r['strategy']:r['mean_seconds'] for r in cold['summary'] if r['configuration_id']==config}
        choices[config]=robust_choice([dict(r,mean_seconds=measured[r['strategy']]) for r in scores['summary'] if r['configuration_id']==config and r['panel_id']=='fixed_budget_main' and r['budget']==4096])
    decision=choices[CONFIGS[1]]
    save_json(out/f'recovery-selection-e3-{revision}.json',dict(status=decision['status'],selected=decision['selected'],basis_configuration=CONFIGS[1],decision_rule=decision['rule'],all_configuration_decisions=choices,budget=4096,panel_id='fixed_budget_main',mapping_sha256=sha(mp),scores_sha256=sha(out/f'scores-e3-{revision}.json'),cost_reference_sha256=sha(out/'cost-reference-e3-r02.json'),scope='single common restoration strategy for E2 candidate ablations; baseline B0 remains reference; choice by primary E1 candidate, other configurations report robustness. Scores file incremental-cache decisions are provisional; this cold-reference selection is authoritative.',E2_started=False))
    cases=[];mapping_digest=sha(mp)
    for path in sorted(out.glob('contexts-*.jsonl')):
        file_digest=sha(path)
        for ctx in rows(path):
            config=ctx['configuration_id'];panel=ctx['panel_id'];P=ctx['strategy'];B=ctx['budget'];i=ctx['intent_id']
            raw=lookup[config,panel,P,B,i,'raw'];ex=lookup[config,panel,P,B,i,'expanded'];final=lookup[config,panel,P,B,i,'final'];base=lookup[config,panel,'P0',B,i,'final']
            tags=[]
            if raw['sufficient']=='no' and ex['sufficient']=='yes':tags.append('confirmed_expansion_recovery')
            if ex['sufficient']=='yes' and final['sufficient'] in ('no','unknown'):tags.append('confirmed_budget_loss' if final['sufficient']=='no' else 'possible_budget_loss')
            if P!='P0' and base['sufficient']!=final['sufficient']:tags.append('restoration_final_contrast')
            if not tags:continue
            cases.append(dict(configuration_id=config,panel_id=panel,strategy=P,budget=B,intent_id=i,tags=tags,raw=raw['sufficient'],expanded=ex['sufficient'],final=final['sufficient'],P0_final=base['sufficient'],requirements=maps[i]['requirements'],stages={s:dict(score=lookup[config,panel,P,B,i,s],units=ctx[s]['units']) for s in ('raw','expanded','final')},truncation=ctx['truncation'],context_id=ctx['context_id'],context_file_sha256=file_digest,mapping_sha256=mapping_digest))
    save_rows(out/f'cases-e3-{revision}.jsonl',cases)
    print(json.dumps(dict(decision=decision,cases=len(cases),table=table),ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.output.resolve(),a.revision)
