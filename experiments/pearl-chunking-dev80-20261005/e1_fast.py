"""Serial E1 driver with reviewed equivalent batched Unicode assembly search."""
import argparse
import json
import os
from pathlib import Path
import time
import traceback
import e1
from e1_batch import batched_search
from runtime import ROOT,EXP,sha,save_json,load_queries

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--e0',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--reuse-first',type=Path);a=p.parse_args()
    for k in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE'):os.environ[k]='1'
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8';os.environ['ANONYMIZED_TELEMETRY']='False';os.environ['RAYON_NUM_THREADS']='8'
    e0=a.e0.resolve();out=a.output.resolve();queries=out/'queries.jsonl';e1.verify_frozen(e0/'delivery-manifest.json');e1.verify_input_copies(e0,out);load_queries(queries,80)
    phase={'e1_fast.py':sha(__file__),'e1_batch.py':sha(EXP/'e1_batch.py'),'e1.py':sha(EXP/'e1.py'),'assemble.py':sha(EXP/'assemble.py')}
    save_json(out/'e1-phase-runtime.json',dict(code_sha256=phase,assembly_semantics='same descending exhaustive Unicode prefixes and exact serialization/token count; batched only',rayon_num_threads=8,serial_model_execution=True,generation_calls=0))
    start=time.perf_counter();m=e1.models();save_json(out/'model-load-cost-e1.json',dict(seconds=time.perf_counter()-start,scope='one shared model loading for serial remaining index and retrieval execution',local_cuda=True))
    ledger=out/'config-ledger.jsonl';failed=[]
    for config in e1.configurations():
        active='build'
        try:
            if a.reuse_first and config=='C1-L256-O0-M0':
                origin=a.reuse_first.resolve()/('index-'+config);target=out/('index-'+config)
                receipt=json.loads((out/'e1-current-run-cache-reuse.json').read_text('utf8'))
                if receipt['origin']!=str(origin):raise ValueError('cache reuse origin mismatch')
                for name,h in receipt['copied_sha256'].items():
                    if sha(origin/name)!=h or sha(target/name)!=h:raise ValueError('current E1 exact cache binding drift')
                e1.verified_identity(e0,out,config)
                for stage in ('build','retrieve'):e1.record_stage(ledger,config,stage,'completed',exact_current_E1_reuse=str(origin),new_model_execution=False)
            else:
                e1.record_stage(ledger,config,'build','running');e1.build(e0,out,config,m);e1.record_stage(ledger,config,'build','completed')
                active='retrieve';e1.record_stage(ledger,config,active,'running');e1.retrieve(e0,out,config,queries,m);e1.record_stage(ledger,config,active,'completed')
            active='contexts';e1.record_stage(ledger,config,active,'running')
            with batched_search():e1.contexts(e0,out,config,queries)
            e1.record_stage(ledger,config,active,'completed')
            save_json(out/f'status-matrix-{config}.json',dict(configuration_id=config,status='assembled',phase_code_sha256=phase,generation_calls=0))
        except Exception as exc:
            failed.append(config);e1.record_stage(ledger,config,active,'failed',error=repr(exc));save_json(out/f'failure-matrix-{config}.json',dict(configuration_id=config,stage=active,status='failed',error=repr(exc),traceback=traceback.format_exc(),generation_calls=0));print('FAILED',config,repr(exc),flush=True)
    e1.verify_frozen(e0/'delivery-manifest.json')
    if any(sha(EXP/n)!=h for n,h in phase.items()):raise ValueError('E1 execution phase runtime changed')
    save_json(out/'matrix-completion-e1.json',dict(status='passed' if not failed else 'failed',failed_configurations=failed,configuration_count=13,phase_code_sha256=phase,generation_calls=0))
    if failed:raise RuntimeError('E1 failed configurations '+repr(failed))

if __name__=='__main__':main()
