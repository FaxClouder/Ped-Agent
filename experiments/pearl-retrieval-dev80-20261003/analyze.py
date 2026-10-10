"""Exploratory dev80 statistics and evidence-limited failure diagnostics."""
from __future__ import annotations

import argparse
import math
from collections import Counter, defaultdict
from pathlib import Path
import platform

import numpy as np

from protocol import score_prefix
from score import GOLD, METHODS, build_details, load_validated_inputs, read, rows, sha, write

SEED = 20260929
REPEATS = 10000
METRICS = ('CEGR', 'BestGroupCov', 'CompleteRR')
COMPARISONS = (('R2','R1'), ('R3','R2'), ('R4','R3'), ('R3','R1'))


def exact_mcnemar(b, c):
    n=b+c
    if not n:return 1.0
    return min(1.0, 2.0 * sum(math.comb(n,k) for k in range(min(b,c)+1)) / 2**n)


def holm(p_values):
    order=sorted(range(len(p_values)),key=lambda i:p_values[i])
    result=[None]*len(order);running=0.0
    for rank,index in enumerate(order):
        running=max(running,min(1.0,(len(order)-rank)*p_values[index]))
        result[index]=running
    return result


def source_components(intents):
    """Connected components of shared-source intent graph, preserving cross strata."""
    parent={q['intent_id']:q['intent_id'] for q in intents}
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    owner={}
    for q in intents:
        for source in {a['source_id'] for a in q['atoms']}:
            if source in owner:
                parent[find(q['intent_id'])]=find(owner[source])
            else:owner[source]=q['intent_id']
    components=defaultdict(list)
    for q in intents:components[find(q['intent_id'])].append(q['intent_id'])
    return sorted((sorted(v) for v in components.values()),key=lambda v:(-len(v),v))


def stratified_bootstrap(values, strata, repeats=REPEATS, seed=SEED):
    """Each sampled row contains all method and metric values, keeping pairs intact."""
    values=np.asarray(values,dtype=float)
    if values.shape[0]!=len(strata):raise ValueError('bootstrap strata size')
    rng=np.random.default_rng(seed)
    dist=np.zeros((repeats,)+values.shape[1:],dtype=float)
    for h in sorted(set(strata)):
        indices=np.array([i for i,label in enumerate(strata) if label==h])
        sample=rng.choice(indices,size=(repeats,len(indices)),replace=True)
        dist+=values[sample].mean(axis=1)*(len(indices)/len(strata))
    return dist


def interval(distribution):
    distribution=np.asarray(distribution,dtype=float)
    bounds=np.quantile(distribution,[.025,.975],method='linear')
    return dict(low=float(bounds[0]),high=float(bounds[1]),
                degenerate=bool(np.all(distribution==distribution[0])))


def cluster_sensitivity(values,intents,components,repeats=REPEATS,seed=SEED):
    """Resample entire components; weights remain frozen N_h/N even across strata."""
    by_id={q['intent_id']:i for i,q in enumerate(intents)}
    labels=[q['main_stratum'] for q in intents]
    group_indices=[np.array([by_id[ident] for ident in group]) for group in components]
    h_indices={h:np.array([i for i,label in enumerate(labels) if label==h]) for h in sorted(set(labels))}
    # Precompute each connected component's stratum counts and sums.
    counts=np.zeros((len(components),len(h_indices)))
    sums=np.zeros((len(components),len(h_indices))+values.shape[1:])
    weights=[]
    for hi,(h,indices) in enumerate(h_indices.items()):
        weights.append(len(indices)/len(intents))
        for ci,group in enumerate(group_indices):
            selected=np.intersect1d(group,indices)
            counts[ci,hi]=len(selected)
            sums[ci,hi]=values[selected].sum(axis=0)
    rng=np.random.default_rng(seed)
    distributions=[];invalid=0
    for _ in range(repeats):
        chosen=rng.integers(0,len(components),size=len(components))
        denom=counts[chosen].sum(axis=0)
        if np.any(denom==0):invalid+=1;continue
        selected_sums=sums[chosen].sum(axis=0)
        distributions.append(sum(weights[h]*selected_sums[h]/denom[h] for h in range(len(weights))))
    enough=len(components)>=10 and max(map(len,components))<.5*len(intents) and invalid<=.05*repeats
    result=dict(cluster_count=len(components),maximum_cluster_size=max(map(len,components)),
                valid_repeats=len(distributions),unestimable_repeats=invalid,
                weighting='fixed original stratum N_h/N; whole connected source components',
                CI_reportable=enough,
                limitation=None if enough else 'Few/large source components or missing-stratum draws; descriptive sensitivity only, no precise cluster CI.')
    if distributions:
        dist=np.stack(distributions)
        result['bootstrap_mean_range']={m:dict(low=float(dist[:,i,0].min()),high=float(dist[:,i,0].max())) for i,m in enumerate(METHODS)}
        if enough:
            result['method_CEGR_CI']={m:interval(dist[:,i,0]) for i,m in enumerate(METHODS)}
            result['difference_CEGR_CI']={a+'-'+b:interval(dist[:,METHODS.index(a),0]-dist[:,METHODS.index(b),0]) for a,b in COMPARISONS}
    return result


def depth_state(gold,decision,ranking,k):
    """Known positive paths prove presence; unknown deeper content forbids negatives."""
    ranking=ranking[:k]
    result=score_prefix(gold,decision['atom_paths'],ranking,k)
    reviewed=set(decision['reviewed_ids'])
    unknown=sorted(set(ranking)-reviewed)
    positive=bool(result['CEGR'])
    first=result['first_complete_rank']
    exact_first=first if first is not None and set(ranking[:first])<=reviewed else None
    return dict(state='known_complete' if positive else ('unresolved' if unknown else 'reviewed_incomplete'),
                complete=True if positive else (None if unknown else False),
                all_depth_reviewed=not unknown,unresolved_ids=unknown,
                first_complete_rank=exact_first,
                first_complete_rank_upper_bound=first,
                BestGroupCov=result['BestGroupCov'] if not unknown or positive else None,
                BestGroupCov_known_lower_bound=result['BestGroupCov'],
                requirements_hit_known=result['requirements_hit'])


def statistics(inputs,details):
    intents=list(inputs['gold']['intents']);by={(d['intent_id'],d['method']):d for d in details}
    values=np.array([[[by[q['intent_id'],m]['scores']['10'][metric] for metric in METRICS] for m in METHODS] for q in intents])
    labels=[q['main_stratum'] for q in intents]
    dist=stratified_bootstrap(values,labels)
    means=values.mean(axis=0)
    summary={m:{metric:dict(mean=float(means[mi,ki]),CI=interval(dist[:,mi,ki]))
                for ki,metric in enumerate(METRICS)} for mi,m in enumerate(METHODS)}
    for m in METHODS:summary[m]['CEGR']['successes']=int(values[:,METHODS.index(m),0].sum())
    comparisons={};ps=[]
    for a,b in COMPARISONS:
        ai,bi=METHODS.index(a),METHODS.index(b)
        b_count=int(np.sum((values[:,ai,0]==1)&(values[:,bi,0]==0)))
        c_count=int(np.sum((values[:,ai,0]==0)&(values[:,bi,0]==1)))
        result=dict(preset=a+'-'+b!='R3-R1',interpretation='exploratory development diagnostic; not confirmatory significance',
                    b=b_count,c=c_count,metrics={})
        for ki,metric in enumerate(METRICS):
            result['metrics'][metric]=dict(mean_difference=float(means[ai,ki]-means[bi,ki]),
                CI=interval(dist[:,ai,ki]-dist[:,bi,ki]),
                strata={h:float((values[:,ai,ki]-values[:,bi,ki])[np.array(labels)==h].mean()) for h in sorted(set(labels))})
        result['CEGR_difference_percentage_points']=100*result['metrics']['CEGR']['mean_difference']
        if result['preset']:
            result['exact_McNemar_p']=exact_mcnemar(b_count,c_count);ps.append(result['exact_McNemar_p'])
        comparisons[a+'-'+b]=result
    adjusted=holm(ps)
    for key,p in zip(['R2-R1','R3-R2','R4-R3'],adjusted):comparisons[key]['Holm_adjusted_p']=p
    components=source_components(intents)
    source_counts=Counter(source for q in intents for source in {a['source_id'] for a in q['atoms']})
    source_n=sum(source_counts.values())
    dependence=dict(source_intent_counts=dict(sorted(source_counts.items())),
        distinct_sources=len(source_counts),source_intent_incidence_count=source_n,
        maximum_intents_per_source=max(source_counts.values()),
        source_incidence_HHI=sum((n/source_n)**2 for n in source_counts.values()),
        components=components,component_definition='any shared Gold source; transitive connections retained across strata',
        sensitivity=cluster_sensitivity(values,intents,components))
    return dict(N=len(intents),method_statistics=summary,comparisons=comparisons,source_dependence=dependence,
                bootstrap=dict(repeats=REPEATS,seed=SEED,unit='paired intent vector',stratum_weights={h:labels.count(h)/len(labels) for h in sorted(set(labels))},
                               quantiles=[.025,.975],quantile_method='numpy linear',paired_CI='marginal, not simultaneous or Holm-adjusted'),
                software=dict(python=platform.python_version(),numpy=np.__version__),
                interpretation='Exploratory 80-intent development diagnostics. Source dependence limits inference; no sealed-evaluation or confirmatory significance claim.')


def validate_unions(inputs):
    path=inputs['directory']/'rrf_union.jsonl'
    records=rows(path);by={r['intent_id']:r for r in records}
    if len(by)!=len(records) or set(by)!=set(inputs['q_by']):raise ValueError('RRF union intent coverage')
    for ident,record in by.items():
        if record.get('pass_number',1)!=1 or record['query']!=inputs['q_by'][ident]['query']:
            raise ValueError('RRF union identity')
        union=record['union'];ids=[c['chunk_id'] for c in union]
        r1=[c['chunk_id'] for c in inputs['ranks'][ident,'R1']['results']]
        r2=[c['chunk_id'] for c in inputs['ranks'][ident,'R2']['results']]
        r3=[c['chunk_id'] for c in inputs['ranks'][ident,'R3']['results']]
        if len(ids)!=len(set(ids)) or set(ids)!=set(r1)|set(r2) or ids[:100]!=r3:
            raise ValueError('RRF union candidate/truncation mismatch')
    return by


def failures(inputs,details):
    by={(d['intent_id'],d['method']):d for d in details}
    unions=validate_unions(inputs)
    source_children=defaultdict(set)
    for c in inputs['children'].values():source_children[c['source_id']].add(c['chunk_id'])
    output=[]
    for ident,q in inputs['q_by'].items():
        decision=inputs['decisions'][ident];reviewed=set(decision['reviewed_ids'])
        ranks={m:[c['chunk_id'] for c in inputs['ranks'][ident,m]['results']] for m in METHODS}
        depths={m:depth_state(q,decision,ranks[m],100) for m in METHODS}
        union_ids=[c['chunk_id'] for c in unions[ident]['union']]
        union=depth_state(q,decision,union_ids,len(union_ids))
        reference_ids=sorted(set().union(*(source_children[a['source_id']] for a in q['atoms'])))
        reference=depth_state(q,decision,reference_ids,len(reference_ids))
        reference['first_complete_rank']=None
        reference['first_complete_rank_upper_bound']=None
        reference['ordering']='unranked reference-source child set; no retrieval completion rank'
        reference['all_Gold_source_children_reviewed']=set(reference_ids)<=reviewed
        full100=depths['R3']['all_depth_reviewed'] and depths['R4']['all_depth_reviewed']
        invariance=None
        if full100:
            a=score_prefix(q,decision['atom_paths'],ranks['R3'],100)
            b=score_prefix(q,decision['atom_paths'],ranks['R4'],100)
            invariance=(a['CEGR']==b['CEGR'] and a['BestGroupCov']==b['BestGroupCov'])
            if not invariance:raise ValueError('reviewed R3/R4 coverage invariant violation')
        for method in METHODS:
            cell=by[ident,method];miss=cell['scores']['10']['CEGR']==0;tags=[]
            if miss:
                if depths[method]['complete'] is True:tags.append('R_TOPK')
                if method=='R4' and by[ident,'R3']['scores']['10']['CEGR']==1:tags.append('R_RERANK_LOSS')
                if method in ('R3','R4') and union['complete'] is True and depths['R3']['complete'] is False:tags.append('R_FUSION_CUTOFF')
                # Whole-source positive identity review is required before absence claims.
                channels_complete=depths['R1']['all_depth_reviewed'] and depths['R2']['all_depth_reviewed']
                if reference['all_Gold_source_children_reviewed'] and reference['complete'] is True and channels_complete:
                    joined=depth_state(q,decision,ranks['R1']+ranks['R2'],200)
                    if joined['complete'] is False:tags.append('R_CANDIDATE_UNOBSERVED')
                if not tags:tags.append('UNRESOLVED')
            hit_atoms=cell['scores']['10']['atoms_hit']
            output.append(dict(intent_id=ident,method=method,main_stratum=q['main_stratum'],
                CEGR_at10=cell['scores']['10']['CEGR'],failure_tags=tags,
                missing_requirements_by_group=cell['scores']['10']['missing_requirements_by_group'],
                missing_atoms=[a for a,hit in hit_atoms.items() if not hit],
                stage_observations=dict(reference_source_children=reference,r1_at100=depths['R1'],r2_at100=depths['R2'],
                    rrf_union=union,r3_at100=depths['R3'],r4_at100=depths['R4'],method_at100=depths[method]),
                structural_R3_R4_candidate_identity='validated',coverage_at100_invariance=invariance,
                accepted_path_evidence=decision['path_evidence'],rejection_summary=decision['rejection_summary'],review_notes=decision['notes'],
                limitation='Known complete paths prove presence; unresolved depth prevents negative absence or exact first-completion claims. Parsing/chunking/index loss require separate canonical/source evidence; no automated attribution here. Layer 2 not executed.'))
    return dict(status='exploratory_development_failure_diagnostics',intent_method_cells=len(output),
                failed_cells=sum(c['CEGR_at10']==0 for c in output),
                label_cell_counts=dict(Counter(t for c in output for t in c['failure_tags'])),
                label_counts_may_overlap=True,details=output)


def timing_analysis(inputs):
    records=rows(inputs['directory']/'query_timings.jsonl')
    if len(records)!=3*len(inputs['q_by']) or len({(r['intent_id'],r['pass_number']) for r in records})!=len(records):
        raise ValueError('timing complete three-pass coverage')
    if {(r['intent_id'],r['pass_number']) for r in records}!={(q,p) for q in inputs['q_by'] for p in (1,2,3)}:
        raise ValueError('timing unknown/missing pass identity')
    fields=sorted(set(k for r in records for k in r if k.endswith('_seconds')))
    summaries={}
    for key in fields:
        if any(key not in r for r in records):raise ValueError('timing stage missing')
        data=np.array([r[key] for r in records],dtype=float)
        if not np.isfinite(data).all() or np.any(data<0):raise ValueError('invalid timing')
        summaries[key]=dict(N=len(data),mean=float(data.mean()),p50=float(np.quantile(data,.5,method='linear')),
            p95=float(np.quantile(data,.95,method='linear')),
            by_pass={str(p):dict(p50=float(np.quantile([r[key] for r in records if r['pass_number']==p],.5,method='linear')),
                                p95=float(np.quantile([r[key] for r in records if r['pass_number']==p],.95,method='linear'))) for p in (1,2,3)})
    # Inspect actual records instead of inheriting a pilot's zero-truncation conclusion.
    dense=[];reranker=[]
    for p in (1,2,3):
        dense.extend(rows(inputs['directory']/f'pass-{p}/query_inputs.jsonl'))
        reranker.extend(rows(inputs['directory']/('model-inputs-r4.jsonl' if p==1 else f'pass-{p}/model-input-identities-r4.jsonl')))
    dense_bad=sum(bool(r['truncated']) for r in dense)
    r4_bad=sum(any(r.get(k) for k in ('query_truncated','child_truncated_initial','child_truncated_pair')) for r in reranker)
    if len(dense)!=len(records):raise ValueError('dense input audit coverage')
    expected_r4=sum(len(inputs['ranks'][q,'R3']['results']) for q in inputs['q_by'])*3
    if len(reranker)!=expected_r4:raise ValueError('R4 input audit coverage')
    if not all(r.get('actual_forward_inputs_verified') is True for r in dense+reranker):raise ValueError('actual forward input audit missing')
    return dict(timed_queries=len(records),warmup_excluded=True,passes=3,scoring_pass=1,stage_seconds=summaries,
        latency_protocol=inputs['run'].get('latency_protocol'),
        query_input_count=len(dense),query_truncated_count=dense_bad,
        reranker_input_count=len(reranker),reranker_truncated_count=r4_bad,
        actual_forward_inputs_verified=True,determinism=inputs['run'].get('determinism'),
        interpretation='Three runs are repeated latency/determinism measurements, never additional statistical intents. Instrumented/gross and audit-adjusted estimates retain their manifest definitions.')


def analyze(directory,mapping_path,score_path,gold_path=GOLD,output=None,failures_output=None):
    inputs=load_validated_inputs(directory,mapping_path,gold_path)
    scored=read(score_path);details=build_details(inputs)
    if scored['details']!=details or scored['mapping_sha256']!=sha(mapping_path) or scored['rankings_sha256']!=sha(Path(directory)/'rankings.jsonl'):
        raise ValueError('analysis scores disagree with frozen-input recomputation')
    diagnostics=failures(inputs,details)
    result=dict(status='agent_reviewed_preliminary_80_intent_development_analysis',run_id=inputs['run']['run_id'],
                gold_sha256=sha(gold_path),mapping_sha256=sha(mapping_path),score_sha256=sha(score_path),
                statistics=statistics(inputs,details),timing=timing_analysis(inputs),
                failure_summary={k:v for k,v in diagnostics.items() if k!='details'},
                unresolved_supplementary_per_intent={q:len(d['unresolved_ids']) for q,d in inputs['decisions'].items()},
                explicit_limits=['Agent review is preliminary, not human Gold.','200 independent evaluation intents remain sealed and unrun.',
                    'Source overlap reduces effective independent information; p values are exploratory development diagnostics.',
                    'No full-depth negative inference or R3/R4 coverage invariant assertion where deeper support remains unresolved.',
                    'The Gold alternative-complete-group aspirational quota was not met; no equivalent groups manufactured.',
                    'Parsing/chunking loss requires source/canonical audit, including dev034 glyph and dev035 word-order issues.'])
    write(output or Path(directory)/'development-analysis.json',result)
    write(failures_output or Path(directory)/'per-intent-failures.json',diagnostics)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--mapping',type=Path,required=True)
    parser.add_argument('--scores',type=Path,required=True)
    parser.add_argument('--gold',type=Path,default=GOLD)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--failures-output',type=Path)
    args=parser.parse_args()
    analyze(args.directory,args.mapping,args.scores,args.gold,args.output,args.failures_output)
