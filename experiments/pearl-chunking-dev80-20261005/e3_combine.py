"""Combine exclusively completed hash-bound cells into one E3 delivery identity."""
import argparse
from pathlib import Path
import shutil
from e3 import CONFIGS,SOURCE,rows,load
from runtime import ROOT,save_json,sha

def run(out,workers):
    base=load(workers[0]/'runtime-r01.json');cost=[];worker_bindings=[]
    for config,worker in zip(CONFIGS,workers):
        runtime=load(worker/'runtime-r01.json')
        for k in ('source_views_sha256','parent_sha256','tokenizer_sha256','map_sha256','ranking_inputs'):assert runtime[k]==base[k]
        for path,digest in runtime['code_sha256'].items():
            if path in base['code_sha256']:assert base['code_sha256'][path]==digest,'Shared worker code drift: '+path
            base['code_sha256'][path]=digest
        worker_bindings.append(dict(configuration_id=config,path=worker.relative_to(ROOT).as_posix(),runtime_sha256=sha(worker/'runtime-r01.json')))
        for path in sorted(worker.glob('contexts-'+config+'-*.jsonl')):
            receipt=path.with_name(path.stem+'-receipt.json');record=load(receipt)
            assert record['contexts_file_sha256']==sha(path) and record['contexts']==80
            assert len(list(rows(path)))==80
            target=out/path.name;assert not target.exists();shutil.copy2(path,target)
            shutil.copy2(receipt,out/receipt.name);cost.append(record)
    assert len(cost)==36
    base.update(configuration_ids=CONFIGS,assembly_driver='e3_cached original B0 worker + two single-configuration e3_worker processes',worker_bindings=worker_bindings,contexts=2880,reused_contexts=480,new_contexts=2400)
    save_json(out/'runtime-r01.json',base)
    shutil.copy2(workers[0]/'input-preservation-r01.json',out/'input-preservation-r01.json')
    shutil.copy2(workers[0]/'e3-selection-rule-r01.md',out/'e3-selection-rule-r01.md')
    save_json(out/'cost-e3-r01.json',dict(cells=cost,contexts=2880,reused_contexts=480,new_contexts=2400,index_builds=0,retrieval_calls=0,generation_calls=0,remote_judge_calls=0,scope='Incremental per-cell memoized assembly in P0/P1/P2, 4096/8192, main/diagnostic order within each intent. Later main cells can reuse diagnostic-warmed cache. Frozen P0 main=0 reuse cost, not intrinsic latency. Use cost-reference-e3-r02 for comparable latency. Worker configuration wall times are not summed into end-to-end latency.',unused_accelerator='e3_token_memo equivalence passed but real probe was slower; not used in final cells. Preliminary -07/-08 attempts kept; only closed B0 cells from -08 used.'))
    print('Combined',len(cost),'cells',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',nargs=3,type=Path,required=True);a=p.parse_args();run(a.output.resolve(),[w.resolve() for w in a.workers])
