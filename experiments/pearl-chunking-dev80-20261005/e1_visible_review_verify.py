"""Independent reopen check of Session 3B r06: reviews, selection-cell scores, candidate rule, preservation.

Deliberately re-implements interval containment, three-valued AND/OR and the
candidate rule instead of importing the r06 scorer.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text('utf8'))
def jl(p):
    with open(p,encoding='utf8') as f:
        for line in f:
            if line.strip():yield json.loads(line)
K=('doc_id','source_version','element_id')
def k(s):return tuple(s[x] for x in K)
def intervals(spans):
    d={}
    for s in spans:d.setdefault(k(s),[]).append((s['start'],s['end']))
    out={}
    for key,v in d.items():
        m=[]
        for a,b in sorted(v):
            if m and a<=m[-1][1]:m[-1][1]=max(m[-1][1],b)
            else:m.append([a,b])
        out[key]=m
    return out
def covers(iv,s):return any(a<=s['start'] and s['end']<=b for a,b in iv.get(k(s),[]))
def all_inside(spans,iv):
    # every character of spans lies inside merged intervals iv
    need=intervals(spans)
    return all(any(a<=x and y<=b for a,b in iv.get(key,[])) for key,v in need.items() for x,y in v)
def touches(spans,iv):return any(min(b,s['end'])>max(a,s['start']) for s in spans for a,b in iv.get(k(s),[]))
def part_of(spans,iv):
    out=[]
    for x in spans:
        for a,b in iv.get(k(x),[]):
            lo,hi=max(a,x['start']),min(b,x['end'])
            if lo<hi:out.append(dict(x,start=lo,end=hi))
    return out
def req_status(req,vis_spans,vis):
    cert=[g for g in req['evidence_groups'] if g.get('status') in ('yes','no') and g.get('reviewer_id') and g.get('rationale') and g.get('necessary_spans')]
    statuses=[g['status'] if all_inside(g['necessary_spans'],vis) else 'unknown' for g in cert]+['unknown']*(len(req['evidence_groups'])-len(cert))
    c='yes' if 'yes' in statuses else 'no' if statuses and all(x=='no' for x in statuses) else 'unknown'
    r=req.get('visible_universe_review')
    if c!='unknown' or r is None:return c
    if any(all_inside(a['source_spans'],vis) for a in r['alternatives']):return 'yes'
    if any(v['verdict']=='supports' and all_inside(v['source_spans'],vis) for u in r['uncertain'] for v in u.get('adjudicated_variants',[])):return 'yes'
    adjudicated=bool(r['uncertain']) and all('adjudicated_variants' in u for u in r['uncertain'])
    if r['universe_status']=='unknown' and not adjudicated:return 'unknown'
    for u in r['uncertain']:
        part=part_of(u['source_spans'],vis)
        if not part:continue
        if 'adjudicated_variants' not in u:return 'unknown'
        if not any(v['verdict']=='does_not_support' and all_inside(part,intervals(v['source_spans'])) for v in u['adjudicated_variants']):return 'unknown'
    U=intervals(r['universe_spans'])
    return 'no' if all_inside(vis_spans,U) else 'unknown'
def sufficient(groups,support):
    vals=[]
    for g in groups:
        s=[support[x] for x in g]
        vals.append('no' if 'no' in s else 'yes' if all(x=='yes' for x in s) else 'unknown')
    return 'yes' if 'yes' in vals else 'no' if all(v=='no' for v in vals) else 'unknown'

CELLS=('layer1_raw/R4/10','fixed_budget_main/P0/4096/final','fixed_budget_main/P0/8192/final')

def extract(src,out,configs):
    d=out/'verify-visible-extract';d.mkdir(exist_ok=True)
    for c in configs:
        idx=src/('index-'+c);vis={}
        for r in jl(idx/'rankings.jsonl'):vis['layer1_raw/R4/10|'+r['intent_id']]=[s for ch in r['results']['R4'][:10] for s in ch['core_spans']+ch.get('overlap_spans',[])]
        for r in jl(idx/'contexts.jsonl'):vis[f"fixed_budget_main/P0/{r['budget']}/final|"+r['intent_id']]=[s for u in r['final']['units'] for s in u['spans']]
        if len(vis)!=240:raise ValueError('extract coverage '+c)
        path=d/(c+'.json')
        with open(path,'x',encoding='utf8') as f:json.dump(dict(configuration_id=c,rankings_sha256=sha(idx/'rankings.jsonl'),contexts_sha256=sha(idx/'contexts.jsonl'),visible=vis),f,sort_keys=True)
        print('extracted',c,flush=True)

def preserve(out,receipt):
    pres={}
    for run in ('pearl-chunking-dev80-20261005-05','pearl-chunking-dev80-20261005-06'):
        man=ROOT/'outputs'/run/'delivery-manifest.json';m=load(man);arts=m.get('artifacts_sha256') or {}
        drift=[];large=[]
        for path,h in arts.items():
            f=ROOT/path
            if f.is_file() and f.stat().st_size>50_000_000:large.append(path);continue
            if not f.is_file() or sha(f)!=h:drift.append(path)
        pres[run]=dict(manifest_sha256=sha(man),artifacts=len(arts),hashed=len(arts)-len(large),drift=drift,large_files_checked_via_extract=large)
    with open(receipt,'x',encoding='utf8') as f:json.dump(dict(status='passed' if not any(v['drift'] for v in pres.values()) else 'failed',runs=pres),f,indent=2,sort_keys=True);f.write('\n')
    print('preservation',{k:len(v['drift']) for k,v in pres.items()},flush=True)

def check(src,out,rev,receipt_path,preservation_path):
    if receipt_path.exists():raise FileExistsError(receipt_path)
    checks={}
    scores=load(out/f'scores-e1-{rev}.json');map_path=out/scores['mapping_path']
    assert sha(map_path)==scores['mapping_sha256'],'score/map binding'
    mapping=load(map_path)
    m06=out/'common-support-map-e1-r06.json'
    if rev=='r06':assert mapping['previous_map_sha256']==sha(src/'common-support-map-e1-r05.json')
    else:
        assert mapping['previous_map_sha256']==sha(m06)
        ai=load(out/'adjudication-integration-r07.json');assert ai['status']=='passed' and ai['map_sha256']==sha(map_path)
        for name,h in mapping['adjudication_review_bindings'].items():assert sha(out/'adjudication-reviews-r07'/name)==h,'adjudication drift '+name
        ex=load(out/'adjudication-export-r07.json')
        for e in ex['packets']:assert sha(out/'adjudication-packets-r07'/e['packet_file'])==e['packet_file_sha256']
        checks['adjudication']=dict(status='passed',packets=len(ex['packets']),verdicts=ai['verdicts'])
    integ=load(out/'visible-universe-integration-r06.json');assert integ['status']=='passed' and integ['map_sha256']==sha(m06)
    for name,h in mapping['visible_universe_review_bindings'].items():assert sha(out/'visible-universe-reviews-r06'/name)==h,'review drift '+name
    views=load(src/'source-views-prepared.json');text={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']}
    exported=load(out/'visible-universe-export-r06.json');binds={e['intent_id']:{b['segment_id']:b['span'] for b in e['segment_bindings']} for e in exported['packets']}
    quotes=0;reviewed=0
    for rec in mapping['records']:
        for req in rec['requirements']:
            r=req.get('visible_universe_review')
            if r is None:continue
            reviewed+=1
            for item in r['alternatives']+r['uncertain']:
                for s in item['review_spans']:
                    b=binds[rec['intent_id']][s['segment_id']];raw=text[k(b)][b['start']+s['start']:b['start']+s['end']]
                    assert raw==s['quote'] and b['start']+s['end']<=b['end'],'quote/source mismatch'
                    quotes+=1
                assert all_inside(item['source_spans'],intervals(r['universe_spans'])),'review span outside universe'
    checks['reviews']=dict(requirements=reviewed,quotes=quotes,status='passed')
    maps={r['intent_id']:r for r in mapping['records']}
    configs=sorted({s['configuration_id'] for s in scores['summaries']})
    counts={};cells=0
    for c in configs:
        ext=load(out/'verify-visible-extract'/(c+'.json'))
        assert ext['rankings_sha256']==scores['input_bindings'][c]['rankings.jsonl'] and ext['contexts_sha256']==scores['input_bindings'][c]['contexts.jsonl'],'extract/score input binding'
        saved={}
        for r in jl(out/('index-'+c)/f'score-details-e1-{rev}.jsonl'):
            if r['cell'] in CELLS:saved[(r['cell'],r['intent_id'])]=r['sufficient']
        mine={}
        for key_,spans in ext['visible'].items():
            cell,intent=key_.split('|');iv=intervals(spans);m=maps[intent]
            mine[(cell,intent)]=sufficient(m['groups'],{q['requirement_id']:req_status(q,spans,iv) for q in m['requirements']})
        bad=[x for x in mine if mine[x]!=saved.get(x)]
        assert set(mine)==set(saved) and not bad,f'{c}: {len(bad)} mismatches {bad[:3]}'
        cells+=len(mine)
        counts[c]={cell:{v:sum(1 for (cc,_),s in mine.items() if cc==cell and s==v) for v in ('yes','no','unknown')} for cell in CELLS}
    checks['score_cells']=dict(cells=cells,mismatches=0,status='passed',cells_checked=list(CELLS))
    with open(out/f'comparison-e1-{rev}.csv',encoding='utf-8-sig') as f:comp={r['configuration_id']:r for r in csv.DictReader(f)}
    for c,v in counts.items():
        for col,cell in (('CGC4K','fixed_budget_main/P0/4096/final'),('CGC8K','fixed_budget_main/P0/8192/final'),('CEGR10','layer1_raw/R4/10')):
            for lab in ('yes','no','unknown'):assert int(comp[c][f'{col}_{lab}'])==v[cell][lab],'comparison csv drift'
    checks['comparison_table']='passed'
    sel=load(out/f'candidate-selection-e1-{rev}.json');assert sel['equivalent_configs']==[]
    lat={r['configuration_id']:r['mean_r4_total_seconds'] for r in load(src/'costs-e1-r01.json')}
    M=[dict(id=c,l4=v['fixed_budget_main/P0/4096/final']['yes']/80,u4=(v['fixed_budget_main/P0/4096/final']['yes']+v['fixed_budget_main/P0/4096/final']['unknown'])/80,l10=v['layer1_raw/R4/10']['yes']/80,u10=(v['layer1_raw/R4/10']['yes']+v['layer1_raw/R4/10']['unknown'])/80,t=lat[c]) for c,v in counts.items() if not c.startswith('B0')]
    M.sort(key=lambda r:(-r['l4'],-r['l10'],r['t'],r['id']))
    def before(x,y):
        if x['l4']!=y['u4']:return x['l4']>y['u4']
        if x['l10']!=y['u10']:return x['l10']>y['u10']
        return (x['t'],x['id'])<(y['t'],y['id'])
    chosen=[];rest=list(M)
    while rest and len(chosen)<2 and all(before(rest[0],y) for y in rest[1:]):chosen.append(rest.pop(0)['id'])
    status='frozen' if len(chosen)==2 or not rest else 'pending_unknown'
    assert chosen==sel['selected'] and status==sel['status'] and [r['id'] for r in M]==sel['provisional_lower_bound_order'],'candidate rule mismatch'
    checks['candidate_rule']=dict(status='passed',selected=chosen,decision=status,order=[r['id'] for r in M])
    pres=load(preservation_path);assert pres['status']=='passed'
    large=set(p for v in pres['runs'].values() for p in v['large_files_checked_via_extract'])
    expected={}
    for run in ('pearl-chunking-dev80-20261005-05','pearl-chunking-dev80-20261005-06'):expected.update(load(ROOT/'outputs'/run/'delivery-manifest.json').get('artifacts_sha256') or {})
    ext_sha={}
    for c in configs:
        e=load(out/'verify-visible-extract'/(c+'.json'));ext_sha[f'outputs/pearl-chunking-dev80-20261005-05/index-{c}/rankings.jsonl']=e['rankings_sha256'];ext_sha[f'outputs/pearl-chunking-dev80-20261005-05/index-{c}/contexts.jsonl']=e['contexts_sha256']
    unchecked=[p for p in large if p not in ext_sha];drift=[p for p in large if p in ext_sha and ext_sha[p]!=expected[p]]
    assert not drift,'large file drift'
    checks['preservation']=dict(receipt=preservation_path.name,receipt_sha256=sha(preservation_path),large_rehashed=len(large)-len(unchecked),large_not_rehashed=sorted(unchecked))
    receipt=dict(status='passed',revision=rev,verifier=Path(__file__).name,verifier_sha256=sha(__file__),score_file_sha256=sha(out/f'scores-e1-{rev}.json'),mapping_sha256=sha(map_path),candidate_selection_sha256=sha(out/f'candidate-selection-e1-{rev}.json'),comparison_sha256=sha(out/f'comparison-e1-{rev}.csv'),checks=checks,counts=counts)
    with open(receipt_path,'x',encoding='utf8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n')
    print('verification passed',rev,checks['candidate_rule'],flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['extract','preserve','check']);p.add_argument('--source-run',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--config',action='append');p.add_argument('--revision',choices=['r06','r07'],default='r07');p.add_argument('--receipt',type=Path);p.add_argument('--preservation',type=Path)
    a=p.parse_args();src=a.source_run.resolve();out=a.output.resolve()
    if a.stage=='extract':extract(src,out,a.config)
    elif a.stage=='preserve':preserve(out,a.receipt)
    else:check(src,out,a.revision,a.receipt,a.preservation)

if __name__=='__main__':main()
