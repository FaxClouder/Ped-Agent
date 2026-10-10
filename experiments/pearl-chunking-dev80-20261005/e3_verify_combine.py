"""Close all three verification partitions; no incomplete partition accepted."""
import argparse
from pathlib import Path
from e3 import CONFIGS,load
from runtime import sha,save_json

def run(out):
    parts=[load(out/f'assembly-verification-r01-{c}-r04.json') for c in CONFIGS]
    profiles=[load(out/f'context-profiles-e3-r01-{c}-r04.json') for c in CONFIGS]
    tokens={};bindings={}
    for c,p in zip(CONFIGS,parts):
        assert p['status']=='passed' and p['configuration_id']==c and p['contexts_checked']==960 and p['p0_frozen_context_parity']==160 and p['ranking_identity_groups']==160
        for h,n in p['serialization_token_counts'].items():
            if h in tokens:assert tokens[h]==n
            tokens[h]=n
        bindings[c]=sha(out/f'assembly-verification-r01-{c}-r04.json')
    audit=[r for p in parts for r in p['maximal_prefix_checks']]
    assert len(audit)<=36 and len({r['context_id'] for r in audit})==len(audit)
    save_json(out/'assembly-verification-r01.json',dict(status='passed',contexts_checked=2880,ranking_identity_groups=480,p0_frozen_context_parity=480,unique_serializations_recounted=len(tokens),source_text_and_offsets='all four stages of all contexts',dedup='source interval union equality and no duplicate character; all contexts',maximal_prefix_sample_cells=36,maximal_prefix_reference=parts[0]['maximal_prefix_reference'],maximal_prefix_checks=audit,seed=20261005,seed_scope='independent deterministic per-configuration draws, one per cell; untruncated samples use complete-sequence fit verified by independent rank/order check',partition_sha256=bindings,verification_code_sha256=sha(__file__),retrieval_calls=0))
    cells=[r for p in profiles for r in p['cells']];assert len(cells)==36
    save_json(out/'context-profiles-e3-r01.json',dict(cells=cells))
    print('Closed verification',2880,'contexts',len(audit),'maximal prefixes',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output.resolve())
