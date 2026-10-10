"""Independent single-configuration E3 worker; no retrieval or generation."""
import argparse
import os
from pathlib import Path
import e3_cached
from runtime import ROOT,sha,save_json

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--attempt',type=Path,required=True);p.add_argument('--config',required=True);a=p.parse_args()
    assert a.config in e3_cached.CONFIGS
    os.environ['HF_HUB_OFFLINE']='1';os.environ['RAYON_NUM_THREADS']='6'
    e3_cached.CONFIGS=(a.config,)
    def save_worker(path,value):
        if path.name=='runtime-r01.json':
            value['configuration_ids']=[a.config]
            value['assembly_driver']='e3_worker.py -> e3_cached.py'
            value['code_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(__file__)
            value['rayon_num_threads']=6
        if path.name=='cost-e3-r01.json':
            value.update(contexts=960,reused_contexts=160,new_contexts=800,scope='Single-config worker; measured incremental cost under recorded P/B/panel order. Cross-cell cache warming is included. 160 main P0 reused, not remeasured.')
        save_json(path,value)
    e3_cached.save_json=save_worker
    e3_cached.run(a.output.resolve(),a.attempt.resolve())
