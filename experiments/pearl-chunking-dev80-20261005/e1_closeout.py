"""Read-only r07 E1 closeout and legacy E3 scoring parity; never runs E3."""
import argparse
import json
import math
from pathlib import Path
import random
import numpy as np
from runtime import ROOT, sha, save_json, save_rows
from e1 import configurations
from e1_statistics import select_panel
from e1_visible_review import stream, detail_key
from evaluate import run as evaluate_saved
from e1_visible_review_verify import intervals, req_status, all_inside
from score import score_support

BASE='B0-regex320-overlap48-M0'
PANELS=('R4_CEGR10','P0_CGC4096','P0_CGC8192')
def load(p): return json.loads(Path(p).read_text('utf8'))

def exact_mcnemar(gain,loss):
    n=gain+loss
    return min(1.,2*sum(math.comb(n,k) for k in range(min(gain,loss)+1))/2**n) if n else 1.

def holm(ps):
    order=sorted(range(len(ps)),key=lambda i:ps[i]);out=[None]*len(ps);last=0.
    for rank,i in enumerate(order):
        last=max(last,min(1.,ps[i]*(len(ps)-rank)));out[i]=last
    return out

def verify_manifest(run):
    manifest=load(run/'delivery-manifest.json');drift=[];code_drift=[];bindings={}
    expected_files=dict(manifest.get('artifacts_sha256',{}))
    for name,item in manifest.get('inputs',{}).items():
        if isinstance(item,dict) and 'path' in item and 'sha256' in item:expected_files[item['path']]=item['sha256']
        elif isinstance(item,str) and '/' in name:expected_files[name]=item
    if not expected_files:raise ValueError('Manifest has no hash bindings')
    for name,expected in expected_files.items():
        p=ROOT/name;actual=sha(p) if p.is_file() else None;bindings[name]=actual
        if actual!=expected:
            item=dict(path=name,expected=expected,actual=actual)
            (code_drift if name.startswith('experiments/') else drift).append(item)
    if drift:raise ValueError('Frozen output drift: '+str(drift))
    return dict(status='passed',manifest_sha256=sha(run/'delivery-manifest.json'),checked=len(bindings),output_drift=drift,code_drift=code_drift,artifacts_sha256=bindings)

def bootstrap(records,maps):
    ids=sorted(maps);positions={i:j for j,i in enumerate(ids)};strata={}
    for i in ids:strata.setdefault(maps[i]['main_stratum'],[]).append(i)
    rng=random.Random(20261005)
    draws=np.asarray([[positions[rng.choice(strata[t])] for t in sorted(strata) for _ in strata[t]] for _ in range(10000)],dtype=np.int32)
    values={};overall=[];paired=[]
    for c,details in records.items():
        for panel in PANELS:
            chosen,lookup=select_panel(details,panel,ids)
            if any(r.get('failure') for r in chosen):raise ValueError('Failed quality cell in statistics')
            a=np.asarray([[int(lookup[i]['sufficient']=='yes'),int(lookup[i]['sufficient']!='no')] for i in ids],dtype=float)
            values[c,panel]=(a,lookup)
            ci=np.quantile(a[draws].mean(axis=1),[.025,.975],axis=0,method='linear')
            overall.append(dict(configuration_id=c,panel=panel,n=len(ids),yes=int(a[:,0].sum()),unknown=int((a[:,1]-a[:,0]).sum()),lower_point=float(a[:,0].mean()),possible_upper_point=float(a[:,1].mean()),lower_estimate_ci=ci[:,0].tolist(),possible_upper_estimate_ci=ci[:,1].tolist(),strata={t:{s:sum(lookup[i]['sufficient']==s for i in group) for s in ('yes','no','unknown')} for t,group in strata.items()}))
    pairs=[(c,BASE,'baseline_family') for c in records if c!=BASE]
    pairs += [('C3-L256-O0-M0','C2-L256-O0-M0','secondary_exploratory'),('C2-L384-O0-M0','C3-L256-O0-M0','secondary_exploratory')]
    for c,b,family in pairs:
        for panel in PANELS:
            a,la=values[c,panel];v,lb=values[b,panel];delta=a[:,0]-v[:,0];bounds=np.stack([a[:,0]-v[:,1],a[:,1]-v[:,0]],axis=1)
            ci=np.quantile(bounds[draws].mean(axis=1),[.025,.975],axis=0,method='linear')
            binary=bool(np.array_equal(a[:,0],a[:,1]) and np.array_equal(v[:,0],v[:,1]))
            gain=sum(la[i]['sufficient']=='yes' and lb[i]['sufficient']=='no' for i in ids);loss=sum(la[i]['sufficient']=='no' and lb[i]['sufficient']=='yes' for i in ids)
            paired.append(dict(configuration_id=c,baseline=b,panel=panel,family=family,n=len(ids),certificate_lower_difference=float(delta.mean()),certificate_lower_difference_ci=np.quantile(delta[draws].mean(axis=1),[.025,.975],method='linear').tolist(),possible_delta_interval=bounds.mean(axis=0).tolist(),possible_delta_bootstrap_envelope=[float(ci[0,0]),float(ci[1,1])],confirmed_gains=gain,confirmed_losses=loss,binary=binary,mcnemar_exact_p=exact_mcnemar(gain,loss) if binary else None))
    tested=[r for r in paired if r['family']=='baseline_family' and r['binary']]
    for row,p in zip(tested,holm([r['mcnemar_exact_p'] for r in tested])):row.update(holm_p=p,holm_family_size=len(tested),holm_significant=p<.05)
    return dict(status='completed',seed=20261005,replicates=10000,independent_intents=80,stratum_sizes={t:len(g) for t,g in strata.items()},sampling_unit='intent; shared draws within sorted strata across configurations and panels',quantile='numpy linear',holm_family='All 12 nonbaseline configurations vs B0 across the two completely binary selection panels (24 tests); exploratory secondary pairs excluded.',scope='Development descriptive intervals and binary exact McNemar/Holm only. Selection and evaluation use the same dev80; no independent confirmation. Unknown envelopes are not confidence intervals or measured success.',overall=overall,paired=paired),values

def run(source,reviewed,output):
    output.mkdir(exist_ok=False)
    preservation={}
    for p in (reviewed,source,ROOT/'outputs/pearl-chunking-dev80-20261005-06'):
        print('hashing',p.name,flush=True);preservation[p.name]=verify_manifest(p)
    save_json(output/'preservation-inputs-r01.json',preservation)
    verification=load(reviewed/'verification-e1-r07.json');scores=load(reviewed/'scores-e1-r07.json');mp=reviewed/'common-support-map-e1-r07.json';maps={r['intent_id']:r for r in load(mp)['records']}
    if verification['status']!='passed' or verification['score_file_sha256']!=sha(reviewed/'scores-e1-r07.json') or verification['mapping_sha256']!=sha(mp) or scores['mapping_sha256']!=sha(mp):raise ValueError('r07 verification binding drift')
    selection=load(reviewed/'candidate-selection-e1-r07.json')
    if selection['status']!='frozen' or selection['selected']!=['C2-L384-O0-M0','C3-L256-O0-M0']:raise ValueError('Unexpected candidate selection')
    records={};parity=[];transitions=[];case_contexts={};detail_bindings={};old=load(source/'verification-e1-r01.json')
    selected=[BASE]+selection['selected']+['C2-L256-O0-M0']
    for config in configurations():
        print('parity',config,flush=True);src=source/('index-'+config);path=reviewed/('index-'+config)/'score-details-e1-r07.jsonl'
        records[config]=list(stream(path));detail_bindings[config]=sha(path)
        meta=load(reviewed/('index-'+config)/'score-meta-e1-r07.json')
        if meta['details_sha256']!=sha(path) or meta['mapping_sha256']!=sha(mp):raise ValueError('detail/meta drift')
        for name in ('contexts.jsonl','rankings.jsonl'):
            if sha(src/name)!=meta['input_sha256'][name] or sha(src/name)!=old['checks'][config]['artifact_sha256'][name]:raise ValueError('r05 input drift')
        res=evaluate_saved(src,mp);expected={(r['intent_id'],r['cell']):r for r in records[config]};mismatches=[]
        fields=('support','support_basis','sufficient','coverage_lower','coverage_upper','mapping_sha256','context_sha256','ranking_sha256')
        for r in res['details']:
            d=expected[r['intent_id'],r['cell']]
            if any(r.get(f)!=d.get(f) for f in fields):mismatches.append(dict(intent_id=r['intent_id'],cell=r['cell']))
        if mismatches or len(res['details'])!=len(expected):raise ValueError('Legacy parity drift '+str(mismatches[:5]))
        # Independent interval implementation; does not invoke support_r06.
        independent=[]
        for context in stream(src/'contexts.jsonl'):
            m=maps[context['intent_id']]
            for stage in ('raw','expanded','final'):
                visible=[s for u in context[stage]['units'] for s in u['spans']];iv=intervals(visible)
                support={q['requirement_id']:req_status(q,visible,iv) for q in m['requirements']}
                d=expected[context['intent_id'],f"{context['panel_id']}/{context['strategy']}/{context['budget']}/{stage}"]
                if support!=d['support'] or score_support(m['groups'],support)['sufficient']!=d['sufficient']:independent.append(context['context_id'])
            if config in selected:case_contexts[config,context['intent_id'],context['budget']]=context
            a=expected[context['intent_id'],f"fixed_budget_main/P0/{context['budget']}/expanded"];b=expected[context['intent_id'],f"fixed_budget_main/P0/{context['budget']}/final"]
            transitions.append(dict(configuration_id=config,intent_id=context['intent_id'],budget=context['budget'],expanded=a['sufficient'],final=b['sufficient'],confirmed_loss=a['sufficient']=='yes' and b['sufficient']=='no',possible_loss=a['sufficient']=='yes' and b['sufficient']=='unknown',context_id=context['context_id'],context_sha256=b['context_sha256']))
        if independent:raise ValueError('Independent context mismatch')
        parity.append(dict(configuration_id=config,detail_cells=len(expected),context_stage_cells=480,legacy_mismatches=0,independent_context_mismatches=0,rankings_sha256=sha(src/'rankings.jsonl'),contexts_sha256=sha(src/'contexts.jsonl')))
    save_json(output/'scoring-parity-r01.json',dict(status='passed',mapping_sha256=sha(mp),checks=parity,detail_cells=sum(r['detail_cells'] for r in parity),context_stage_cells=6240,independent_verifier='e1_visible_review_verify.req_status; saved raw/expanded/final spans',generation_calls=0,remote_judge_calls=0))
    stats,values=bootstrap(records,maps);stats.update(mapping_sha256=sha(mp),score_file_sha256=sha(reviewed/'scores-e1-r07.json'),verification_sha256=sha(reviewed/'verification-e1-r07.json'),detail_bindings=detail_bindings)
    save_json(output/'statistics-e1-r07-closeout-r01.json',stats)
    save_rows(output/'budget-transitions-r07-r01.jsonl',transitions)
    cases=[]
    pairs=[(c,BASE) for c in selection['selected']]+[('C3-L256-O0-M0','C2-L256-O0-M0')]
    for c,b in pairs:
        for panel in PANELS:
            _,la=values[c,panel];_,lb=values[b,panel]
            for intent in sorted(maps):
                if la[intent]['sufficient']==lb[intent]['sufficient']:continue
                row=dict(configuration_id=c,comparator=b,panel=panel,intent_id=intent,query=maps[intent]['query'],candidate_status=la[intent]['sufficient'],comparator_status=lb[intent]['sufficient'],candidate_detail=la[intent],comparator_detail=lb[intent],requirements=maps[intent]['requirements'],interpretation='Saved-content difference under existing review, not a new semantic judgment or isolated chunking cause.')
                if panel!='R4_CEGR10':
                    budget=4096 if panel=='P0_CGC4096' else 8192
                    for tag,config in (('candidate',c),('comparator',b)):
                        ctx=case_contexts[config,intent,budget];vis=[s for u in ctx['final']['units'] for s in u['spans']];iv=intervals(vis)
                        row[tag+'_context']=dict(path=str((source/('index-'+config)/'contexts.jsonl').relative_to(ROOT)),context_id=ctx['context_id'],visible_spans=vis,token_count=ctx['final']['token_count'],visible_units=ctx['final']['units'])
                        row[tag+'_support_trace']=[dict(requirement_id=q['requirement_id'],basis=row[tag+'_detail']['support_basis'][q['requirement_id']],reviewer_id=q.get('visible_universe_review',{}).get('reviewer_id'),caveats=q.get('visible_universe_review',{}).get('caveats',[]),alternatives=[dict(source_spans=a['source_spans'],fully_visible=all_inside(a['source_spans'],iv),review_spans=a.get('review_spans'),rationale=a.get('rationale')) for a in q.get('visible_universe_review',{}).get('alternatives',[])]) for q in maps[intent]['requirements']]
                cases.append(row)
    save_rows(output/'paired-difference-cases-r07-r01.jsonl',cases)
    r06_changes=[]
    for c,ds in records.items():
        before={detail_key(r):r for r in stream(reviewed/('index-'+c)/'score-details-e1-r06.jsonl')}
        r06_changes += [dict(configuration_id=c,intent_id=d['intent_id'],cell=d['cell'],r06=before[detail_key(d)]['sufficient'],r07=d['sufficient'],support_basis=d['support_basis']) for d in ds if d['sufficient']!=before[detail_key(d)]['sufficient']]
    save_rows(output/'r06-r07-status-changes-r01.jsonl',r06_changes)
    save_json(output/'closeout-receipt-r01.json',dict(status='completed',stage='E1_closeout_E3_scoring_bridge',selected=selection['selected'],baseline=BASE,cases=len(cases),budget_transitions=len(transitions),r06_r07_status_changes=len(r06_changes),index_builds=0,retrieval_runs=0,assembly_runs=0,E3_units=0,semantic_judgments_added=0,generation_calls=0,remote_model_calls=0,remote_judge_calls=0))
    print('closeout completed; E3 units 0',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-run',type=Path,required=True);p.add_argument('--reviewed-run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.source_run.resolve(),a.reviewed_run.resolve(),a.output.resolve())
