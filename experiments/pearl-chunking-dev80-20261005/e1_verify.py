"""Reopen E1 indexes, ranks, actual contexts and evidence; independent arithmetic."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
from runtime import ROOT, EXP, sha, cache_identity, save_json, verify_index, load_queries
from smoke import counter
from e1 import configurations, conservation, ranking_bindings, verify_frozen
from verify import independent_truth, independent_source_support, check_visible_unit
from assemble import serialize,unit,views_by_id,subtract_spans,union_spans,prefix_unit

def rows(path):return [json.loads(l) for l in path.read_text('utf8').splitlines() if l.strip()]

def verify_ranking(row,library):
    for method in ('R1','R2','R3','R4'):
        values=row['results'][method]
        if len({r['chunk_id'] for r in values})!=len(values):raise ValueError('duplicate ranked children')
        for child in values:
            if not math.isfinite(child['score']):raise ValueError('nonfinite ranking score')
            original=library[child['chunk_id']]
            if any(child.get(k)!=v for k,v in original.items()):raise ValueError('ranking/library source drift')
    scores={}
    for method in ('R1','R2'):
        for rank,r in enumerate(row['results'][method],1):scores[r['chunk_id']]=scores.get(r['chunk_id'],0.)+1/(60+rank)
    expected=sorted(scores,key=lambda k:(-scores[k],k));r3=row['results']['R3'];r4=row['results']['R4'];union=row['rrf_union']
    if [r['chunk_id'] for r in union]!=expected or any(abs(r['score']-scores[r['chunk_id']])>1e-12 for r in union):raise ValueError('RRF complete union mismatch')
    if [r['chunk_id'] for r in r3]!=expected[:100] or any(abs(r['score']-scores[r['chunk_id']])>1e-12 for r in r3):raise ValueError('R3 RRF top100 mismatch')
    if {r['chunk_id'] for r in r3}!={r['chunk_id'] for r in r4} or r4!=sorted(r4,key=lambda r:(-r['score'],r['chunk_id'])):raise ValueError('R4 candidates/score ordering mismatch')
    return True

def verify_totals(details,summaries):
    lookup={r['cell']:r for r in summaries}
    if set(lookup)!={r['cell'] for r in details}:raise ValueError('summary matrix coverage drift')
    for cell,summary in lookup.items():
        local=[r for r in details if r['cell']==cell];n=len(local)
        actual=dict(n=n,**{s:sum(r['sufficient']==s for r in local) for s in ('yes','no','unknown')},failure_n=sum(bool(r['failure']) for r in local))
        actual.update(complete_group_lower=actual['yes']/n,complete_group_upper=(actual['yes']+actual['unknown'])/n,coverage_lower_mean=statistics.mean(r['coverage_lower'] for r in local),coverage_upper_mean=statistics.mean(r['coverage_upper'] for r in local))
        if any(summary.get(k)!=v for k,v in actual.items()):raise ValueError('independent saved summary denominator/arithmetic mismatch')
        if cell.startswith('layer1'):
            for bound in ('lower','upper'):
                if summary['complete_mrr_'+bound]!=statistics.mean(r['complete_rr_'+bound] for r in local):raise ValueError('independent MRR mean drift')
    return True

def independent_metric(visible,mapping):
    support=independent_source_support(visible,mapping)
    return dict(support=support,sufficient=independent_truth(mapping['groups'],support),coverage_lower=max(sum(support[r]=='yes' for r in g)/len(g) for g in mapping['groups']),coverage_upper=max(sum(support[r]!='no' for r in g)/len(g) for g in mapping['groups']))

def verify_final_prefix(dedup,final,views,budget,c,truncation=None):
    """Independent ordered stop rule and exhaustive longer-prefix rejection.

    Batch counts use the exact frozen tokenizer; public counts check the accepted
    prefix and every complete unit. This does not call the runtime batch helper.
    """
    kept=[]
    for position,u in enumerate(dedup):
        if c.count(serialize(kept+[u]))<=budget:
            if len(final)<=len(kept) or final[len(kept)]!=u:raise ValueError('final full-unit order/retention mismatch')
            kept.append(u);continue
        saved=final[len(kept)] if len(final)>len(kept) else None
        n=len(saved['text']) if saved else 0
        if n>=len(u['text']) or saved is not None and prefix_unit(u,n,views)!=saved:raise ValueError('final prefix source/order mismatch')
        fixed=serialize(kept);prefix=(fixed+'\n\n') if fixed else ''
        texts=[]
        def reject_batch():
            if not texts:return
            counts=[len(e.ids) for e in c._tokenizer.encode_batch(texts)] if hasattr(c,'_tokenizer') else [c.count(t) for t in texts]
            if any(v<=budget for v in counts):raise ValueError('final prefix is not maximal under exhaustive Unicode rule')
            texts.clear()
        for longer in range(len(u['text'])-1,n,-1):
            if not any(p['text_start']<longer<=p['text_end'] for p in u['parts']):continue
            spans=[dict(p['span'],end=p['span']['start']+min(longer,p['text_end'])-p['text_start']) for p in u['parts'] if longer>p['text_start']]
            header='[Source '+json.dumps([[s[k] for k in ('doc_id','source_version','element_id','start','end')] for s in spans],ensure_ascii=False,separators=(',',':'))+']\n'
            texts.append(prefix+header+u['text'][:longer])
            if len(texts)==128:reject_batch()
        reject_batch()
        if saved:
            if c.count(serialize(kept+[saved]))>budget:raise ValueError('final retained prefix exceeds budget')
            kept.append(saved)
        if final!=kept:raise ValueError('final includes evidence after first budget stop')
        if truncation is not None:
            offsets=c.encode_with_offsets(u['text'])[1] if hasattr(c,'encode_with_offsets') else []
            expected=[dict(seed_chunk_id=u['seed_chunk_id'],reason='prefix_truncated' if saved else 'header_or_body_cannot_fit',retained_characters=n,token_offset_boundary=bool(saved) and n in {b for a,b in offsets},search='descending_exhaustive_unicode_source_prefix_batched_equivalent')]
            expected += [dict(seed_chunk_id=later['seed_chunk_id'],reason='after_budget_stop',retained_characters=0) for later in dedup[position+1:]]
            if truncation!=expected:raise ValueError('saved truncation trace drift')
        return True
    if final!=kept:raise ValueError('final extra/reordered full unit')
    if truncation is not None and truncation:raise ValueError('spurious truncation trace')
    return True

def verify_candidate_order(decision):
    metrics=decision['nonduplicate_metrics']
    def key(row,bound):return (-row['cgc4_'+bound],-row['cegr10_'+bound],row['retrieval_mean_seconds'],row['configuration_id'])
    ordered=sorted(metrics,key=lambda r:key(r,'lower'));remaining=list(ordered);expected=[]
    while remaining and len(expected)<2:
        worst=key(remaining[0],'lower')
        if any(worst>=key(other,'upper') for other in remaining[1:]):break
        expected.append(remaining.pop(0)['configuration_id'])
    status='pending_unknown' if remaining and len(expected)<2 else 'frozen'
    if decision['selected']!=expected or decision['status']!=status or decision['provisional_lower_bound_order']!=[r['configuration_id'] for r in ordered]:raise ValueError('independent candidate interval/order/freeze mismatch')
    return True

CANDIDATE_EQUIVALENCE_BASIS='identical canonical source partition, R1/R2/RRF-union/R3/R4 ranked source-text-score contracts, and actual P0 stage serialized text/spans at 4096/8192; configuration-derived chunk/context IDs ignored'

def _candidate_digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def _candidate_without_ids(value):
    if isinstance(value,dict):return {k:_candidate_without_ids(v) for k,v in value.items() if k not in ('chunk_id','seed_chunk_id','context_id','configuration_id')}
    if isinstance(value,list):return [_candidate_without_ids(v) for v in value]
    return value

def independent_candidate_contract(library,ranking_rows,context_rows):
    partition=[{k:_candidate_without_ids(r.get(k)) for k in ('core_spans','overlap_spans','prefix_spans','text')} for r in library]
    ranking=[]
    for row in sorted(ranking_rows,key=lambda r:r['intent_id']):
        if row.get('status')!='success':raise ValueError('candidate contract requires successful rankings')
        ranking.append(dict(intent_id=row['intent_id'],status=row['status'],results={method:_candidate_without_ids(row['results'][method]) for method in ('R1','R2','R3','R4')},rrf_union=_candidate_without_ids(row['rrf_union'])))
    contexts=[]
    for row in sorted(context_rows,key=lambda r:(r['intent_id'],r['budget'])):
        contexts.append(dict(intent_id=row['intent_id'],budget=row['budget'],panel_id=row['panel_id'],strategy=row['strategy'],stages={stage:_candidate_without_ids(row[stage]) for stage in ('raw','expanded','deduplicated','final')},truncation=_candidate_without_ids(row['truncation'])))
    components=dict(source_partition_signature=_candidate_digest(partition),ranking_contract_signature=_candidate_digest(ranking),context_contract_signature=_candidate_digest(contexts))
    return dict(**components,strict_equivalence_signature=_candidate_digest(components))

def verify_candidate_equivalence(decision,contracts):
    if decision.get('baseline_retained')!='B0-regex320-overlap48-M0':raise ValueError('candidate baseline drift')
    component_names=('source_partition_signature','ranking_contract_signature','context_contract_signature')
    for config,contract in contracts.items():
        components={k:contract[k] for k in component_names}
        if contract.get('configuration_id')!=config or contract.get('strict_equivalence_signature')!=_candidate_digest(components):raise ValueError('candidate equivalence signature drift')
    metrics=decision.get('nonduplicate_metrics',[]);aliases=decision.get('equivalent_configs',[])
    representatives={r.get('configuration_id'):r for r in metrics};alias_lookup={r.get('configuration_id'):r for r in aliases}
    if len(representatives)!=len(metrics) or len(alias_lookup)!=len(aliases) or set(representatives)&set(alias_lookup) or set(representatives)|set(alias_lookup)!=set(contracts):raise ValueError('candidate coverage drift')
    for config,alias in alias_lookup.items():
        target=representatives.get(alias.get('equivalent_to'))
        if target is None or any(contracts[config][k]!=contracts[target['configuration_id']][k] for k in component_names):raise ValueError('candidate equivalence alias contract drift')
    groups={}
    for config,contract in contracts.items():groups.setdefault(tuple(contract[k] for k in component_names),[]).append(config)
    expected_representatives={min(group,key=lambda config:(contracts[config]['retrieval_mean_seconds'],config)) for group in groups.values()}
    if set(representatives)!=expected_representatives:raise ValueError('candidate representative drift')
    expected_aliases=[]
    for group in groups.values():
        representative=min(group,key=lambda config:(contracts[config]['retrieval_mean_seconds'],config))
        for config in sorted(c for c in group if c!=representative):
            expected_aliases.append(dict(configuration_id=config,equivalent_to=representative,basis=CANDIDATE_EQUIVALENCE_BASIS,strict_equivalence_signature=contracts[config]['strict_equivalence_signature'],representative_rule='minimum measured retrieval mean seconds, then configuration_id'))
    if sorted(aliases,key=lambda r:r['configuration_id'])!=sorted(expected_aliases,key=lambda r:r['configuration_id']):raise ValueError('candidate equivalence alias record drift')
    for config,metric in representatives.items():
        expected=contracts[config]
        if any(metric.get(k)!=expected[k] for k in (*component_names,'strict_equivalence_signature','retrieval_mean_seconds')):raise ValueError('candidate representative signature/time drift')
    return True

def run(output,e0,retrieval_check):
    import numpy as np
    import os
    from transformers import AutoTokenizer
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    checks={'E0_frozen_release':verify_frozen(e0/'delivery-manifest.json')}
    phase=json.loads((output/'e1-phase-runtime.json').read_text('utf8'))
    for name,expected in phase['code_sha256'].items():
        if sha(EXP/name)!=expected:raise ValueError('E1 executed phase code drift '+name)
    equivalence=json.loads((output/'batch-assembly-equivalence-r02.json').read_text('utf8'))
    if equivalence['status']!='passed' or equivalence['batch_code_sha256']!=phase['code_sha256']['e1_batch.py']:raise ValueError('batch/serial equivalence receipt drift')
    probes=equivalence['checks']
    if len(probes)!=6 or len({(r['intent_id'],r['budget']) for r in probes})!=6 or any(r['status']!='passed' for r in probes):raise ValueError('complete six-case batch/serial probe required')
    independent_retrieval=json.loads(retrieval_check.read_text('utf8'))
    if independent_retrieval['status']!='passed':raise ValueError('independent sparse/reranker output check required')
    rerun_configs={r['configuration_id']:r for r in independent_retrieval['configurations']}
    if len(rerun_configs)!=13 or set(rerun_configs)!=set(configurations()):raise ValueError('independent retrieval configuration coverage drift')
    for config,record in rerun_configs.items():
        directory=output/('index-'+config)
        if any(record[method]['status']!='passed' or record[method]['queries']!=80 for method in ('R1','R4')) or record['R4']['pairs_compared']!=8000:raise ValueError('independent retrieval complete denominator drift')
        for field,name in [('rankings_sha256','rankings.jsonl'),('manifest_sha256','manifest.json'),('fts_sqlite_sha256','fts.sqlite3'),('child_chunks_sha256','child_chunks.jsonl')]:
            if record['R1'][field]!=sha(directory/name):raise ValueError('independent retrieval receipt/artifact drift '+config+'/'+name)
    if independent_retrieval['provenance']['verifier_code_sha256']!=sha(EXP/'e1_retrieval_verify.py') or independent_retrieval['provenance']['queries_sha256']!=sha(output/'queries.jsonl'):raise ValueError('independent retrieval code/query provenance drift')
    scores=json.loads((output/'scores-e1-r01.json').read_text('utf8'));map_path=Path(scores['mapping_path'])
    if sha(map_path)!=scores['mapping_sha256']:raise ValueError('score/source map file binding drift')
    maps={r['intent_id']:r for r in json.loads(map_path.read_text('utf8'))['records']}
    sources=json.loads((output/'source-views-prepared.json').read_text('utf8'));lookup={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in sources for e in v['elements']}
    source_views=views_by_id(sources)
    c=counter();tokenizer=AutoTokenizer.from_pretrained(str(ROOT/'memPed/knowledge/models/bge-m3'),local_files_only=True)
    from ped_knowledge.tokenization import HuggingFaceTokenCounter
    if type(c) is not HuggingFaceTokenCounter:raise ValueError('E1 batch equivalence requires the frozen exact counter class')
    queries=load_queries(output/'queries.jsonl',80);query_lookup={q['intent_id']:q for q in queries};summary_lookup={config:[r for r in scores['summaries'] if r['configuration_id']==config] for config in configurations()}
    if {(r['intent_id'],r['budget']) for r in probes}!={(q['intent_id'],b) for q in queries[:3] for b in (4096,8192)}:raise ValueError('batch/serial probes are not the six fixed actual query contexts')
    total_details=total_contexts=total_ranks=0;common_table_signature=None;candidate_contracts={}
    for config in configurations():
        directory=output/('index-'+config);manifest=directory/'manifest.json'
        if not manifest.exists():
            checks[config]={'status':'failed','reason':'missing built index; reported failures retained'};continue
        verify_index(manifest);index=json.loads(manifest.read_text('utf8'));library_rows=rows(directory/'child_chunks.jsonl');library={r['chunk_id']:r for r in library_rows}
        if len(library)!=len(library_rows) or index['child_count']!=len(library):raise ValueError('index cardinality drift')
        for child in library_rows:
            if child['prefix_spans']:raise ValueError('E1 M0 contains a metadata prefix')
            check_visible_unit(sources,{'spans':child['overlap_spans']+child['core_spans'],'text':child['text']},lookup)
            check_visible_unit(sources,{'spans':child['core_spans'],'text':child['core_text']},lookup)
        table_signature=cache_identity([{k:r[k] for k in ('core_spans','overlap_spans','prefix_spans','text')} for r in library_rows if r['is_table']])
        if common_table_signature is None:common_table_signature=table_signature
        if table_signature!=common_table_signature:raise ValueError('common table partition drift across configurations')
        for name,h in index['configuration']['code'].items():
            if sha(ROOT/name)!=h:raise ValueError('execution code drift '+name)
        saved_conservation=json.loads((directory/'source-conservation.json').read_text('utf8'))
        if conservation(sources,library_rows,config.startswith('B0'))!=saved_conservation:raise ValueError('saved conservation arithmetic drift')
        ids=json.loads((directory/'dense_ids.json').read_text('utf8'));vectors=np.load(directory/'dense_vectors.npy',allow_pickle=False)
        if ids!=list(library) or vectors.shape!=(len(ids),1024) or not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors,axis=1),1.,atol=1e-5):raise ValueError('dense identity or numerical invariant mismatch')
        inputs=rows(directory/'model_inputs.jsonl')
        if [r['chunk_id'] for r in inputs]!=ids:raise ValueError('dense model input membership drift')
        for start in range(0,len(inputs),64):
            batch=inputs[start:start+64];expected=tokenizer([library[r['chunk_id']]['text'] for r in batch],add_special_tokens=True,truncation=False)['input_ids']
            for r,t in zip(batch,expected,strict=True):
                if r['token_ids']!=t or r['raw_tokens']!=len(t) or len(t)>1024 or r['truncated'] or not r['actual_forward_inputs_verified']:raise ValueError('actual dense model input drift or truncation')
        ranking_rows=rows(directory/'rankings.jsonl');rankings={r['intent_id']:r for r in ranking_rows};audits=rows(directory/'retrieval-audits.jsonl');qvectors=np.load(directory/'query-vectors.npy',allow_pickle=False)
        rank_hashes={i:cache_identity(r) for i,r in rankings.items()};r4_hashes={i:cache_identity(r['results']['R4'][:100]) for i,r in rankings.items() if r['status']=='success'}
        if list(rankings)!=[q['intent_id'] for q in queries] or len(rankings)!=80 or len(audits)!=80 or qvectors.shape!=(80,1024) or not np.isfinite(qvectors).all() or not np.allclose(np.linalg.norm(qvectors,axis=1),1.,atol=1e-5):raise ValueError('retrieval complete denominator/order/numerical drift')
        for qi,(q,audit) in enumerate(zip(queries,audits,strict=True)):
            row=rankings[q['intent_id']]
            if row['status']!='success' or any(row.get(k)!=v for k,v in ranking_bindings(e0,directory,config,q).items()):raise ValueError('ranking input binding drift')
            if any(audit.get(k)!=v for k,v in ranking_bindings(e0,directory,config,q).items()):raise ValueError('retrieval audit input binding drift')
            verify_ranking(row,library)
            # Recompute exact dot scores individually, preserving float32 kernel behavior.
            dense=np.dot(vectors,qvectors[qi]);expected_ids=sorted(range(len(ids)),key=lambda i:(-float(dense[i]),ids[i]))[:100]
            if [r['chunk_id'] for r in row['results']['R2']]!=[ids[i] for i in expected_ids] or any(abs(r['score']-float(dense[i]))>1e-6 for r,i in zip(row['results']['R2'],expected_ids,strict=True)):raise ValueError('independent saved dense ranking mismatch')
            da=audit['dense'];token_ids=tokenizer(q['query'],add_special_tokens=True,truncation=False)['input_ids']
            if da['token_ids']!=token_ids or da['truncated'] or not da['actual_forward_inputs_verified'] or audit['intent_id']!=q['intent_id']:raise ValueError('dense query audit drift')
            if len(audit['rerank'])!=len(row['results']['R3']) or any(not r['actual_forward_inputs_verified'] or r['query_truncated'] or r['child_truncated_initial'] or r['child_truncated_pair'] for r in audit['rerank']):raise ValueError('reranker actual input/truncation audit failed')
            for r,child in zip(audit['rerank'],row['results']['R3'],strict=True):
                if r['chunk_id']!=child['chunk_id'] or r['query_text']!=q['query'] or r['child_text']!=child['text'] or r['child_text_sha256']!=child['text_sha256'] or r['model_input_length']!=len(r['model_input_ids']) or r['model_input_ids_sha256']!=cache_identity(r['model_input_ids']):raise ValueError('reranker pair/text/actual input identity drift')
        context_rows=rows(directory/'contexts.jsonl');contexts={r['context_id']:r for r in context_rows}
        context_hashes={i:cache_identity(r) for i,r in contexts.items()}
        if len(contexts)!=160 or {(r['intent_id'],r['budget']) for r in context_rows}!={(q['intent_id'],b) for q in queries for b in (4096,8192)}:raise ValueError('context matrix denominator drift')
        for context in context_rows:
            if config=='C1-L256-O0-M0':
                probe=next((r for r in probes if (r['intent_id'],r['budget'])==(context['intent_id'],context['budget'])),None)
                if probe and probe['final_sha256']!=cache_identity(context['final']):raise ValueError('actual saved context/batch equivalence probe drift')
            if context['strategy']!='P0' or context['panel_id']!='fixed_budget_main' or context['ranking_sha256']!=r4_hashes[context['intent_id']]:raise ValueError('P0 context/ranking binding drift')
            if any(context.get(k)!=v for k,v in ranking_bindings(e0,directory,config,query_lookup[context['intent_id']]).items()):raise ValueError('context index/query/source binding drift')
            ranked=rankings[context['intent_id']]['results']['R4'][:100]
            expected_raw=[unit(child['core_spans']+child['overlap_spans'],source_views,child['chunk_id'],rank) for rank,child in enumerate(ranked,1)]
            if context['raw']['units']!=expected_raw:raise ValueError('context raw evidence is not actual ranked child text')
            expected_dedup=[];seen=[]
            for raw_unit in expected_raw:
                residual=subtract_spans(raw_unit['spans'],seen)
                if residual:expected_dedup.append(unit(residual,source_views,raw_unit['seed_chunk_id'],raw_unit['rank']))
                seen=union_spans(seen+raw_unit['spans'])
            if context['deduplicated']['units']!=expected_dedup or context['dedup']!=context['deduplicated']:raise ValueError('saved P0 deduplication/order drift')
            verify_final_prefix(expected_dedup,context['final']['units'],source_views,context['budget'],c,context['truncation'])
            if context['context_id']!=cache_identity({k:v for k,v in context.items() if k not in ('assembly_seconds','context_id','intent_id','configuration_id','index_sha256','query_sha256','source_sha256','parent_sha256')}):raise ValueError('context identity drift')
            for stage in ('raw','expanded','deduplicated','final'):
                snap=context[stage]
                for visible_unit in snap['units']:check_visible_unit(sources,visible_unit,lookup)
                serialized=serialize(snap['units'])
                if serialized!=snap['serialized_context'] or c.count(serialized)!=snap['token_count'] or snap['text_sha256']!=hashlib.sha256(serialized.encode()).hexdigest():raise ValueError('saved context serialized budget/text/hash drift')
                if len(c._tokenizer.encode_batch([serialized])[0].ids)!=snap['token_count']:raise ValueError('pinned batch/public tokenizer count drift')
            if context['raw']!=context['expanded'] or context['final']['token_count']>context['budget']:raise ValueError('P0 recovery semantics or budget violation')
            final_spans=[s for u in context['final']['units'] for s in u['spans']];raw_spans=[s for u in expected_raw for s in u['spans']]
            if subtract_spans(final_spans,raw_spans):raise ValueError('final includes unreturned source evidence')
            if sum(s['end']-s['start'] for s in final_spans)!=sum(s['end']-s['start'] for s in union_spans(final_spans)):raise ValueError('final source intervals were not deduplicated')
        details=rows(directory/'score-details-e1-r01.jsonl')
        expected={('layer1_raw',q['intent_id'],m,k) for q in queries for m in ('R1','R2','R3','R4') for k in (1,5,10,20)}|{('context',r['intent_id'],r['budget'],s) for r in context_rows for s in ('raw','expanded','final')}
        observed=[(r['kind'],r['intent_id'],r['method'],r['k']) if r['kind']=='layer1_raw' else (r['kind'],r['intent_id'],r['budget'],r['stage']) for r in details]
        if len(details)!=1760 or len(set(observed))!=1760 or set(observed)!=expected:raise ValueError('score matrix denominator drift')
        for detail in details:
            m=maps[detail['intent_id']]
            if detail['groups']!=m['groups'] or detail['mapping_sha256']!=scores['mapping_sha256']:raise ValueError('detail/Gold requirement/map binding drift')
            if detail['kind']=='context':
                context=contexts[detail['context_id']]
                if detail['context_sha256']!=context_hashes[detail['context_id']] or context['intent_id']!=detail['intent_id']:raise ValueError('detail/context binding drift')
                visible=[s for u in context[detail['stage']]['units'] for s in u['spans']];value=independent_metric(visible,m)
            else:
                ranking=rankings[detail['intent_id']]
                if detail['ranking_sha256']!=rank_hashes[detail['intent_id']]:raise ValueError('detail/ranking binding drift')
                ranked=ranking['results'][detail['method']][:detail['k']];visible=[];prefix=[]
                for rank,child in enumerate(ranked,1):
                    visible+=child['core_spans']+child['overlap_spans'];prefix.append(dict(rank=rank,**independent_metric(visible,m)))
                value=independent_metric(visible,m)
                lower=next((1/r['rank'] for r in prefix if r['sufficient']=='yes'),0.);upper=next((1/r['rank'] for r in prefix if r['sufficient']!='no'),0.)
                if detail['prefix_evidence']!=prefix or detail['complete_rr_lower']!=lower or detail['complete_rr_upper']!=upper:raise ValueError('independent MRR prefix evidence mismatch')
            if any(detail.get(k)!=v for k,v in value.items()):raise ValueError('independent actual-visible source support/AND/OR score mismatch')
        verify_totals(details,summary_lookup[config]);total_details+=len(details);total_contexts+=160;total_ranks+=80
        if not config.startswith('B0'):
            contract=independent_candidate_contract(library_rows,ranking_rows,context_rows)
            candidate_contracts[config]=dict(configuration_id=config,retrieval_mean_seconds=statistics.mean(r['times']['r4_total_seconds'] for r in ranking_rows),**contract)
        checks[config]={'status':'passed','children':len(ids),'rankings':80,'rerank_pairs':sum(len(a['rerank']) for a in audits),'contexts':160,'score_details':len(details),'real_model_inputs_reopened':True,'ordered_final_and_exhaustive_maximality_verified':True,'truncation_trace_verified':True,'artifact_sha256':{name:sha(directory/name) for name in ('score-details-e1-r01.jsonl','rankings.jsonl','contexts.jsonl','retrieval-audits.jsonl','manifest.json')}};print('verified',config,flush=True)
    expected_candidates={c for c in configurations() if not c.startswith('B0')}
    if set(candidate_contracts)!=expected_candidates:raise ValueError('candidate contract configuration coverage drift')
    decision=json.loads((output/'candidate-selection-e1-r01.json').read_text('utf8'));verify_candidate_equivalence(decision,candidate_contracts);verify_candidate_order(decision)
    for metric in decision['nonduplicate_metrics']:
        config=metric['configuration_id'];summaries=summary_lookup[config]
        a=next(r for r in summaries if r['cell']=='fixed_budget_main/P0/4096/final');b=next(r for r in summaries if r['cell']=='layer1_raw/R4/10')
        expected=dict(cgc4_lower=a['complete_group_lower'],cgc4_upper=a['complete_group_upper'],cegr10_lower=b['complete_group_lower'],cegr10_upper=b['complete_group_upper'],retrieval_mean_seconds=statistics.mean(r['times']['r4_total_seconds'] for r in rows(output/('index-'+config)/'rankings.jsonl')))
        if any(metric[k]!=v for k,v in expected.items()):raise ValueError('candidate metric/actual summary/time drift')
    return dict(status='passed' if all(r['status']=='passed' for r in checks.values()) else 'failed_matrix_explicit',checks=checks,independent_intents=80,rankings=total_ranks,contexts=total_contexts,score_details=total_details,score_file_sha256=sha(output/'scores-e1-r01.json'),mapping_sha256=scores['mapping_sha256'],independent_retrieval_check_sha256=sha(retrieval_check),candidate_selection_sha256=sha(output/'candidate-selection-e1-r01.json'),candidate_configuration_coverage=len(candidate_contracts),candidate_strict_equivalence_verified=True,candidate_interval_order_verified=True,generation_calls=0,remote_judge_calls=0)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--e0',type=Path,required=True);p.add_argument('--retrieval-check',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();save_json(a.receipt,run(a.output.resolve(),a.e0.resolve(),a.retrieval_check.resolve()));print('E1 saved-output verification finished')

if __name__=='__main__':main()
