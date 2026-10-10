"""Frozen three-valued Layer 2 scoring; no retrieval or answer prediction."""
import argparse
import json
import math
import hashlib
import importlib.util
import random
import sys
from pathlib import Path

CONFIGS = ('C0-4096','C0-8192','C1-4096','C1-8192')
PAIRS = (('C1-4096','C0-4096'),('C1-8192','C0-8192'),('C0-8192','C0-4096'),('C1-8192','C1-4096'))
STATISTICS_VERSION = 'layer2-stratified-paired-bootstrap-r01'
BOOTSTRAP_REPLICATES = 10000
BOOTSTRAP_SEED = 20261004

def _percentile(values, fraction):
    ordered=sorted(values)
    index=(len(ordered)-1)*fraction
    floor=math.floor(index)
    remainder=index-floor
    return ordered[floor]*(1-remainder)+ordered[min(floor+1,len(ordered)-1)]*remainder

def bootstrap_intervals(rows):
    """Pre-result descriptive percentile envelopes, with unknown kept in both bounds."""
    lookup={(r['intent_id'],r['configuration']):r for r in rows}
    ids=sorted({r['intent_id'] for r in rows})
    if not ids or len(lookup)!=len(rows) or set(lookup)!={(i,c) for i in ids for c in CONFIGS}:
        raise ValueError('bootstrap requires a nonempty complete paired configuration matrix')
    strata={}
    vectors={}
    for i in ids:
        types={lookup[i,c]['question_type'] for c in CONFIGS}
        if len(types)!=1:
            raise ValueError('one stable question type required per intent cluster')
        strata.setdefault(next(iter(types)),[]).append(i)
        bounds={}
        for c in CONFIGS:
            status=lookup[i,c]['sufficient']
            if status not in ('yes','no','unknown'):
                raise ValueError('invalid bootstrap support status')
            bounds[c]=(int(status=='yes'),int(status!='no'))
        vector=[v for c in CONFIGS for v in bounds[c]]
        for a,b in PAIRS:
            vector.extend((bounds[a][0]-bounds[b][1],bounds[a][1]-bounds[b][0]))
        vectors[i]=vector
    n=len(ids)
    dimensions=len(vectors[ids[0]])
    samples=[[] for _ in range(dimensions)]
    ordered_strata=[strata[t] for t in sorted(strata)]
    rng=random.Random(BOOTSTRAP_SEED)
    for _ in range(BOOTSTRAP_REPLICATES):
        # One shared resample of clusters preserves all four configurations and contrasts.
        draw=[rng.choice(cluster_ids) for cluster_ids in ordered_strata for _ in cluster_ids]
        totals=[0]*dimensions
        for i in draw:
            for index,value in enumerate(vectors[i]):
                totals[index]+=value
        for index,total in enumerate(totals):
            samples[index].append(total/n)
    points=[sum(vectors[i][j] for i in ids)/n for j in range(dimensions)]
    def interval(index):
        lower_ci=[_percentile(samples[index],q) for q in (.025,.975)]
        upper_ci=[_percentile(samples[index+1],q) for q in (.025,.975)]
        return {'lower_bound_point':points[index],'upper_bound_point':points[index+1],
                'lower_bound_ci':lower_ci,'upper_bound_ci':upper_ci,
                'envelope':[lower_ci[0],upper_ci[1]]}
    supplement=Path(__file__).with_name('statistics-supplement.md')
    return {'statistics_version':STATISTICS_VERSION,'confidence_level':.95,
            'replicates':BOOTSTRAP_REPLICATES,'seed':BOOTSTRAP_SEED,'n':n,
            'stratum_sizes':{t:len(strata[t]) for t in sorted(strata)},
            'resampling_unit':'underlying_intent_cluster','quantile_method':'linear_interpolation_(B-1)*q',
            'purpose':'pre-summary descriptive uncertainty envelopes; not additional hypothesis tests',
            'python_version':sys.version.split()[0],
            'score_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'statistics_supplement_sha256':hashlib.sha256(supplement.read_bytes()).hexdigest() if supplement.exists() else None,
            'overall':{c:interval(j*2) for j,c in enumerate(CONFIGS)},
            'paired':[{'a':a,'b':b,**interval(len(CONFIGS)*2+j*2)} for j,(a,b) in enumerate(PAIRS)]}

def score_support(groups, support):
    if not groups or any(not g or len(g)!=len(set(g)) for g in groups):
        raise ValueError('nonempty unique requirement groups required')
    required = set().union(*map(set,groups))
    if not required <= support.keys() or any(support[r] not in ('yes','no','unknown') for r in required):
        raise ValueError('all requirements need explicit three-valued judgments')
    statuses = []
    for g in groups:
        labels = [support[r] for r in g]
        statuses.append('no' if 'no' in labels else 'yes' if all(v=='yes' for v in labels) else 'unknown')
    return {'sufficient':'yes' if 'yes' in statuses else 'no' if all(v=='no' for v in statuses) else 'unknown',
            'coverage_lower':max(sum(support[r]=='yes' for r in g)/len(g) for g in groups),
            'coverage_upper':max(sum(support[r]!='no' for r in g)/len(g) for g in groups)}

def aggregate(rows):
    n = len(rows)
    counts = {v:sum(r['sufficient']==v for r in rows) for v in ('yes','no','unknown')}
    active = [r['unit_labels'] for r in rows if r['unit_labels']]
    if any(v not in ('relevant','irrelevant','mixed','unknown') for labels in active for v in labels):
        raise ValueError('invalid unit label')
    out = {'n':n, **counts,'complete_group_lower':counts['yes']/n if n else None,
           'complete_group_upper':(counts['yes']+counts['unknown'])/n if n else None,
           'coverage_lower':sum(r['coverage_lower'] for r in rows)/n if n else None,
           'coverage_upper':sum(r['coverage_upper'] for r in rows)/n if n else None,
           'relevance_applicable_n':len(active),'unit_n':sum(map(len,active)),
           'unknown_unit_n':sum(labels.count('unknown') for labels in active)}
    for metric, positive in [('relevance',{'relevant','mixed'}),('noise',{'irrelevant','mixed'})]:
        out[metric+'_lower'] = sum(sum(v in positive for v in labels)/len(labels) for labels in active)/len(active) if active else None
        out[metric+'_upper'] = sum(sum(v in positive or v=='unknown' for v in labels)/len(labels) for labels in active)/len(active) if active else None
    return out

def exact_mcnemar(gain, loss):
    n = gain+loss
    return min(1.0, 2*sum(math.comb(n,k) for k in range(min(gain,loss)+1))/(2**n)) if n else 1.0

def holm(values):
    out = [None]*len(values)
    previous = 0.0
    for rank,index in enumerate(sorted(range(len(values)),key=lambda i:values[i])):
        previous = max(previous,min(1.0,(len(values)-rank)*values[index]))
        out[index] = previous
    return out

def paired(rows, a, b):
    lookup = {(r['intent_id'],r['configuration']):r for r in rows}
    ids = sorted({r['intent_id'] for r in rows})
    if any((i,c) not in lookup for i in ids for c in (a,b)):
        raise ValueError('paired configurations missing')
    gain=loss=unknown=0
    lower=upper=0
    for i in ids:
        av,bv = lookup[i,a]['sufficient'],lookup[i,b]['sufficient']
        unknown += 'unknown' in (av,bv)
        gain += av=='yes' and bv=='no'
        loss += av=='no' and bv=='yes'
        lower += int(av=='yes')-int(bv!='no')
        upper += int(av!='no')-int(bv=='yes')
    return {'a':a,'b':b,'n':len(ids),'unknown_pairs':unknown,'resolved_pairs':len(ids)-unknown,
            'gain':gain,'loss':loss,'delta_lower':lower/len(ids),'delta_upper':upper/len(ids),
            'exact_mcnemar_p_resolved':exact_mcnemar(gain,loss)}

def score_records(contexts, packets, bindings, reviews, expected_n=None):
    packet_map = {p['packet_id']:p for p in packets}
    review_map = {r['packet_id']:r for r in reviews}
    binding_map = {(b['context_id'],b['stage']):b for b in bindings}
    if len(packet_map)!=len(packets) or len(review_map)!=len(reviews) or len(binding_map)!=len(bindings):
        raise ValueError('duplicate packet, review, or binding')
    if set(review_map)!=set(packet_map):
        raise ValueError('review set must exactly match packet set')
    review_spec=importlib.util.spec_from_file_location('evidence_review_validation',Path(__file__).with_name('review.py'))
    review_module=importlib.util.module_from_spec(review_spec)
    review_spec.loader.exec_module(review_module)
    for p in packets:
        body={k:v for k,v in p.items() if k not in ('packet_id','packet_sha256')}
        if review_module.sha_text(review_module.canonical(body))!=p['packet_sha256']:
            raise ValueError('packet content hash mismatch')
        review_module.validate_review(p,review_map[p['packet_id']])
    if len({c['context_id'] for c in contexts})!=len(contexts):
        raise ValueError('duplicate contexts')
    ids={c['intent_id'] for c in contexts}
    if expected_n is not None and len(ids)!=expected_n:
        raise ValueError('intent denominator differs from frozen expected N')
    if len(contexts)!=len(ids)*4 or any(c['configuration'] not in CONFIGS for c in contexts):
        raise ValueError('four-configuration matrix required')
    rows = []
    step_rows=[]
    for c in contexts:
        if hashlib.sha256(c['serialized_context'].encode('utf-8')).hexdigest()!=c['text_sha256']:
            raise ValueError('saved context hash mismatch')
        binding = binding_map[c['context_id'],'final']
        if binding['original_text_sha256']!=c['text_sha256']:
            raise ValueError('context binding mismatch')
        p = packet_map[binding['packet_id']]
        r = review_map[p['packet_id']]
        if r['packet_sha256']!=p['packet_sha256']:
            raise ValueError('review binding mismatch')
        support = {k:v['label'] for k,v in r['support'].items()}
        result = score_support(p['allowed_groups'],support)
        rows.append({'context_id':c['context_id'],'intent_id':c['intent_id'],'configuration':c['configuration'],
                     'question_type':c.get('question_type',c.get('main_stratum','unknown')),
                     'packet_id':p['packet_id'],'text_sha256':c['text_sha256'],'support':support,
                     'unit_labels':[r['unit_labels'][u['unit_id']] for u in p['units']], **result})
        for stage,view in [*c.get('steps',{}).items(),('final',c)]:
            bound=binding_map.get((c['context_id'],stage))
            if not bound:
                raise ValueError('step binding missing')
            digest=hashlib.sha256(view['serialized_context'].encode('utf-8')).hexdigest()
            if digest!=view['text_sha256'] or digest!=bound['original_text_sha256']:
                raise ValueError('step binding mismatch')
            step_packet=packet_map[bound['packet_id']]
            step_review=review_map[bound['packet_id']]
            step_support={k:v['label'] for k,v in step_review['support'].items()}
            step_rows.append({'context_id':c['context_id'],'stage':stage,'packet_id':step_packet['packet_id'],
                              'text_sha256':digest,'support':step_support, **score_support(step_packet['allowed_groups'],step_support)})
    comparisons = [paired(rows,*p) for p in PAIRS]
    for c,p in zip(comparisons,holm([c['exact_mcnemar_p_resolved'] for c in comparisons])):
        c['holm_p_resolved'] = p
    return {'rows':rows,'overall':{c:aggregate([r for r in rows if r['configuration']==c]) for c in CONFIGS},
            'by_type':{t:{c:aggregate([r for r in rows if r['configuration']==c and r['question_type']==t]) for c in CONFIGS} for t in sorted({r['question_type'] for r in rows})},
            'paired':comparisons,'step_rows':step_rows,'attribution':attribute_steps(step_rows),
            'bootstrap_ci':bootstrap_intervals(rows)}

def attribute_steps(rows):
    lookup={(r['context_id'],r['stage']):r for r in rows}
    changes=[]
    for cid in sorted({r['context_id'] for r in rows}):
        for before,after in [('raw','expanded'),('expanded','deduplicated'),('deduplicated','final')]:
            if (cid,before) not in lookup or (cid,after) not in lookup:
                continue
            a,b=lookup[cid,before],lookup[cid,after]
            requirements=set(a['support'])|set(b['support'])
            changes.append({'context_id':cid,'before_stage':before,'after_stage':after,
                            'before_status':a['sufficient'],'after_status':b['sufficient'],
                            'requirement_gains':sorted(r for r in requirements if a['support'][r]=='no' and b['support'][r]=='yes'),
                            'requirement_losses':sorted(r for r in requirements if a['support'][r]=='yes' and b['support'][r]=='no'),
                            'unknown_requirements':sorted(r for r in requirements if 'unknown' in (a['support'][r],b['support'][r]))})
    return changes

def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]

def main():
    parser=argparse.ArgumentParser()
    for name in ('contexts','packets','bindings','reviews','output'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--expected-n',type=int,default=80)
    args=parser.parse_args()
    result=score_records(*(read_jsonl(getattr(args,n)) for n in ('contexts','packets','bindings','reviews')),expected_n=args.expected_n)
    with Path(args.output).open('x',encoding='utf-8') as out:
        json.dump(result,out,ensure_ascii=False,indent=2)
    digest=lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    manifest={'expected_n':args.expected_n,'input_artifacts':{n:{'path':str(Path(getattr(args,n)).resolve()),'sha256':digest(getattr(args,n))} for n in ('contexts','packets','bindings','reviews')},
              'code_sha256':digest(__file__),'review_code_sha256':digest(Path(__file__).with_name('review.py')),
              'output_path':str(Path(args.output).resolve()),'output_sha256':digest(args.output),
              'statistical_family':[list(pair) for pair in PAIRS],
              'statistics_version':STATISTICS_VERSION,'statistics_supplement_sha256':result['bootstrap_ci']['statistics_supplement_sha256'],
              'bootstrap_replicates':BOOTSTRAP_REPLICATES,'bootstrap_seed':BOOTSTRAP_SEED,'human_verified':False}
    with Path(str(args.output)+'.manifest.json').open('x',encoding='utf-8') as out:
        json.dump(manifest,out,ensure_ascii=False,indent=2)

if __name__=='__main__':
    main()
