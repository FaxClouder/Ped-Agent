"""E2 scoring/analysis: frozen AND/OR three-valued support on actual P0 contexts.

O0 contexts are the exact E3 -11 P0 files (strict-equivalence reuse); O10/O20 are the
new -12 files. Scope-revision projection is the E3 r10 one (e3_scope_revision);
an E2 supplement map must be a strict extension of r10 recorded in a lineage file.
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
from assemble import union_spans, subtract_spans, key
from score import score_context, aggregate

E1=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
BASES=('C2-L384-O0-M0','C3-L256-O0-M0')
def arms(base):return [base,base.replace('-O0-','-O10-'),base.replace('-O0-','-O20-')]
CONFIGS=[c for b in BASES for c in arms(b)]
PANELS=('fixed_budget_main','seed10_diagnostic');BUDGETS=(4096,8192);STAGES=('raw','expanded','deduplicated','final')

def load(p):return json.loads(Path(p).read_text('utf8'))
def jsonl(p):
    with Path(p).open(encoding='utf8') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def ctx_path(config,B,panel):
    root=E3 if '-O0-' in config else OUT
    return root/f'contexts-{config}-P0-{B}-{panel}.jsonl'
def index_dir(config):return (E1 if '-O0-' in config else OUT)/('index-'+config)

def chars(spans):return sum(s['end']-s['start'] for s in union_spans(spans)) if spans else 0

def transition(a,b):
    if a=='no' and b=='yes':return 'confirmed_gain'
    if a=='yes' and b=='no':return 'confirmed_loss'
    if a=='yes' and b=='unknown':return 'possible_loss'
    if a=='unknown' and b=='yes':return 'unresolved_to_yes'
    return a+'->'+b

def choose(rows):
    """Pre-registered r01: 4K yes desc, CEGR@10 yes desc, smaller O; threats keep pending."""
    order=sorted(rows,key=lambda r:(-r['yes'],-r['cegr10_yes'],r['overlap_ratio']))
    best=order[0]
    threats=[r['configuration_id'] for r in order[1:] if r['yes']+r['unknown']>=best['yes']]
    return dict(order=[r['configuration_id'] for r in order],selected=None if threats else best['configuration_id'],status='pending_review' if threats else 'frozen',threats=threats,rule='e2-overlap-selection-rule-r01')

def run(mapping_path,revision):
    core.reviewed_support=lambda spans,m:rev.support_revision(spans,m)[:2]
    mapping=load(mapping_path);maps={r['intent_id']:r for r in mapping['records']};mh=sha(mapping_path);assert len(maps)==80
    children={c:{r['chunk_id']:r for r in jsonl(index_dir(c)/'child_chunks.jsonl')} for c in CONFIGS}
    details=[];summary=[];look={};unknown=[];profiles=[]
    for config in CONFIGS:
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
                    # duplication / effective overlap on actual units
                    exp_spans=[s for u in ctx['expanded']['units'] for s in u['spans']]
                    gross=sum(s['end']-s['start'] for s in exp_spans);dedup=sum(s['end']-s['start'] for u in ctx['deduplicated']['units'] for s in u['spans'])
                    fin=[s for u in ctx['final']['units'] for s in u['spans']]
                    ov=[];ovgross=0
                    for u in ctx['final']['units']:
                        o=children[config][u['seed_chunk_id']].get('overlap_spans',[]);ovgross+=sum(s['end']-s['start'] for s in o)
                        for s in u['spans']:
                            for t in o:
                                if key(s)==key(t) and min(s['end'],t['end'])>max(s['start'],t['start']):ov.append(dict(s,start=max(s['start'],t['start']),end=min(s['end'],t['end'])))
                    prof['gross_chars'].append(gross);prof['dedup_chars'].append(dedup);prof['duplicate_ratio'].append(1-dedup/gross if gross else 0.)
                    prof['final_tokens'].append(ctx['final']['token_count']);prof['final_units'].append(len(ctx['final']['units']))
                    prof['final_sources'].append(len({(s['doc_id'],s['source_version']) for s in fin}));prof['final_chars'].append(chars(fin))
                    prof['final_effective_overlap_chars'].append(chars(ov));prof['final_overlap_gross_chars'].append(ovgross)
                    prof['truncated'].append(any(t['reason']=='prefix_truncated' for t in ctx['truncation']))
                    prof['assembly_seconds'].append(ctx['assembly_seconds'])
                agg=aggregate(local)
                summary.append(dict(configuration_id=config,strategy='P0',budget=B,panel_id=panel,contexts_file_sha256=fh,**agg))
                profiles.append(dict(configuration_id=config,budget=B,panel_id=panel,n=80,**{k:(statistics.mean(v) if k!='truncated' else sum(v)) for k,v in prof.items()},effective_overlap_share_of_final_chars=sum(prof['final_effective_overlap_chars'])/sum(prof['final_chars'])))
    for config in CONFIGS:
        for B in BUDGETS:
            for panel in PANELS:
                hit=[r for r in summary if r['configuration_id']==config and r['budget']==B and r['panel_id']==panel][0]
                hit['cegr10_yes']=sum(look[config,B,'seed10_diagnostic',i]['raw']['sufficient']=='yes' for i in maps) if panel=='seed10_diagnostic' else None
    transitions=[]
    for base in BASES:
        for config in arms(base)[1:]:
            for B in BUDGETS:
                for panel in PANELS:
                    for i in sorted(maps):
                        a=look[base,B,panel,i]['final']['sufficient'];b=look[config,B,panel,i]['final']['sufficient']
                        transitions.append(dict(configuration_id=config,base=base,budget=B,panel_id=panel,intent_id=i,before=a,after=b,transition=transition(a,b),mapping_sha256=mh))
    # CEGR@10 is the seed10 raw stage, budget independent: assert identical across budgets.
    cegr={}
    for c in CONFIGS:
        v=[sum(look[c,B,'seed10_diagnostic',i]['raw']['sufficient']=='yes' for i in maps) for B in BUDGETS];assert v[0]==v[1];cegr[c]=dict(yes=v[0],unknown=sum(look[c,4096,'seed10_diagnostic',i]['raw']['sufficient']=='unknown' for i in maps))
    decisions={}
    for base in BASES:
        rows=[dict(configuration_id=c,overlap_ratio={'O0':0,'O10':.1,'O20':.2}[c.split('-')[2]],cegr10_yes=cegr[c]['yes'],**{k:r[k] for k in ('yes','no','unknown')}) for c in arms(base) for r in summary if r['configuration_id']==c and r['budget']==4096 and r['panel_id']=='fixed_budget_main']
        decisions[base]=dict(table=rows,**choose(rows))
    stats=bootstrap(look,maps)
    save_rows(OUT/f'score-details-e2-{revision}.jsonl',details);save_rows(OUT/f'transitions-e2-{revision}.jsonl',transitions);save_rows(OUT/f'unknown-e2-{revision}.jsonl',unknown)
    save_json(OUT/f'context-profiles-e2-{revision}.json',profiles)
    save_json(OUT/f'scores-e2-{revision}.json',dict(mapping_path=mapping_path.relative_to(ROOT).as_posix(),mapping_sha256=mh,summary=summary,cegr10=cegr,decisions=decisions,statistics=stats,score_cells=len(details),contexts=len(look),independent_intents=80,stage='E2',generation_calls=0))
    print(json.dumps(dict(decisions=decisions,cegr10=cegr),ensure_ascii=False,indent=1),flush=True)

def bootstrap(look,maps):
    strata=collections.defaultdict(list)
    for i,m in maps.items():strata[m['main_stratum']].append(i)
    rng=random.Random(20261005);draws=[[rng.choice(strata[t]) for t in sorted(strata) for _ in strata[t]] for _ in range(10000)]
    out=[]
    for base in BASES:
        for config in arms(base)[1:]:
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
