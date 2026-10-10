"""Offline E1 source-certificate scoring and frozen candidate rule; no inference."""
from __future__ import annotations
import argparse
import copy
import csv
import json
from pathlib import Path
import statistics
from runtime import ROOT, sha, cache_identity, save_json, save_rows, load_queries
from support import visible_support
from score import score_support, aggregate
from e1 import configurations

def rows(path):
    return [json.loads(line) for line in Path(path).read_text('utf8').splitlines() if line.strip()]

def integration_output_paths(output,revision='r04'):
    if revision not in ('r04','r05'):raise ValueError('unsupported integration revision')
    mapping=output/f'common-support-map-e1-{revision}.json'
    receipt=output/('source-review-integration.json' if revision=='r04' else f'source-review-integration-{revision}.json')
    return mapping,receipt

def merge_reviews(records, packets, reviews):
    """Require every supplied bundle judgment; certify only literal packet spans."""
    result=copy.deepcopy(records); lookup={r['intent_id']:r for r in result}
    packets_by_id={p['intent_id']:p for p in packets}
    expected={(p['intent_id'],r['requirement_id'],b['bundle_index']) for p in packets for r in p['requirements'] for b in r['bundles']}
    seen=set()
    for review in reviews:
        if not review.get('reviewer_id'):raise ValueError('explicit source reviewer required')
        for j in review['judgments']:
            key=(j['intent_id'],j['requirement_id'],j['bundle_index'])
            if key not in expected or key in seen:raise ValueError('unknown or duplicate review bundle')
            seen.add(key); packet=packets_by_id[j['intent_id']]
            if j['packet_sha256']!=packet['packet_sha256']:raise ValueError('review packet binding drift')
            req=next(r for r in packet['requirements'] if r['requirement_id']==j['requirement_id'])
            bundle=next(b for b in req['bundles'] if b['bundle_index']==j['bundle_index'])
            text={tuple(e[k] for k in ('doc_id','source_version','element_id')):e['text'] for e in bundle['sources']}
            if j['status'] not in ('yes','no','unknown') or not j.get('rationale'):raise ValueError('invalid semantic judgment')
            spans=j.get('necessary_spans',[])
            if j['status']=='yes' and not spans:raise ValueError('TRUE needs complete necessary source evidence')
            for s in spans:
                raw=text.get(tuple(s[k] for k in ('doc_id','source_version','element_id')))
                if raw is None or not isinstance(s['start'],int) or not isinstance(s['end'],int) or not 0<=s['start']<s['end']<=len(raw):raise ValueError('review cites invisible or invalid source span')
            target_req=next(r for r in lookup[j['intent_id']]['requirements'] if r['requirement_id']==j['requirement_id'])
            target=target_req['evidence_groups'][j['bundle_index']]
            target.update(status=j['status'],necessary_spans=spans,reviewer_id=review['reviewer_id'],rationale=j['rationale'],review_caveats=j.get('caveats',[]),review_packet_sha256=j['packet_sha256'])
    if seen!=expected:raise ValueError('incomplete explicit source review coverage')
    for i in packets_by_id:lookup[i]['review_status']='source_reviewed'
    return result

def integrate(output,revision='r04'):
    map_output,receipt_output=integration_output_paths(output,revision)
    base=json.loads((output/'common-support-map-r03.json').read_text('utf8'));packets=[];reviews=[];bindings={}
    for i in (1,2):
        p=output/f'source-review-packets-e1-{i}.json';r=output/f'source-reviews-e1-{i}-r02.json'
        if not r.exists():r=output/f'source-reviews-e1-{i}.json'
        packet=json.loads(p.read_text('utf8'));review=json.loads(r.read_text('utf8'))
        if review['input_packet_file_sha256']!=sha(p):raise ValueError('source review file SHA drift')
        for item in packet['records']:
            if cache_identity({k:v for k,v in item.items() if k!='packet_sha256'})!=item['packet_sha256']:raise ValueError('source packet content SHA drift')
        packets+=packet['records'];reviews.append(review);bindings[p.name]=sha(p);bindings[r.name]=sha(r)
    # Packet authenticity is rechecked against the frozen canonical-derived view.
    sources=json.loads((output/'source-views-prepared.json').read_text('utf8'))
    text={(e['doc_id'],e['source_version'],e['element_id']):e['text'] for v in sources for e in v['elements']}
    authority={r['intent_id']:r for r in base['records']}
    for p in packets:
        original=authority[p['intent_id']]
        if p['query']!=original['query'] or p['groups']!=original['groups']:raise ValueError('source packet/Gold intent identity drift')
        for req in p['requirements']:
            frozen=next(r for r in original['requirements'] if r['requirement_id']==req['requirement_id'])
            if any(req[k]!=frozen[k] for k in ('description','scope')) or {b['bundle_index'] for b in req['bundles']}!=set(range(len(frozen['evidence_groups']))):raise ValueError('source packet/Gold requirement or bundle structure drift')
            for bundle in req['bundles']:
                for e in bundle['sources']:
                    if text.get(tuple(e[k] for k in ('doc_id','source_version','element_id')))!=e['text']:raise ValueError('packet/frozen source authenticity drift')
    base['records']=merge_reviews(base['records'],packets,reviews)
    base.update(schema_version=f'e1-common-source-support-{revision}',previous_map_sha256=sha(output/'common-support-map-r03.json'),review_bindings=bindings,source_view_file_sha256=sha(output/'source-views-prepared.json'),legacy_chunk_labels_inherited=False)
    base.pop('map_sha256',None);base['map_sha256']=cache_identity(base)
    save_json(map_output,base)
    save_json(receipt_output,dict(status='passed',revision=revision,intents=len(base['records']),new_reviewed_intents=len(packets),bundles=sum(len(r['judgments']) for r in reviews),map_sha256=sha(map_output),review_bindings=bindings))

def prefix_metrics(ranked,mapping,k):
    prefix=[];states=[];first_yes=first_possible=None
    for rank,child in enumerate(ranked[:k],1):
        prefix+=child['core_spans']+child.get('overlap_spans',[])
        support=visible_support(prefix,mapping);values=score_support(mapping['groups'],support)
        states.append(dict(rank=rank,support=support,**values))
        if values['sufficient']=='yes' and first_yes is None:first_yes=rank
        if values['sufficient']!='no' and first_possible is None:first_possible=rank
    if not states:
        values=score_support(mapping['groups'],{r['requirement_id']:'no' for r in mapping['requirements']});support={r['requirement_id']:'no' for r in mapping['requirements']}
    return dict(support=support,**values,complete_rr_lower=1/first_yes if first_yes else 0.,complete_rr_upper=1/first_possible if first_possible else 0.,prefix_evidence=states)

def guaranteed_before(a,b):
    if a['cgc4_lower']>b['cgc4_upper']:return True
    if a['cgc4_lower']<b['cgc4_upper']:return False
    if a['cegr10_lower']>b['cegr10_upper']:return True
    if a['cegr10_lower']<b['cegr10_upper']:return False
    return (a['retrieval_mean_seconds'],a['configuration_id'])<(b['retrieval_mean_seconds'],b['configuration_id'])

def candidate_decision(metrics):
    ordered=sorted(metrics,key=lambda r:(-r['cgc4_lower'],-r['cegr10_lower'],r['retrieval_mean_seconds'],r['configuration_id']))
    selected=[];remaining=list(ordered)
    while remaining and len(selected)<2:
        a=remaining[0]
        if not all(guaranteed_before(a,b) for b in remaining[1:]):break
        selected.append(a['configuration_id']);remaining.pop(0)
    pending=bool(remaining and len(selected)<2)
    return dict(status='pending_unknown' if pending else 'frozen',selected=selected,provisional_lower_bound_order=[r['configuration_id'] for r in ordered],rule='4K CGC lower, R4 CEGR@10 lower, measured retrieval mean seconds, config_id; freeze only when unknown bounds cannot change order',pending_reason='Unknown possible bounds can change the next candidate; possible upper bounds are not scores.' if pending else None)

def execution_row(configuration_id,query_ids,rank_rows,context_rows,scored_detail_cells):
    query_ids=set(query_ids);expected_contexts={(intent,budget) for intent in query_ids for budget in (4096,8192)}
    rank_ids={r['intent_id'] for r in rank_rows};context_cells={(r['intent_id'],r['budget']) for r in context_rows}
    successful={r['intent_id'] for r in rank_rows if r.get('status')=='success' and r['intent_id'] in query_ids}
    exact_rank_coverage=len(rank_rows)==len(query_ids) and rank_ids==query_ids
    exact_context_coverage=len(context_rows)==len(expected_contexts) and context_cells==expected_contexts
    complete=exact_rank_coverage and successful==query_ids and exact_context_coverage
    return dict(configuration_id=configuration_id,planned_intents=len(query_ids),retrieved=len(successful),retrieval_failed=len(query_ids)-len(successful),planned_contexts=len(expected_contexts),assembled=len(context_cells & expected_contexts),assembly_failed=len(expected_contexts)-len(context_cells & expected_contexts),scored_detail_cells=scored_detail_cells,quality_unknown=None,status='scored' if complete else 'failed_or_partial',exact_ranking_coverage=exact_rank_coverage,exact_context_coverage=exact_context_coverage)

EQUIVALENCE_BASIS='identical canonical source partition, R1/R2/RRF-union/R3/R4 ranked source-text-score contracts, and actual P0 stage serialized text/spans at 4096/8192; configuration-derived chunk/context IDs ignored'

def _without_config_ids(value):
    if isinstance(value,dict):return {k:_without_config_ids(v) for k,v in value.items() if k not in ('chunk_id','seed_chunk_id','context_id','configuration_id')}
    if isinstance(value,list):return [_without_config_ids(v) for v in value]
    return value

def strict_equivalence_signatures(library,rank_rows,context_rows):
    partition=[{k:_without_config_ids(r.get(k)) for k in ('core_spans','overlap_spans','prefix_spans','text')} for r in library]
    ranking=[]
    for row in sorted(rank_rows,key=lambda r:r['intent_id']):
        if row.get('status')!='success':raise ValueError('strict equivalence requires successful rankings')
        ranking.append(dict(intent_id=row['intent_id'],status=row['status'],results={method:_without_config_ids(row['results'][method]) for method in ('R1','R2','R3','R4')},rrf_union=_without_config_ids(row['rrf_union'])))
    contexts=[]
    for row in sorted(context_rows,key=lambda r:(r['intent_id'],r['budget'])):
        contexts.append(dict(intent_id=row['intent_id'],budget=row['budget'],panel_id=row['panel_id'],strategy=row['strategy'],stages={stage:_without_config_ids(row[stage]) for stage in ('raw','expanded','deduplicated','final')},truncation=_without_config_ids(row['truncation'])))
    result=dict(source_partition_signature=cache_identity(partition),ranking_contract_signature=cache_identity(ranking),context_contract_signature=cache_identity(contexts))
    result['strict_equivalence_signature']=cache_identity(result)
    return result

def select_equivalent_representatives(records):
    groups={}
    for record in records:groups.setdefault(record['signatures']['strict_equivalence_signature'],[]).append(record)
    representatives=[];aliases=[]
    for signature,group in groups.items():
        representative=min(group,key=lambda r:(float('inf') if r.get('retrieval_mean_seconds') is None else r['retrieval_mean_seconds'],r['configuration_id']))
        selected={k:v for k,v in representative.items() if k!='signatures'};selected.update(representative['signatures']);representatives.append(selected)
        for alias in sorted((r for r in group if r is not representative),key=lambda r:r['configuration_id']):
            aliases.append(dict(configuration_id=alias['configuration_id'],equivalent_to=representative['configuration_id'],basis=EQUIVALENCE_BASIS,strict_equivalence_signature=signature,representative_rule='minimum measured retrieval mean seconds, then configuration_id'))
    return representatives,aliases

def write_csv(path,records):
    with path.open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)

def score_matrix(output,map_path):
    mapping=json.loads(map_path.read_text('utf8'));mapping_sha256=sha(map_path);maps={r['intent_id']:r for r in mapping['records']};query_ids={r['intent_id'] for r in load_queries(output/'queries.jsonl',80)}
    if set(maps)!=query_ids:raise ValueError('common map must cover exactly 80 query intents')
    summaries=[];profiles=[];costs=[];candidate_records=[];execution=[];all_details=[]
    for config in configurations():
        directory=output/('index-'+config);rank_path=directory/'rankings.jsonl';context_path=directory/'contexts.jsonl'
        rank_rows=rows(rank_path) if rank_path.exists() else [];context_rows=rows(context_path) if context_path.exists() else []
        ranks={r['intent_id']:r for r in rank_rows};contexts={(r['intent_id'],r['budget']):r for r in context_rows}
        if len(ranks)!=len(rank_rows) or len(contexts)!=len(context_rows):raise ValueError('duplicate intent/context cell')
        rank_hashes={i:cache_identity(r) for i,r in ranks.items()};context_hashes={i:cache_identity(r) for i,r in contexts.items()}
        details=[]
        for intent in sorted(query_ids):
            m=maps[intent];ranking=ranks.get(intent);failed=not ranking or ranking['status']!='success'
            for method in ('R1','R2','R3','R4'):
                metrics_by_k={k:prefix_metrics(ranking['results'][method],m,k) for k in (1,5,10,20)} if not failed else {}
                for k in (1,5,10,20):
                    value=metrics_by_k.get(k) or dict(support={r['requirement_id']:'unknown' for r in m['requirements']},sufficient='unknown',coverage_lower=0.,coverage_upper=1.,complete_rr_lower=0.,complete_rr_upper=1.,prefix_evidence=[])
                    details.append(dict(configuration_id=config,kind='layer1_raw',intent_id=intent,main_stratum=m['main_stratum'],method=method,k=k,cell=f'layer1_raw/{method}/{k}',groups=m['groups'],mapping_sha256=mapping_sha256,ranking_sha256=rank_hashes.get(intent),failure='missing_or_failed_retrieval' if failed else None,**value))
            for B in (4096,8192):
                context=contexts.get((intent,B));missing=context is None
                for stage in ('raw','expanded','final'):
                    support=visible_support([s for u in context[stage]['units'] for s in u['spans']],m) if not missing else {r['requirement_id']:'unknown' for r in m['requirements']}
                    details.append(dict(configuration_id=config,kind='context',intent_id=intent,main_stratum=m['main_stratum'],budget=B,stage=stage,cell=f'fixed_budget_main/P0/{B}/{stage}',groups=m['groups'],mapping_sha256=mapping_sha256,context_id=context['context_id'] if context else None,context_sha256=context_hashes.get((intent,B)),support=support,failure='missing_or_failed_assembly' if missing else None,**score_support(m['groups'],support)))
        save_rows(directory/'score-details-e1-r01.jsonl',details) if directory.exists() else save_rows(output/f'score-details-{config}-failed.jsonl',details)
        for cell in sorted({r['cell'] for r in details}):
            values=[r for r in details if r['cell']==cell];summary=dict(configuration_id=config,cell=cell,**aggregate(values),coverage_lower_mean=statistics.mean(r['coverage_lower'] for r in values),coverage_upper_mean=statistics.mean(r['coverage_upper'] for r in values))
            summary['complete_mrr_lower']=statistics.mean(r['complete_rr_lower'] for r in values) if cell.startswith('layer1') else None;summary['complete_mrr_upper']=statistics.mean(r['complete_rr_upper'] for r in values) if cell.startswith('layer1') else None
            summaries.append(summary)
        exec_row=execution_row(config,query_ids,rank_rows,context_rows,len(details));exec_row['quality_unknown']=sum(r['sufficient']=='unknown' for r in details)
        execution.append(exec_row);all_details+=details
        if (directory/'chunk-profile.json').exists():profiles.append(json.loads((directory/'chunk-profile.json').read_text('utf8')))
        local_cost={name:json.loads((directory/(name+'-cost.json')).read_text('utf8')) if (directory/(name+'-cost.json')).exists() else None for name in ('build','retrieval','context')}
        successful=[r for r in ranks.values() if r['status']=='success'];times=[r['times'] for r in successful]
        retrieval_mean=statistics.mean(t['r4_total_seconds'] for t in times) if times else None
        costs.append(dict(configuration_id=config,stages=local_cost,mean_r4_total_seconds=retrieval_mean,latency_definition='Measured query_encode + sparse/dense search + RRF + reranker + sort, excluding instrument/audit overhead; not end-to-end answer latency.',query_cost_records=[dict(intent_id=r['intent_id'],**r['times']) for r in successful],assembly_cost_records=[dict(intent_id=r['intent_id'],budget=r['budget'],seconds=r['assembly_seconds'],tokens=r['final']['token_count']) for r in context_rows],generation_calls=0,remote_judge_calls=0,remote_model_calls=0,monetary_cost=None,monetary_cost_reason='Local GPU energy and monetary rate unmeasured.'))
        if exec_row['status']=='scored' and not config.startswith('B0'):
            library=rows(directory/'child_chunks.jsonl');sig=cache_identity([dict(core_spans=r['core_spans'],overlap_spans=r['overlap_spans'],prefix_spans=r['prefix_spans'],text=r['text']) for r in library])
            a=next(r for r in summaries if r['configuration_id']==config and r['cell']=='fixed_budget_main/P0/4096/final');b=next(r for r in summaries if r['configuration_id']==config and r['cell']=='layer1_raw/R4/10')
            signatures=strict_equivalence_signatures(library,rank_rows,context_rows)
            if signatures['source_partition_signature']!=sig:raise ValueError('source partition signature implementation drift')
            candidate_records.append(dict(configuration_id=config,cgc4_lower=a['complete_group_lower'],cgc4_upper=a['complete_group_upper'],cegr10_lower=b['complete_group_lower'],cegr10_upper=b['complete_group_upper'],retrieval_mean_seconds=retrieval_mean,signatures=signatures))
    selection_metrics,equivalent=select_equivalent_representatives(candidate_records)
    decision=candidate_decision(selection_metrics)
    if any(r['status']!='scored' for r in execution):decision.update(status='pending_failed_matrix',selected=[],pending_reason='Incomplete cells prevent final comparison; failure denominators retained.')
    decision.update(baseline_retained='B0-regex320-overlap48-M0',nonduplicate_metrics=selection_metrics,equivalent_configs=equivalent,generation_calls=0)
    save_json(output/'candidate-selection-e1-r01.json',decision);save_json(output/'scores-e1-r01.json',dict(schema_version='e1-layer1-layer2-source-score-v1',mapping_path=str(map_path),mapping_sha256=sha(map_path),summaries=summaries,execution=execution,details_count=len(all_details),independent_intents=80,unknown_semantics='Full reviewed conservative necessary ranges => yes; incomplete or missing certificates => unknown. Bounds are not confidence intervals.',generation_calls=0))
    write_csv(output/'main-table-e1-r01.csv',summaries);save_json(output/'chunk-profiles-e1-r01.json',profiles);save_json(output/'costs-e1-r01.json',costs);save_json(output/'execution-e1-r01.json',execution)
    compact=[{k:r.get(k) for k in ('configuration_id','kind','intent_id','main_stratum','method','k','budget','stage','sufficient','coverage_lower','coverage_upper','complete_rr_lower','complete_rr_upper','failure','mapping_sha256','ranking_sha256','context_sha256')} for r in all_details]
    write_csv(output/'per-intent-table-e1-r01.csv',compact)
    print('scored',len(all_details),'details;',len(summaries),'table cells;',decision['status'],flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['integrate','score']);p.add_argument('--output',type=Path,required=True);p.add_argument('--mapping',type=Path);p.add_argument('--revision',choices=['r04','r05'],default='r04');a=p.parse_args()
    if a.stage=='integrate':integrate(a.output.resolve(),a.revision)
    else:score_matrix(a.output.resolve(),(a.mapping or a.output/'common-support-map-e1-r04.json').resolve())

if __name__=='__main__':main()
