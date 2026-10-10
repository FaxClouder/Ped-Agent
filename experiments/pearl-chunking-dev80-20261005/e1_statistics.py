"""E1 intent-cluster paired descriptive intervals with three-valued bounds."""
import argparse
import json
from pathlib import Path
import random
import numpy as np
from runtime import save_json,sha
from e1 import configurations

def rows(p):return [json.loads(l) for l in p.read_text('utf8').splitlines() if l.strip()]

def load_verified_scoring(output,verification_receipt):
    scores_path=(output/'scores-e1-r01.json').resolve();verification_receipt=Path(verification_receipt).resolve()
    verification=json.loads(verification_receipt.read_text('utf8'))
    if verification.get('status')!='passed':raise ValueError('passed verification receipt required for statistics')
    if verification.get('score_file_sha256')!=sha(scores_path):raise ValueError('verification receipt/score file binding drift')
    scores=json.loads(scores_path.read_text('utf8'));map_path=Path(scores['mapping_path'])
    if not map_path.is_absolute():map_path=scores_path.parent/map_path
    map_path=map_path.resolve()
    if scores.get('mapping_sha256')!=sha(map_path) or verification.get('mapping_sha256')!=scores.get('mapping_sha256'):raise ValueError('verification/scoring mapping binding drift')
    return scores,json.loads(map_path.read_text('utf8'))['records'],map_path

def require_verified_artifact(output,verification,config,filename):
    if verification.get('status')!='passed':raise ValueError('passed verification receipt required for artifact binding')
    check=verification.get('checks',{}).get(config)
    if not isinstance(check,dict) or check.get('status')!='passed':raise ValueError('passed per-configuration verification gate required')
    expected=check.get('artifact_sha256',{}).get(filename)
    if not isinstance(expected,str) or not expected:raise ValueError('required verifier artifact binding missing')
    path=output/('index-'+config)/filename
    if not path.is_file() or sha(path)!=expected:raise ValueError('verified artifact drift '+config+'/'+filename)
    return expected

def select_panel(records,panel,ids):
    if panel=='R4_CEGR10':chosen=[r for r in records if r['kind']=='layer1_raw' and r['method']=='R4' and r['k']==10]
    else:chosen=[r for r in records if r['kind']=='context' and r['stage']=='final' and r['budget']==(4096 if panel=='P0_CGC4096' else 8192)]
    lookup={r['intent_id']:r for r in chosen}
    if len(chosen)!=len(ids) or len(lookup)!=len(chosen) or set(lookup)!=set(ids):raise ValueError('duplicate or incomplete statistics panel coverage')
    return chosen,lookup

def success_metadata():
    """Explicitly account for the bootstrap-only statistics stage."""
    return dict(generation_calls=0,semantic_judgments_added=0,remote_model_calls=0,remote_judge_calls=0)

def run(output,verification_receipt):
    base='B0-regex320-overlap48-M0';configs=list(configurations())
    scores,maps,map_path=load_verified_scoring(output,verification_receipt);verification=json.loads(Path(verification_receipt).read_text('utf8'));ids=sorted(r['intent_id'] for r in maps);n=len(ids)
    if n!=80:raise ValueError('statistics requires exactly 80 scoring-map intents')
    strata={}
    for r in maps:strata.setdefault(r['main_stratum'],[]).append(r['intent_id'])
    for group in strata.values():group.sort()
    positions={i:j for j,i in enumerate(ids)};rng=random.Random(20261005)
    draws=np.asarray([[positions[rng.choice(strata[t])] for t in sorted(strata) for _ in strata[t]] for _ in range(10000)],dtype=np.int32)
    values={};tables=[];bindings={}
    for config in configs:
        path=output/('index-'+config)/'score-details-e1-r01.jsonl'
        bindings[config]=require_verified_artifact(output,verification,config,'score-details-e1-r01.jsonl');records=rows(path)
        for panel in ('R4_CEGR10','P0_CGC4096','P0_CGC8192'):
            chosen,lookup=select_panel(records,panel,ids)
            if any(r['failure'] for r in chosen):return dict(status='skipped_failed_matrix',reason='Technical failures cannot be converted to paired quality scores.',independent_intents=80)
            arr=np.asarray([[int(lookup[i]['sufficient']=='yes'),int(lookup[i]['sufficient']!='no')] for i in ids],dtype=float);values[config,panel]=arr
            boot=arr[draws].mean(axis=1);ci=np.quantile(boot,[.025,.975],axis=0,method='linear')
            tables.append(dict(configuration_id=config,panel=panel,n=n,lower_point=float(arr[:,0].mean()),possible_upper_point=float(arr[:,1].mean()),lower_estimate_ci=ci[:,0].tolist(),possible_upper_estimate_ci=ci[:,1].tolist(),unknown_n=sum(r['sufficient']=='unknown' for r in chosen),strata={t:dict(n=len(group),yes=sum(lookup[i]['sufficient']=='yes' for i in group),no=sum(lookup[i]['sufficient']=='no' for i in group),unknown=sum(lookup[i]['sufficient']=='unknown' for i in group)) for t,group in strata.items()}))
    paired=[]
    for config in configs:
        if config==base:continue
        for panel in ('R4_CEGR10','P0_CGC4096','P0_CGC8192'):
            a=values[config,panel];b=values[base,panel];delta=a[:,0]-b[:,0];bounds=np.stack([a[:,0]-b[:,1],a[:,1]-b[:,0]],axis=1)
            ci=np.quantile(bounds[draws].mean(axis=1),[.025,.975],axis=0,method='linear')
            paired.append(dict(configuration_id=config,baseline=base,panel=panel,n=n,certificate_lower_difference=float(delta.mean()),certificate_lower_difference_ci=np.quantile(delta[draws].mean(axis=1),[.025,.975],method='linear').tolist(),possible_delta_interval=bounds.mean(axis=0).tolist(),possible_delta_bootstrap_envelope=[float(ci[0,0]),float(ci[1,1])]))
    return dict(status='completed',verification_receipt_sha256=sha(verification_receipt),score_file_sha256=sha(output/'scores-e1-r01.json'),mapping_path=str(map_path),mapping_sha256=scores['mapping_sha256'],independent_intents=80,seed=20261005,replicates=10000,sampling_unit='underlying intent, shared draws across configurations and panels, within sorted strata',stratum_sizes={t:len(g) for t,g in strata.items()},quantile='numpy linear',scope='Development descriptive paired intervals. Unknown possible bounds are not confidence intervals or measured success; envelope combines uncertainty and sampling variation. No binary tests on unknown cells.',score_detail_bindings=bindings,overall=tables,paired=paired,**success_metadata())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--verification-receipt',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();save_json(a.receipt,run(a.output.resolve(),a.verification_receipt.resolve()));print('saved paired E1 statistics')

if __name__=='__main__':main()
