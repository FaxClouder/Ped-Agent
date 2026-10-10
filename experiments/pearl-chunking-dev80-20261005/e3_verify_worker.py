"""Partition the unchanged E3 verification by frozen configuration."""
import argparse
import os
from pathlib import Path
import verify_e3_r04 as v
from runtime import sha,save_json

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--config',required=True);a=p.parse_args()
    assert a.config in v.CONFIGS;v.CONFIGS=(a.config,);os.environ['RAYON_NUM_THREADS']='6'
    def save_partition(path,value):
        value['configuration_id']=a.config;value['partition_driver_sha256']=sha(__file__)
        target=path.with_name(path.stem+'-'+a.config+'-r04.json');save_json(target,value)
    v.save_json=save_partition;v.verify(a.output.resolve())
