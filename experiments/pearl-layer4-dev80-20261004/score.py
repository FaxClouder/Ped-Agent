"""Frozen Layer 4 denominators; semantic labels must come from actual reviews."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json

def ratio(n,d): return n/d if d else None
def mean(values):
    values=[x for x in values if x is not None]
    return sum(values)/len(values) if values else None

def claim_metrics(labels, facts, extraction_unknown=False):
    if any(x not in {'supported','partial','unsupported','contradicted','unknown'} for x in labels): raise ValueError('invalid grounding label')
    if len(labels)!=len(facts) or any(x not in {'true','false','unknown'} for x in facts): raise ValueError('invalid factuality labels')
    n=len(labels); c=Counter(labels); f=Counter(facts)
    bounds=lambda lo,hi: [ratio(lo,n),ratio(hi,n)] if not extraction_unknown else [None,None]
    return dict(N=n,grounding_counts=dict(c),factuality_counts=dict(f),extraction_unknown=extraction_unknown,
        faithfulness=bounds(c['supported'],c['supported']+c['unknown']),
        unsupported_rate=bounds(c['partial']+c['unsupported']+c['contradicted'],n-c['supported']),
        context_contradiction_rate=bounds(c['contradicted'],c['contradicted']+c['unknown']),
        partial_rate=ratio(c['partial'],n) if not extraction_unknown else None,missing_rate=ratio(c['unsupported'],n) if not extraction_unknown else None,
        factuality=bounds(f['true'],f['true']+f['unknown']),
        factuality_resolved_accuracy=ratio(f['true'],f['true']+f['false']) if not extraction_unknown else None,
        factuality_coverage=ratio(f['true']+f['false'],n) if not extraction_unknown else None,fact_conflict_rate=ratio(f['false'],n) if not extraction_unknown else None)

def citation_metrics(claim_ids,pairs,extraction_unknown=False):
    ids=set(claim_ids)
    if len(ids)!=len(claim_ids): raise ValueError('duplicate claim ids')
    if any(p['claim_id'] not in ids for p in pairs): raise ValueError('pair claim absent')
    labels={'supported','partial','unsupported','contradicted','unknown','invalid','outside-context'}
    if any(p['label'] not in labels for p in pairs): raise ValueError('invalid citation label')
    supported={p['claim_id'] for p in pairs if p['label']=='supported'}
    possible=supported|{p['claim_id'] for p in pairs if p['label']=='unknown'}
    c=Counter(p['label'] for p in pairs); n=len(pairs)
    return dict(pair_N=n,claim_N=len(ids),counts=dict(c),precision=[ratio(c['supported'],n),ratio(c['supported']+c['unknown'],n)] if not extraction_unknown else [None,None],
        recall=[ratio(len(supported),len(ids)),ratio(len(possible),len(ids))] if not extraction_unknown else [None,None])

def reliability_metrics(rows):
    counts=Counter(); unknown=[]
    for r in rows:
        a=r['answerability']; b=r['abstain']
        if a not in {'complete','partial','none','unknown'}: raise ValueError('bad answerability')
        if b is not None and type(b) is not bool: raise ValueError('abstain must be boolean or None')
        if a=='unknown' or b is None: unknown.append(r); continue
        if type(b) is not bool: raise ValueError('abstain must be boolean or None')
        counts[('T' if a!='complete' else 'F')+'P' if b else ('F' if a!='complete' else 'T')+'N']+=1
    tp,fp,fn,tn=(counts[k] for k in ('TP','FP','FN','TN'))
    # Enumerate feasible contingency tables for unknown cells; bounded size 400.
    feasible={(tp,fp,fn,tn)}
    for r in unknown:
        classes=['complete','partial'] if r['answerability']=='unknown' else [r['answerability']]
        actions=[True,False] if r['abstain'] is None else [r['abstain']]
        options=set((0 if a!='complete' and b else 1 if a=='complete' and b else 2 if a!='complete' else 3) for a in classes for b in actions)
        feasible={tuple(v+(i==j) for j,v in enumerate(t)) for t in feasible for i in options}
        if len(feasible)>100000:
            # Conservative full range rather than inventing a resolved assignment.
            feasible=None; break
    funcs=dict(precision=lambda t:ratio(t[0],t[0]+t[1]),recall=lambda t:ratio(t[0],t[0]+t[2]),f1=lambda t:ratio(2*t[0],2*t[0]+t[1]+t[2]),false_answer_rate=lambda t:ratio(t[2],t[0]+t[2]),false_refusal_rate=lambda t:ratio(t[1],t[1]+t[3]))
    result=dict(TP=tp,FP=fp,FN=fn,TN=tn,total_cells=len(rows),resolved_cells=len(rows)-len(unknown),unknown_cells=len(unknown),coverage=ratio(len(rows)-len(unknown),len(rows)),answerability_counts=dict(Counter(r['answerability'] for r in rows)))
    for name,fun in funcs.items():
        result[name]=fun((tp,fp,fn,tn))
        vals=[fun(t) for t in feasible] if feasible is not None else [0.,1.]
        defined=[x for x in vals if x is not None]
        result[name+'_bounds']=[min(defined),max(defined)] if defined else [None,None]
        result[name+'_may_be_na']=any(x is None for x in vals)
    return result

def score(reviewed:dict,old_l3:dict,out:Path):
    old={(r['intent_id'],r['arm']):r for r in old_l3['rows']}
    rows=[]
    for r in reviewed['rows']:
        claims=r['claims']; labels=[c['grounding']['label'] for c in claims]; facts=[c['factuality']['label'] for c in claims]
        previous=old[(r['intent_id'],r['arm'])]
        row={k:r[k] for k in ('cell_id','intent_id','arm','stratum','answerability','behavior','abstain','reason')}
        row.update(claim_metrics(labels,facts,r.get('extraction_unknown',False)))
        row['citation']=citation_metrics([c['claim_id'] for c in claims],r['citation_pairs'],r.get('citation_extraction_unknown',False))
        if r.get('extraction_unknown',False): row['citation']['recall']=[None,None]
        row['old_strict']=previous['strict']; rows.append(row)
    summaries={}
    for arm in sorted({r['arm'] for r in rows}):
        subset=[r for r in rows if r['arm']==arm]
        summaries[arm]=summarize(subset)
        summaries[arm]['strata']={s:summarize([r for r in subset if r['stratum']==s]) for s in sorted({r['stratum'] for r in subset})}
    result=dict(schema_version='pearl-layer4-score-v1',rows=rows,arms=summaries)
    with Path(out).open('x',encoding='utf-8') as stream: json.dump(result,stream,ensure_ascii=False,indent=2)
    return result

def summarize(rows):
    result=dict(cell_N=len(rows),claim_N=sum(r['N'] for r in rows),claim_na=sum(r['faithfulness'][0] is None for r in rows),extraction_unknown_cells=sum(r['extraction_unknown'] for r in rows))
    for metric in ('faithfulness','unsupported_rate','context_contradiction_rate','factuality'):
        result[metric+'_macro']=[mean([r[metric][j] for r in rows]) for j in (0,1)]
        eligible=[r for r in rows if r[metric][0] is not None]
        denom=sum(r['N'] for r in eligible)
        result[metric+'_micro']=[ratio(sum(r[metric][j]*r['N'] for r in eligible),denom) for j in (0,1)]
    result['factuality_coverage_macro']=mean([r['factuality_coverage'] for r in rows])
    known=[r for r in rows if not r['extraction_unknown']]
    result['factuality_coverage_micro']=ratio(sum(sum(r['factuality_counts'].get(k,0) for k in ('true','false')) for r in known),sum(r['N'] for r in known))
    result['grounding_counts']=dict(sum((Counter(r['grounding_counts']) for r in rows),Counter()))
    result['factuality_counts']=dict(sum((Counter(r['factuality_counts']) for r in rows),Counter()))
    for metric,denom in (('precision','pair_N'),('recall','claim_N')):
        result['citation_'+metric+'_macro']=[mean([r['citation'][metric][j] for r in rows]) for j in (0,1)]
        eligible=[r for r in rows if r['citation'][metric][0] is not None]
        result['citation_'+metric+'_micro']=[ratio(sum(r['citation'][metric][j]*r['citation'][denom] for r in eligible),sum(r['citation'][denom] for r in eligible)) for j in (0,1)]
        result['citation_'+metric+'_na']=sum(r['citation'][metric][0] is None for r in rows)
    result['citation_pair_N']=sum(r['citation']['pair_N'] for r in rows)
    result['reliability']=reliability_metrics(rows)
    result['behavior_counts']=dict(Counter(r['behavior'] for r in rows))
    reasons=[r['reason'] for r in rows if r['reason']!='na']
    result['reason_counts']=dict(Counter(reasons)); result['reason_accuracy']=ratio(reasons.count('correct'),sum(x!='unknown' for x in reasons))
    complete=[r for r in rows if r['answerability']=='complete']
    result['complete_strict']=dict(N=len(complete),correct=sum(r['old_strict']=='yes' for r in complete),rate=ratio(sum(r['old_strict']=='yes' for r in complete),len(complete)))
    joint=Counter()
    for r in rows:
        support='fully_supported' if r['N'] and r['grounding_counts'].get('supported',0)==r['N'] and not r['extraction_unknown'] else 'not_fully_supported' if r['N'] else 'no_claims'
        joint['|'.join((r['answerability'],r['behavior'],r['old_strict'],support))]+=1
    result['joint_counts']=dict(joint)
    return result
