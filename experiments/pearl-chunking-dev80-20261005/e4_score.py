"""E4 scoring and final Layer 1-2 re-evaluation under one common support map.

Arms: C2-L384-O0-M0 (E1 ranking, E3 -11 P0 contexts; strict reuse) and C2-L384-O0-M1
(-13 new index/ranking/contexts). Final-freeze candidates C3-L256-O0-M0 and
B0-regex320-overlap48-M0 (E1 rankings, E3 -11 P0 contexts) are re-scored under the
same map. Layer 1 = raw R1-R4 Top1/5/10/20 child core+overlap spans (prefix spans
never scored); Layer 2 = P0 x 4K/8K x two panels x four stages. Production scoring
(score.score_context with the E3 scope-revision projection) is asserted per cell
against the independent projection. Decision follows e4-prefix-selection-rule-r01.
"""
from __future__ import annotations
import argparse
import collections
import json
import random
import statistics
from pathlib import Path
import e3_scope_revision as rev
import score as core
from e1_visible_review_verify import intervals
from runtime import ROOT, sha, save_json, save_rows
from assemble import union_spans
from score import score_context, aggregate, score_support

E1=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
E2=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-13'
M0='C2-L384-O0-M0';M1='C2-L384-O0-M1';C3='C3-L256-O0-M0';B0='B0-regex320-overlap48-M0'
CONFIGS=(M0,M1,C3,B0)
PANELS=('fixed_budget_main','seed10_diagnostic');BUDGETS=(4096,8192);STAGES=('raw','expanded','deduplicated','final')
METHODS=('R1','R2','R3','R4');KS=(1,5,10,20)
COMPARE=('support','support_basis','sufficient','coverage_lower','coverage_upper','context_id','visible_text_sha256','contexts_file_sha256','ranking_file_sha256')

def load(p):return json.loads(Path(p).read_text('utf8'))
def jsonl(p):
    with Path(p).open(encoding='utf8') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def ctx_path(config,B,panel):return (OUT if config==M1 else E3)/f'contexts-{config}-P0-{B}-{panel}.jsonl'
def rank_path(config):return (OUT if config==M1 else E1)/('index-'+config)/'rankings.jsonl'

def transition(a,b):
    if a=='no' and b=='yes':return 'confirmed_gain'
    if a=='yes' and b=='no':return 'confirmed_loss'
    if a=='yes' and b=='unknown':return 'possible_loss'
    if a=='unknown' and b=='yes':return 'unresolved_to_yes'
    return a+'->'+b

def choose(rows):
    """Pre-registered r01: 4K yes desc, CEGR@10 yes desc, M0 on ties; threats keep pending."""
    order=sorted(rows,key=lambda r:(-r['yes'],-r['cegr10_yes'],0 if r['configuration_id']==M0 else 1))
    best=order[0]
    threats=[r['configuration_id'] for r in order[1:] if r['yes']+r['unknown']>=best['yes']]
    return dict(order=[r['configuration_id'] for r in order],selected=None if threats else best['configuration_id'],status='pending_review' if threats else 'frozen',threats=threats,
        existing_identity_if_pending=M0,rule='e4-prefix-selection-rule-r01')

def support_cell(spans,m):
    support,basis,_=rev.support_revision(spans,m);iv=intervals(spans)
    ind={q['requirement_id']:rev.independent_status(q,spans,iv) for q in m['requirements']}
    if ind!=support:raise AssertionError('independent projection mismatch')
    return support,basis

def layer1(config,maps,mh):
    rows=[];rp=rank_path(config);rh=sha(rp)
    for r in jsonl(rp):
        if r['status']!='success':raise ValueError('failed ranking '+config+' '+r['intent_id'])
        m=maps[r['intent_id']]
        for method in METHODS:
            ranked=r['results'][method];spans=[];first_yes=first_possible=None;k_state={}
            for rank,child in enumerate(ranked[:max(KS)],1):
                spans=spans+child['core_spans']+child.get('overlap_spans',[])
                support,basis=support_cell(spans,m);value=score_support(m['groups'],support)
                if value['sufficient']=='yes' and first_yes is None:first_yes=rank
                if value['sufficient']!='no' and first_possible is None:first_possible=rank
                if rank in KS:k_state[rank]=(support,basis,value)
            for k in KS:
                support,basis,value=k_state[k]
                rows.append(dict(kind='layer1_raw',configuration_id=config,intent_id=r['intent_id'],method=method,k=k,support=support,support_basis=basis,
                    complete_rr_lower=1/first_yes if first_yes and first_yes<=k else 0.,complete_rr_upper=1/first_possible if first_possible and first_possible<=k else 0.,
                    mapping_sha256=mh,ranking_file_sha256=rh,prefix_spans_scored=False,**value))
    return rows

def run(mapping_path,revision):
    core.reviewed_support=lambda spans,m:rev.support_revision(spans,m)[:2]
    mapping=load(mapping_path);maps={r['intent_id']:r for r in mapping['records']};mh=sha(mapping_path);assert len(maps)==80
    details=[];l1=[];summary=[];look={};unknown=[];profiles=[]
    for config in CONFIGS:
        l1+=layer1(config,maps,mh)
        for B in BUDGETS:
            for panel in PANELS:
                p=ctx_path(config,B,panel);fh=sha(p);local=[];prof=collections.defaultdict(list)
                for ctx in jsonl(p):
                    assert ctx['configuration_id']==config and ctx['strategy']=='P0' and ctx['budget']==B and ctx['panel_id']==panel
                    m=maps[ctx['intent_id']];st={}
                    for stage in STAGES:
                        spans=[s for u in ctx[stage]['units'] for s in u['spans']];iv=intervals(spans)
                        r=score_context(ctx,m,stage)
                        ind={q['requirement_id']:rev.independent_status(q,spans,iv) for q in m['requirements']}
                        assert ind==r['support'],('independent projection mismatch',config,ctx['intent_id'],stage)
                        r.update(configuration_id=config,strategy='P0',budget=B,panel_id=panel,mapping_sha256=mh,contexts_file_sha256=fh,ranking_file_sha256=ctx['ranking_file_sha256'],visible_text_sha256=ctx[stage]['text_sha256'])
                        st[stage]=r;details.append(r)
                        if stage=='final' and r['sufficient']=='unknown':unknown.append(dict(r,visible_spans=spans,context_file=p.relative_to(ROOT).as_posix()))
                    look[config,B,panel,ctx['intent_id']]=st;local.append(st['final'])
                    fin=[s for u in ctx['final']['units'] for s in u['spans']]
                    prof['final_tokens'].append(ctx['final']['token_count']);prof['final_units'].append(len(ctx['final']['units']))
                    prof['final_sources'].append(len({(s['doc_id'],s['source_version']) for s in fin}));prof['final_chars'].append(sum(s['end']-s['start'] for s in union_spans(fin)) if fin else 0)
                    prof['truncated'].append(any(t['reason']=='prefix_truncated' for t in ctx['truncation']));prof['assembly_seconds'].append(ctx['assembly_seconds'])
                assert len(local)==80
                summary.append(dict(configuration_id=config,strategy='P0',budget=B,panel_id=panel,contexts_file_sha256=fh,**aggregate(local)))
                profiles.append(dict(configuration_id=config,budget=B,panel_id=panel,n=80,**{k:(statistics.mean(v) if k!='truncated' else sum(v)) for k,v in prof.items()}))
    cegr={}
    for c in CONFIGS:
        v=[sum(look[c,B,'seed10_diagnostic',i]['raw']['sufficient']=='yes' for i in maps) for B in BUDGETS];assert v[0]==v[1]
        cegr[c]=dict(yes=v[0],unknown=sum(look[c,4096,'seed10_diagnostic',i]['raw']['sufficient']=='unknown' for i in maps))
        l1y=sum(r['sufficient']=='yes' for r in l1 if r['configuration_id']==c and r['method']=='R4' and r['k']==10)
        if l1y!=v[0]:raise AssertionError('Layer1 R4@10 differs from seed10 raw CEGR@10 '+c)
    l1sum=[]
    for c in CONFIGS:
        for method in METHODS:
            for k in KS:
                vals=[r for r in l1 if r['configuration_id']==c and r['method']==method and r['k']==k]
                l1sum.append(dict(configuration_id=c,method=method,k=k,**aggregate(vals),complete_mrr_lower=statistics.mean(r['complete_rr_lower'] for r in vals),complete_mrr_upper=statistics.mean(r['complete_rr_upper'] for r in vals)))
    rows=[dict(configuration_id=c,cegr10_yes=cegr[c]['yes'],**{k:r[k] for k in ('yes','no','unknown')}) for c in (M0,M1) for r in summary if r['configuration_id']==c and r['budget']==4096 and r['panel_id']=='fixed_budget_main']
    decision=dict(table=rows,**choose(rows))
    transitions=[dict(configuration_id=M1,base=M0,budget=B,panel_id=panel,intent_id=i,before=look[M0,B,panel,i]['final']['sufficient'],after=look[M1,B,panel,i]['final']['sufficient'],
        transition=transition(look[M0,B,panel,i]['final']['sufficient'],look[M1,B,panel,i]['final']['sufficient']),mapping_sha256=mh) for B in BUDGETS for panel in PANELS for i in sorted(maps)]
    pairs=[(M1,M0),(M0,B0),(M1,B0),(C3,B0)]
    stats=bootstrap(look,maps,pairs)
    equivalence,changes=compare_previous(details,revision)
    retrieval=ranking_shift()
    save_rows(OUT/f'score-details-e4-{revision}.jsonl',details);save_rows(OUT/f'layer1-details-e4-{revision}.jsonl',l1)
    save_rows(OUT/f'transitions-e4-{revision}.jsonl',transitions);save_rows(OUT/f'unknown-e4-{revision}.jsonl',unknown);save_rows(OUT/f'scoring-revision-changes-e4-{revision}.jsonl',changes)
    save_json(OUT/f'context-profiles-e4-{revision}.json',profiles)
    save_json(OUT/f'scores-e4-{revision}.json',dict(mapping_path=mapping_path.relative_to(ROOT).as_posix(),mapping_sha256=mh,summary=summary,layer1_summary=l1sum,cegr10=cegr,decision=decision,
        statistics=stats,equivalence=equivalence,retrieval_shift=retrieval,score_cells=len(details),layer1_cells=len(l1),contexts=len(look),independent_intents=80,stage='E4+final-layer1-2',
        prefix_scored=False,generation_calls=0))
    print(json.dumps(dict(decision=decision,cegr10=cegr,equivalence={k:{x:y for x,y in v.items() if x!='mismatch_examples'} for k,v in equivalence.items()}),ensure_ascii=False,indent=1),flush=True)

def compare_previous(details,revision):
    """Strict-equivalence proof vs E2 r11 (C2/C3 M0) and revision changes vs E3 r10 (B0)."""
    prev={}
    for path,configs in ((E2/'score-details-e2-r11.jsonl',(M0,C3)),(E3/'score-details-e3-r10.jsonl',(B0,))):
        for r in jsonl(path):
            if r['configuration_id'] in configs and r.get('strategy')=='P0':prev[r['configuration_id'],r['budget'],r['panel_id'],r['intent_id'],r['stage']]=(path.name,r)
    own=OUT/'score-details-e4-r11.jsonl'
    if revision!='r11' and own.is_file():
        for r in jsonl(own):prev[r['configuration_id'],r['budget'],r['panel_id'],r['intent_id'],r['stage']]=(own.name,r)
    out={};changes=[]
    for r in details:
        k=(r['configuration_id'],r['budget'],r['panel_id'],r['intent_id'],r['stage'])
        if k not in prev:continue
        name,p=prev[k];e=out.setdefault(f'{r["configuration_id"]} vs {name}',dict(cells=0,identical=0,sufficient_changed=0,context_identical=0,mismatch_examples=[]))
        e['cells']+=1;same=all(r.get(f)==p.get(f) for f in COMPARE if f not in ('contexts_file_sha256',)) and r['contexts_file_sha256']==p['contexts_file_sha256']
        e['context_identical']+=r['context_id']==p['context_id'] and r['visible_text_sha256']==p['visible_text_sha256'] and r['contexts_file_sha256']==p['contexts_file_sha256']
        if same:e['identical']+=1
        else:
            if len(e['mismatch_examples'])<5:e['mismatch_examples'].append(dict(key=list(k),fields=[f for f in COMPARE if r.get(f)!=p.get(f)]))
        if r['sufficient']!=p['sufficient'] or r['support']!=p['support']:
            e['sufficient_changed']+=r['sufficient']!=p['sufficient']
            changes.append(dict(configuration_id=k[0],budget=k[1],panel_id=k[2],intent_id=k[3],stage=k[4],previous_file=name,previous_mapping_sha256=p['mapping_sha256'],mapping_sha256=r['mapping_sha256'],
                before=p['sufficient'],after=r['sufficient'],support_before=p['support'],support_after=r['support']))
    return out,changes

def ranking_shift():
    """Mechanism report: how much M1 moves the R1-R4 candidate sets relative to M0 (by base chunk)."""
    a={r['intent_id']:r for r in jsonl(rank_path(M0))};out={}
    b={r['intent_id']:r for r in jsonl(rank_path(M1))}
    for method in METHODS:
        for k in (10,100):
            j=[]
            for i in a:
                x={c['chunk_id'] for c in a[i]['results'][method][:k]};y={c.get('base_chunk_id',c['chunk_id']) for c in b[i]['results'][method][:k]}
                j.append(len(x&y)/len(x|y) if x|y else 1.)
            out[f'{method}@{k}']=dict(mean_jaccard=statistics.mean(j),identical_sets=sum(v==1. for v in j))
    return out

def bootstrap(look,maps,pairs):
    strata=collections.defaultdict(list)
    for i,m in maps.items():strata[m['main_stratum']].append(i)
    rng=random.Random(20261005);draws=[[rng.choice(strata[t]) for t in sorted(strata) for _ in strata[t]] for _ in range(10000)]
    out=[]
    for config,base in pairs:
        for B in BUDGETS:
            for panel in PANELS:
                d={i:(look[config,B,panel,i]['final']['sufficient']=='yes')-(look[base,B,panel,i]['final']['sufficient']=='yes') for i in maps}
                vals=sorted(sum(d[i] for i in s)/80 for s in draws)
                a=[look[base,B,panel,i]['final']['sufficient'] for i in sorted(maps)];b=[look[config,B,panel,i]['final']['sufficient'] for i in sorted(maps)]
                gain=sum(x=='no' and y=='yes' for x,y in zip(a,b));loss=sum(x=='yes' and y=='no' for x,y in zip(a,b))
                lo=(sum(y=='yes' for y in b)-sum(x!='no' for x in a))/80;hi=(sum(y!='no' for y in b)-sum(x=='yes' for x in a))/80
                mc=None
                if 'unknown' not in a+b:
                    from scipy.stats import binomtest
                    n=gain+loss;mc=binomtest(gain,n,.5).pvalue if n else 1.0
                out.append(dict(configuration_id=config,base=base,budget=B,panel_id=panel,confirmed_yes_difference=sum(d.values())/80,bootstrap_95=[vals[249],vals[9749]],confirmed_gain=gain,confirmed_loss=loss,possible_difference_bounds=[lo,hi],exact_mcnemar_p=mc,seed=20261005,draws=10000))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mapping',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();run(a.mapping.resolve(),a.revision)
