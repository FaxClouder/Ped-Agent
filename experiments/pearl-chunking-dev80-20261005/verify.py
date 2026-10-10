"""Reopen actual E0 artifacts and independently recompute three-valued totals."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from runtime import sha,cache_identity,save_json,load_queries,verify_index

def independent_truth(groups,status):
    results=[]
    for group in groups:
        values=[status[k] for k in group]
        results.append('no' if 'no' in values else 'yes' if all(v=='yes' for v in values) else 'unknown')
    return 'yes' if 'yes' in results else 'no' if results and all(v=='no' for v in results) else 'unknown'

def check_visible_unit(views,unit,lookup=None):
    if lookup is None:lookup={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']}
    parts=[];previous=None
    for s in unit['spans']:
        key=tuple(s[k] for k in ('doc_id','source_version','element_id'));text=lookup[key]
        if not 0<=s['start']<s['end']<=len(text):raise ValueError('invalid final source offset')
        if parts and (key!=previous[0] or s['start']!=previous[1]):parts.append('\n\n')
        parts.append(text[s['start']:s['end']]);previous=(key,s['end'])
    if ''.join(parts)!=unit['text']:raise ValueError('saved visible text/offset mismatch')
    return True

def rows(path):return [json.loads(l) for l in path.read_text('utf8').splitlines() if l.strip()]

def independent_source_support(visible,mapping):
    result={}
    for requirement in mapping['requirements']:
        states=[]
        for group in requirement['evidence_groups']:
            covered=bool(group['necessary_spans'])
            for need in group['necessary_spans']:
                pieces=sorted((s['start'],s['end']) for s in visible if all(s[k]==need[k] for k in ('doc_id','source_version','element_id')))
                cursor=need['start']
                for a,b in pieces:
                    if a<=cursor:cursor=max(cursor,b)
                covered=covered and cursor>=need['end']
            states.append(group['status'] if covered and group.get('reviewer_id') and group.get('rationale') and group['status'] in ('yes','no') else 'unknown')
        result[requirement['requirement_id']]='yes' if 'yes' in states else 'no' if states and all(s=='no' for s in states) else 'unknown'
    return result

def run(output,score_path=None):
    from smoke import counter
    from assemble import serialize
    import numpy as np
    c=counter();views=json.loads((output/'source-views-prepared.json').read_text('utf8'))
    index_path=output/'index-C1-L384-O0-M0/manifest.json'
    checks={'index':verify_index(index_path)}
    index=json.loads(index_path.read_text('utf8'));identity=index['configuration']
    for key,name in (('source','source-views-prepared.json'),('table','table-snapshot.json'),('parent','public-parent-graph.json')):
        if identity[key]!=sha(output/name):raise ValueError('frozen index/source input drift')
    library={r['chunk_id']:r for r in rows(index_path.parent/'child_chunks.jsonl')}
    queries=load_queries(output/'queries.jsonl');ranks=rows(output/'rankings.jsonl');contexts=rows(output/'contexts.jsonl')
    if len(ranks)!=8 or {r['intent_id'] for r in ranks}!={q['intent_id'] for q in queries}:raise ValueError('real smoke intent denominator mismatch')
    for row in ranks:
        if row['status']!='success':raise ValueError('failed real smoke retrieval')
        query=next(q for q in queries if q['intent_id']==row['intent_id'])
        bindings={'query_sha256':cache_identity(query),'index_sha256':sha(index_path),'source_sha256':identity['source'],'parent_sha256':identity['parent']}
        if any(row.get(k)!=v for k,v in bindings.items()):raise ValueError('ranking frozen input mismatch')
        for method in ('R1','R2','R3','R4'):
            result=row['results'][method]
            if len({r['chunk_id'] for r in result})!=len(result):raise ValueError('duplicate ranked children')
            for child in result:
                if not math.isfinite(child['score']):raise ValueError('nonfinite ranking score')
                original=library[child['chunk_id']]
                if any(child.get(k)!=v for k,v in original.items()):raise ValueError('ranked child/source/library mismatch')
        a,b=row['results']['R3'],row['results']['R4']
        if len(a)!=100 or len(b)!=100 or {r['chunk_id'] for r in a}!={r['chunk_id'] for r in b}:raise ValueError('R3/R4 candidate set mismatch')
        scores={}
        for name in ('R1','R2'):
            for rank,r in enumerate(row['results'][name],1):scores[r['chunk_id']]=scores.get(r['chunk_id'],0.)+1/(60+rank)
        expected=sorted(scores,key=lambda k:(-scores[k],k))
        if expected!=[r['chunk_id'] for r in row['rrf_union']]:raise ValueError('RRF independent identity mismatch')
        if any(not math.isfinite(r['score']) or abs(scores[r['chunk_id']]-r['score'])>1e-12 for r in row['rrf_union']):raise ValueError('RRF numerical mismatch')
        if [r['chunk_id'] for r in a]!=expected[:100] or any(abs(scores[r['chunk_id']]-r['score'])>1e-12 for r in a):raise ValueError('R3 frozen Top100 order/score mismatch')
        if b!=sorted(b,key=lambda r:(-r['score'],r['chunk_id'])):raise ValueError('R4 score/tie order mismatch')
    expected_contexts={(q['intent_id'],P,B,panel) for q in queries for P in ('P0','P1','P2') for B in (4096,8192) for panel in ('fixed_budget_main','seed10_diagnostic')}
    actual_contexts=[(r['intent_id'],r['strategy'],r['budget'],r['panel_id']) for r in contexts]
    if len(contexts)!=96 or len(set(actual_contexts))!=96 or set(actual_contexts)!=expected_contexts:raise ValueError('context cell denominator mismatch')
    if len({r['context_id'] for r in contexts})!=96:raise ValueError('duplicate context IDs')
    element_lookup={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']}
    for record in contexts:
        ranked=next(r for r in ranks if r['intent_id']==record['intent_id'])['results']['R4']
        seed=ranked[:10] if record['panel_id']=='seed10_diagnostic' else ranked[:100]
        if record['ranking_sha256']!=cache_identity(seed):raise ValueError('context/ranking binding drift')
        for stage in ('raw','expanded','deduplicated','final'):
            snap=record[stage]
            for unit in snap['units']:check_visible_unit(views,unit,element_lookup)
            rendered=serialize(snap['units'])
            if rendered!=snap['serialized_context'] or c.count(rendered)!=snap['token_count']:raise ValueError('saved serialized context/token mismatch')
        if record['final']['token_count']>record['budget']:raise ValueError('budget exceeded')
    checks['contexts']={'count':len(contexts),'span_and_serialized_budget':'passed'}
    audits=rows(output/'retrieval-audits.jsonl')
    if len(audits)!=8 or any(not a['dense']['actual_forward_inputs_verified'] or len(a['rerank'])!=100 or any(not p['actual_forward_inputs_verified'] for p in a['rerank']) for a in audits):raise ValueError('missing actual model execution evidence')
    checks['real_model_audits']={'queries':8,'rerank_pairs':800,'status':'passed'}
    threshold=json.loads((output/'calibration-r02/semantic-threshold.json').read_text('utf8'))
    expected=float(np.quantile(threshold['distance_values'],.9,method='linear'))
    if not math.isfinite(expected) or not math.isfinite(threshold['threshold']) or abs(expected-threshold['threshold'])>1e-12:raise ValueError('C4 percentile recomputation mismatch')
    checks['semantic_threshold']={'pairs':len(threshold['distance_values']),'threshold':expected,'status':'passed'}
    if score_path:
        scored=json.loads(score_path.read_text('utf8'));details=scored['details']
        mapping_path=Path(scored['mapping_path'])
        if sha(mapping_path)!=scored['mapping_sha256']:raise ValueError('score/map binding drift')
        source_map=json.loads(mapping_path.read_text('utf8'));maps={r['intent_id']:r for r in source_map['records']};by_context={r['context_id']:r for r in contexts};by_intent={r['intent_id']:r for r in ranks}
        expected_detail_keys={('context',r['context_id'],stage) for r in contexts for stage in ('raw','expanded','final')}
        expected_detail_keys|={('layer1_raw',q['intent_id'],method,k) for q in queries for method in ('R1','R2','R3','R4') for k in (1,5,10,20)}
        actual_detail_keys=[('context',r['context_id'],r['stage']) if r['kind']=='context' else ('layer1_raw',r['intent_id'],r['method'],r['k']) for r in details]
        if len(details)!=416 or len(set(actual_detail_keys))!=416 or set(actual_detail_keys)!=expected_detail_keys:raise ValueError('score detail cell denominator mismatch')
        for result in details:
            if result['groups']!=maps[result['intent_id']]['groups']:raise ValueError('score Gold group structure drift')
            if result['mapping_sha256']!=scored['mapping_sha256']:raise ValueError('score detail/map drift')
            if result['kind']=='context':
                context=by_context[result['context_id']]
                if context['intent_id']!=result['intent_id']:raise ValueError('score context/intent mismatch')
                expected_cell=f"{context['panel_id']}/{context['strategy']}/{context['budget']}/{result['stage']}"
                if cache_identity(context)!=result['context_sha256']:raise ValueError('score/context binding drift')
                visible=[s for u in context[result['stage']]['units'] for s in u['spans']]
            else:
                ranking=by_intent[result['intent_id']]
                expected_cell=f"layer1_raw/{result['method']}/{result['k']}"
                if cache_identity(ranking)!=result['ranking_sha256']:raise ValueError('score/ranking binding drift')
                visible=[s for child in ranking['results'][result['method']][:result['k']] for s in child['core_spans']+child['overlap_spans']]
            if expected_cell!=result['cell']:raise ValueError('score detail cell identity mismatch')
            if independent_source_support(visible,maps[result['intent_id']])!=result['support']:raise ValueError('actual visible support recomputation mismatch')
            if independent_truth(result['groups'],result['support'])!=result['sufficient']:raise ValueError('independent AND/OR score mismatch')
            lower=max(sum(result['support'][r]=='yes' for r in g)/len(g) for g in result['groups'])
            upper=max(sum(result['support'][r]!='no' for r in g)/len(g) for g in result['groups'])
            if result['coverage_lower']!=lower or result['coverage_upper']!=upper:raise ValueError('independent coverage bounds mismatch')
        summaries={}
        for result in details:
            key=result['cell'];summaries.setdefault(key,{'n':0,'yes':0,'no':0,'unknown':0})
            summaries[key]['n']+=1;summaries[key][result['sufficient']]+=1
        if set(summaries)!=set(scored['summaries']) or len(summaries)!=52 or any(count['n']!=8 for count in summaries.values()):raise ValueError('score summary matrix mismatch')
        for key,count in summaries.items():
            actual=scored['summaries'][key]
            if any(actual[k]!=v for k,v in count.items()):raise ValueError('saved score denominator/count mismatch')
            if actual['complete_group_lower']!=count['yes']/count['n'] or actual['complete_group_upper']!=(count['yes']+count['unknown'])/count['n']:raise ValueError('saved score bounds mismatch')
        checks['independent_scoring']={'details':len(details),'cells':len(summaries),'status':'passed'}
    return {'status':'passed','checks':checks,'artifacts_sha256':{p.name:sha(p) for p in output.iterdir() if p.is_file() and p.suffix in ('.json','.jsonl')},'generation':'not executed; no round-specific authorization','E1':'not executed'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--scores',type=Path);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();save_json(a.receipt,run(a.output,a.scores));print('saved-output independent verification passed')

if __name__=='__main__':main()
