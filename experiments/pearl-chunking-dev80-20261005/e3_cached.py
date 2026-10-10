"""Equivalent E3 assembly with per-intent snapshot/search memo and frozen P0 reuse."""
import argparse
import copy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import statistics
import time
import assemble as a
from e1_batch import batched_search
from e3 import SOURCE,REVIEW,CLOSE,CONFIGS,PANELS,STAGES,rows,load
from runtime import ROOT,EXP,sha,save_json
from smoke import counter

@contextmanager
def memoized_assembly(c):
    snapshots={};searches={};old_snapshot=a.snapshot;old_search=a.truncate_with_offsets
    def snapshot(units,counter):
        k=a.digest(units)
        if k not in snapshots:snapshots[k]=old_snapshot(units,counter)
        return snapshots[k]
    def search(u,kept,views,budget,counter):
        k=a.digest([u,kept,budget])
        if k not in searches:searches[k]=old_search(u,kept,views,budget,counter)
        return searches[k]
    a.snapshot=snapshot;a.truncate_with_offsets=search
    try:yield
    finally:a.snapshot=old_snapshot;a.truncate_with_offsets=old_search

def project_p0(full,ranking,views,parents,B,c):
    started=time.perf_counter()
    record={k:v for k,v in full.items() if k in ('assembly_version','source_views_sha256','parent_graph_sha256')}
    record.update(panel_id='seed10_diagnostic',strategy='P0',budget=B,ranking_sha256=a.digest(ranking[:10]))
    for stage in STAGES:record[stage]=a.snapshot([u for u in full[stage]['units'] if u['rank']<=10],c)
    seeds={ch['chunk_id'] for ch in ranking[:10]}
    record['truncation']=[t for t in full['truncation'] if t['seed_chunk_id'] in seeds]
    record['dedup']=record['deduplicated'];record['assembly_seconds']=time.perf_counter()-started
    record['context_id']=a.digest({k:v for k,v in record.items() if k not in ('assembly_seconds','context_id')})
    return record

def run(output,attempt):
    output.mkdir(exist_ok=False)
    previous=load(attempt/'runtime-r01.json');pres=load(attempt/'input-preservation-r01.json')
    for run in (SOURCE,REVIEW,CLOSE):assert sha(run/'delivery-manifest.json')==pres[run.name]['manifest_sha256']
    assert sha(SOURCE/'source-views-prepared.json')==previous['source_views_sha256']
    assert sha(SOURCE/'public-parent-graph.json')==previous['parent_sha256']
    shutil.copy2(attempt/'input-preservation-r01.json',output/'input-preservation-r01.json')
    shutil.copy2(attempt/'e3-selection-rule-r01.md',output/'e3-selection-rule-r01.md')
    c=counter();assert c.fingerprint==previous['tokenizer_fingerprint']
    runtime=dict(previous,assembly_driver='e3_cached.py',prior_hash_audit_path=str(attempt/'input-preservation-r01.json'),prior_hash_audit_sha256=sha(attempt/'input-preservation-r01.json'),reuse='480 frozen P0 main contexts; P0 Top10 projected by rank; P1/P2 exact original algorithm with per-intent memoized snapshots/truncation')
    runtime['code_sha256'].update({(EXP/n).relative_to(ROOT).as_posix():sha(EXP/n) for n in ('e3_cached.py','verify_e3.py')})
    save_json(output/'runtime-r01.json',runtime)
    views=load(SOURCE/'source-views-prepared.json');parents=load(SOURCE/'public-parent-graph.json');cost=[]
    oldv=load(SOURCE/'verification-e1-r01.json')
    with batched_search():
        for config in CONFIGS:
            src=SOURCE/('index-'+config);rp=src/'rankings.jsonl';rh=sha(rp)
            assert rh==runtime['ranking_inputs'][config] and rh==oldv['checks'][config]['artifact_sha256']['rankings.jsonl']
            assert sha(src/'contexts.jsonl')==oldv['checks'][config]['artifact_sha256']['contexts.jsonl']
            frozen={(ctx['intent_id'],ctx['budget']):ctx for ctx in rows(src/'contexts.jsonl')}
            streams={};metrics={};start=time.perf_counter()
            for P in ('P0','P1','P2'):
                for B in (4096,8192):
                    for panel in PANELS:
                        cell=P,B,panel;path=output/f'contexts-{config}-{P}-{B}-{panel}.jsonl'
                        streams[cell]=path.open('x',encoding='utf8',newline='\n');metrics[cell]=dict(path=path,times=[],tokens=[],bytes=[],reuse=0)
            try:
                for j,row in enumerate(rows(rp),1):
                    ranking=row['results']['R4'];assert row['status']=='success'
                    with memoized_assembly(c):
                        for cell,stream in streams.items():
                            P,B,panel=cell;met=metrics[cell]
                            if P=='P0':
                                original=frozen[row['intent_id'],B]
                                if panel=='fixed_budget_main':
                                    ctx=dict(original);ctx['assembly_seconds']=0.;met['reuse']+=1
                                else:ctx=project_p0(original,ranking,views,parents,B,c)
                            else:ctx=a.assemble(ranking,views,parents,P,B,panel,c)
                            ctx.update(intent_id=row['intent_id'],configuration_id=config,ranking_file_sha256=rh,query_sha256=row['query_sha256'])
                            stream.write(json.dumps(ctx,ensure_ascii=False)+'\n');stream.flush()
                            met['times'].append(ctx['assembly_seconds']);met['tokens'].append(ctx['final']['token_count']);met['bytes'].append(len(ctx['final']['serialized_context'].encode()))
                    if j%5==0:print('assembled',config,j,'of80 x12contexts',round(time.perf_counter()-start,1),'seconds',flush=True)
            finally:
                for stream in streams.values():stream.close()
            for (P,B,panel),met in metrics.items():
                record=dict(configuration_id=config,strategy=P,budget=B,panel_id=panel,contexts=len(met['times']),wall_seconds=None,configuration_wall_seconds=time.perf_counter()-start,mean_seconds=statistics.mean(met['times']),median_seconds=statistics.median(met['times']),mean_final_tokens=statistics.mean(met['tokens']),serialized_bytes=sum(met['bytes']),contexts_file_sha256=sha(met['path']),reused_contexts=met['reuse'],memoized_execution=P!='P0',cost_caveat='Memo warm order P1 before P2, 4096 before8192, main before diagnostic; frozen main P0 cost=0 reuse, not intrinsic algorithm latency.')
                cost.append(record);save_json(output/(met['path'].stem+'-receipt.json'),record)
    save_json(output/'cost-e3-r01.json',dict(cells=cost,contexts=2880,reused_contexts=480,new_contexts=2400,index_builds=0,retrieval_calls=0,generation_calls=0,remote_judge_calls=0,scope='Measured incremental memoized assembly only. Reused main P0 cost zero, not a new P0 latency measurement. Main panel strategy costs exclude diagnostic amortization; configuration wall time includes all panels. Historical retrieval not added; provider/monetary cost NA.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--attempt',type=Path,required=True);args=p.parse_args()
    os.environ['HF_HUB_OFFLINE']='1';os.environ['RAYON_NUM_THREADS']='8';run(args.output.resolve(),args.attempt.resolve())
