"""Session 3 E1 only: independent real indexes, R1-R4, P0 contexts; no generation."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import traceback
from datetime import datetime, timezone
from runtime import ROOT, EXP, sha, cache_identity, save_json, save_rows, load_queries, build_fts, build_dense, verify_index, legacy_runtime, model_assets, runtime_code
from smoke import counter, load, models

def configurations():
    return {**{f'{C}-L{L}-O0-M0':(C,L) for C in ('C1','C2','C3','C4') for L in (256,384,512)},'B0-regex320-overlap48-M0':('B0',320)}

def verify_frozen(manifest_path,root=ROOT):
    manifest=load(manifest_path)
    drift=[name for name,h in manifest['artifacts_sha256'].items() if not (root/name).is_file() or sha(root/name)!=h]
    if drift:raise ValueError('E0 frozen artifact drift: '+repr(drift))
    return {'status':'passed','artifact_count':len(manifest['artifacts_sha256']),'manifest_sha256':sha(manifest_path)}


def verify_input_copies(e0,output):
    """Bind the runtime's public copies to the E0 release and copy receipt."""
    receipt=load(output/'input-copy-manifest.json')
    if receipt['E0_sha256']!=sha(e0/'delivery-manifest.json'):
        raise ValueError('E1 copy receipt/E0 release drift')
    required={'source-views-prepared.json','table-snapshot.json','public-parent-graph.json',
              'calibration-r02/semantic-threshold.json','queries.jsonl'}
    copied=receipt['copied_sha256']
    if not required.issubset(copied):raise ValueError('E1 copy receipt missing required public assets')
    for name,expected in copied.items():
        target=output/name
        if not target.is_file() or sha(target)!=expected:
            raise ValueError('E1 copy drift: '+name)
        original=e0/name if name!='queries.jsonl' else Path(receipt.get('queries_original','__no_original__'))
        if name=='queries.jsonl' and original.is_file():
            if sha(original)!=receipt['queries_original_sha256'] or load_queries(original,80)!=load_queries(target,80):raise ValueError('E1 dev80 query content/source drift')
            continue
        if original.is_file() and sha(original)!=expected:
            raise ValueError('E1 copy/E0 asset drift: '+name)
    return {'status':'passed','receipt_sha256':sha(output/'input-copy-manifest.json'),
            'e0_manifest_sha256':receipt['E0_sha256'],'copied_files':len(copied)}


def record_stage(path,config,stage,status,**detail):
    if status not in {'running','completed','failed'}:raise ValueError('invalid E1 stage status')
    row=dict(configuration_id=config,stage=stage,status=status,
             timestamp_utc=datetime.now(timezone.utc).isoformat(),**detail)
    with Path(path).open('a',encoding='utf8',newline='\n') as stream:
        stream.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
        stream.flush();os.fsync(stream.fileno())
    return row

def assert_bindings(row,bindings):
    if any(row.get(k)!=v for k,v in bindings.items()):raise ValueError('E1 ranking/input/configuration drift')

def conservation(views,children,baseline):
    spans={}
    for row in children:
        for s in row['core_spans']:
            spans.setdefault((s['doc_id'],s['source_version'],s['element_id']),[]).append((s['start'],s['end']))
    missing=duplicate=total=0;gaps=[]
    for view in views:
        eligible={eid for run in view['barrier_runs'] for eid in run}
        for e in view['elements']:
            if e['element_id'] not in eligible:continue
            key=(view['doc_id'],view['source_version'],e['element_id']);cursor=0;total+=len(e['text'])
            for a,b in sorted(spans.pop(key,[])):
                if a<0 or b>len(e['text']) or b<=a:raise ValueError('invalid source interval')
                if a>cursor:
                    missing+=a-cursor;gaps.append(dict(doc_id=key[0],source_version=key[1],element_id=key[2],start=cursor,end=a,reason='legacy_regex_boundary' if baseline else 'unexpected_gap'))
                duplicate+=max(0,min(cursor,b)-a);cursor=max(cursor,b)
            if cursor<len(e['text']):
                missing+=len(e['text'])-cursor;gaps.append(dict(doc_id=key[0],source_version=key[1],element_id=key[2],start=cursor,end=len(e['text']),reason='legacy_regex_boundary' if baseline else 'unexpected_gap'))
    if spans or duplicate or (missing and not baseline):raise ValueError(f'source conservation failed: missing={missing}, duplicate={duplicate}, unknown={len(spans)}')
    return dict(status='passed' if not missing else 'baseline_legacy_gaps_recorded',source_characters=total,missing_characters=missing,duplicate_core_characters=duplicate,gaps=gaps)

def asset_bindings(e0):
    return {name:sha(e0/path) for name,path in [('source','source-views-prepared.json'),('table','table-snapshot.json'),('parent','public-parent-graph.json'),('calibration','calibration-r02/semantic-threshold.json')]}

def identity(e0,config,c):
    from ped_knowledge.tokenization import EnglishLexicalAnalyzer
    code=runtime_code();code['experiments/pearl-chunking-dev80-20261005/e1.py']=sha(__file__)
    return dict(policy=config,**asset_bindings(e0),tokenizer=c.fingerprint,lexical=EnglishLexicalAnalyzer().fingerprint,models=model_assets(),code=code,retrieval={'depth':100,'RRF_k':60,'dense':'exact_float32_dot','seed':20260929})

def make_children(e0,config,c):
    from chunkers import chunk
    from parent_graph import parents_for_spans
    views=load(e0/'source-views-prepared.json');graph=load(e0/'public-parent-graph.json');semantic=load(e0/'calibration-r02/semantic-threshold.json')
    if semantic['view_sha256s']!=[v['view_sha256'] for v in views]:raise ValueError('C4 calibration/source view drift')
    C,L=configurations()[config];rows=[]
    for v in views:
        local={'parents':[p for p in graph['parents'] if p['doc_id']==v['doc_id'] and p['source_version']==v['source_version']]}
        for ch in chunk(v,C,L,c,semantic if C=='C4' else None):
            ch['parent_ids']=parents_for_spans(ch['core_spans'],local)
            ch.update(text=ch['retrieval_text'],text_sha256=hashlib.sha256(ch['retrieval_text'].encode()).hexdigest(),source_id=v['doc_id'],resource_id=v['doc_id'],version_id=v['source_version'],title=v.get('title',''),heading_path=[],locator=json.dumps(ch['core_spans']),chunk_level='child')
            rows.append(ch)
    if len({r['chunk_id'] for r in rows})!=len(rows):raise ValueError('duplicate children')
    return views,rows

def build(e0,output,config,m=None):
    import numpy as np
    started=time.perf_counter();directory=output/('index-'+config);directory.mkdir(exist_ok=False)
    c=counter();binding=identity(e0,config,c);views,rows=make_children(e0,config,c)
    save_rows(directory/'child_chunks.jsonl',rows)
    save_json(directory/'source-conservation.json',conservation(views,rows,config.startswith('B0')))
    lengths=[c.count(r['text']) for r in rows]
    C,L=configurations()[config]
    if C!='B0' and any(c.count(r['core_text'])>(256 if r['is_table'] else L) for r in rows):raise ValueError('core exceeds predeclared limit')
    oversized=[{'chunk_id':r['chunk_id'],'bge_tokens':n} for r,n in zip(rows,lengths,strict=True) if n>1024]
    by_type={label:[n for r,n in zip(rows,lengths,strict=True) if r['is_table']==is_table] for label,is_table in [('body',False),('table',True)]}
    save_json(directory/'chunk-profile.json',dict(configuration_id=config,children=len(rows),table_children=sum(r['is_table'] for r in rows),token_min=min(lengths),token_max=max(lengths),token_quantiles={str(q):float(np.quantile(lengths,q)) for q in (0,.25,.5,.75,.9,.95,1)},separate_profiles={name:dict(n=len(values),total_tokens=sum(values),mean=float(np.mean(values)),quantiles={str(q):float(np.quantile(values,q)) for q in (0,.25,.5,.75,.9,.95,1)}) for name,values in by_type.items()},passage_limit=1024,oversized=oversized))
    if oversized:raise ValueError(f'{config}: {len(oversized)} passages exceed frozen dense 1024; no truncation')
    chunk_seconds=time.perf_counter()-started
    build_fts(directory/'fts.sqlite3',rows,binding);fts_seconds=time.perf_counter()-started-chunk_seconds
    m=m or models();dense_started=time.perf_counter();build_dense(m,rows,directory);dense_seconds=time.perf_counter()-dense_started
    size=sum(p.stat().st_size for p in directory.iterdir() if p.is_file())
    save_json(directory/'build-cost.json',dict(wall_seconds=time.perf_counter()-started,chunk_seconds=chunk_seconds,fts_seconds=fts_seconds,dense_seconds=dense_seconds,index_bytes=size,encoded_passages=len(rows),passage_tokens=sum(lengths),local_cuda=True,generation_calls=0,remote_calls=0))
    manifest=dict(configuration=binding,output_sha256={p.name:sha(p) for p in directory.iterdir() if p.is_file()},child_count=len(rows),smoke_only=False,dense={'max_length':1024})
    save_json(directory/'manifest.json',manifest);save_json(directory/'verification.json',verify_index(directory/'manifest.json'))
    print(json.dumps({'configuration':config,'children':len(rows),'status':'built'}),flush=True)

def verified_identity(e0,output,config):
    directory=output/('index-'+config);verify_index(directory/'manifest.json')
    manifest=load(directory/'manifest.json');assert_bindings(manifest['configuration'],identity(e0,config,counter()))
    return directory,manifest

def ranking_bindings(e0,directory,config,q):
    return dict(configuration_id=config,index_sha256=sha(directory/'manifest.json'),query_sha256=cache_identity(q),source_sha256=sha(e0/'source-views-prepared.json'),parent_sha256=sha(e0/'public-parent-graph.json'))

def retrieve(e0,output,config,queries_path,m=None):
    import numpy as np
    directory,_=verified_identity(e0,output,config);queries=load_queries(queries_path,80);old=legacy_runtime()
    children={r['chunk_id']:r for r in old.compare.read_jsonl(directory/'child_chunks.jsonl')};ids=load(directory/'dense_ids.json');vectors=np.load(directory/'dense_vectors.npy',allow_pickle=False)
    if list(children)!=ids or vectors.shape[0]!=len(ids):raise ValueError('index cardinality/order mismatch')
    m=m or models();started=time.perf_counter();failed=[];query_vectors=[]
    with (directory/'rankings.jsonl').open('x',encoding='utf8') as ranks,(directory/'retrieval-audits.jsonl').open('x',encoding='utf8') as audits:
        for q in queries:
            binding=ranking_bindings(e0,directory,config,q)
            try:
                results,union,vector,dense_audit,r4_audits,times=old.retrieve(m,directory,vectors,ids,children,q['query'])
                record=dict(intent_id=q['intent_id'],status='success',results=results,rrf_union=union,times=times,**binding)
                audit=dict(intent_id=q['intent_id'],dense=dense_audit,rerank=r4_audits,times=times,**binding);query_vectors.append(vector)
            except Exception as e:
                failed.append(q['intent_id']);record=dict(intent_id=q['intent_id'],status='failed',error=repr(e),**binding);audit=dict(intent_id=q['intent_id'],status='failed',traceback=traceback.format_exc(),**binding)
            ranks.write(json.dumps(record,ensure_ascii=False)+'\n');ranks.flush();audits.write(json.dumps(audit,ensure_ascii=False)+'\n');audits.flush()
            print(config,q['intent_id'],record['status'],flush=True)
    if not failed:np.save(directory/'query-vectors.npy',np.asarray(query_vectors),allow_pickle=False)
    save_json(directory/'retrieval-cost.json',dict(wall_seconds=time.perf_counter()-started,queries=80,failed_intents=failed,rankings_sha256=sha(directory/'rankings.jsonl'),audits_sha256=sha(directory/'retrieval-audits.jsonl'),queries_sha256=sha(queries_path),generation_calls=0,remote_calls=0))
    if failed:raise RuntimeError('failed real retrieval units: '+repr(failed))

def contexts(e0,output,config,queries_path):
    from assemble import assemble
    directory,_=verified_identity(e0,output,config);old=legacy_runtime();c=counter();views=load(e0/'source-views-prepared.json');parents=load(e0/'public-parent-graph.json')
    queries={q['intent_id']:q for q in load_queries(queries_path,80)};rankings=old.compare.read_jsonl(directory/'rankings.jsonl')
    if len(rankings)!=80 or {r['intent_id'] for r in rankings}!=set(queries):raise ValueError('ranking intent cardinality mismatch')
    cost=load(directory/'retrieval-cost.json')
    if cost['rankings_sha256']!=sha(directory/'rankings.jsonl') or cost['queries_sha256']!=sha(queries_path):raise ValueError('retrieval output drift')
    started=time.perf_counter();count=0
    with (directory/'contexts.jsonl').open('x',encoding='utf8') as target:
        for row in rankings:
            if row['status']!='success':raise ValueError('failed retrieval cannot assemble')
            binding=ranking_bindings(e0,directory,config,queries[row['intent_id']]);assert_bindings(row,binding)
            for B in (4096,8192):
                record=assemble(row['results']['R4'],views,parents,'P0',B,'fixed_budget_main',c);record.update(intent_id=row['intent_id'],**binding)
                target.write(json.dumps(record,ensure_ascii=False)+'\n');target.flush();count+=1
            print('assembled',config,row['intent_id'],flush=True)
    save_json(directory/'context-cost.json',dict(wall_seconds=time.perf_counter()-started,contexts=count,contexts_sha256=sha(directory/'contexts.jsonl'),rankings_sha256=sha(directory/'rankings.jsonl'),generation_calls=0,remote_calls=0))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage',choices=['build','retrieve','contexts','matrix']);parser.add_argument('--e0',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--queries',type=Path);parser.add_argument('--config',choices=['all']+list(configurations()),default='all');args=parser.parse_args()
    if not args.output.is_dir():parser.error('output must be existing separately named E1 directory')
    for k in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE'):os.environ[k]='1'
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8';os.environ['ANONYMIZED_TELEMETRY']='False'
    e0=args.e0.resolve();output=args.output.resolve();queries=(args.queries or output/'queries.jsonl').resolve()
    verify_frozen(e0/'delivery-manifest.json');verify_input_copies(e0,output);load_queries(queries,80)
    if queries!=output/'queries.jsonl':raise ValueError('use the receipt-bound E1 query-only copy')
    ledger=output/'config-ledger.jsonl'
    selected=list(configurations()) if args.config=='all' else [args.config];m=models() if args.stage in ('build','retrieve','matrix') else None;failed=[]
    for config in selected:
        active_stage=args.stage
        try:
            if args.stage in ('build','matrix'):
                active_stage='build';record_stage(ledger,config,active_stage,'running');build(e0,output,config,m);record_stage(ledger,config,active_stage,'completed')
            if args.stage in ('retrieve','matrix'):
                active_stage='retrieve';record_stage(ledger,config,active_stage,'running');retrieve(e0,output,config,queries,m);record_stage(ledger,config,active_stage,'completed')
            if args.stage in ('contexts','matrix'):
                active_stage='contexts';record_stage(ledger,config,active_stage,'running');contexts(e0,output,config,queries);record_stage(ledger,config,active_stage,'completed')
            save_json(output/(f'status-{args.stage}-{config}.json'),dict(configuration_id=config,stage=args.stage,status='assembled' if args.stage in ('contexts','matrix') else 'built' if args.stage=='build' else 'retrieved',generation_calls=0))
        except Exception as exc:
            record_stage(ledger,config,active_stage,'failed',error=repr(exc))
            failed.append(config);save_json(output/(f'failure-{args.stage}-{config}.json'),dict(configuration_id=config,stage=active_stage,status='failed',error=repr(exc),traceback=traceback.format_exc(),generation_calls=0));print(config,'FAILED',repr(exc),flush=True)
    verify_frozen(e0/'delivery-manifest.json')
    if failed:raise RuntimeError('E1 stage failures: '+repr(failed))

if __name__=='__main__':main()
