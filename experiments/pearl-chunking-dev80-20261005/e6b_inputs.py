"""Session 6B input check: 6A delivery, frozen evaluation versions and calibration anchors (offline, no provider call)."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from runtime import ROOT, sha, save_json

S6A=ROOT/'outputs/pearl-chunking-dev80-20261006-14'
S5B=ROOT/'outputs/pearl-chunking-dev80-20261006-13'
CHAIN=ROOT/'outputs/pearl-chunking-chain-20261006'
S6A_MANIFEST_SHA='20c072421da5a0b2a2aeb8165b36da847319569537ea43e1c0ef538bcaaedb44'
L3CAL=ROOT/'outputs/pearl-answer-dev80-20261004-01/calibration'
L4CAL=ROOT/'outputs/pearl-layer4-dev80-20261004-01/calibration'


def load(p):return json.loads(Path(p).read_text(encoding='utf8'))


def check():
    errors=[]
    status=load(CHAIN/'status-6A-a3.json')
    if status['status']!='passed' or status['delivery_manifest_sha256']!=S6A_MANIFEST_SHA:errors.append('6A status/manifest binding')
    if sha(S6A/'delivery-manifest.json')!=S6A_MANIFEST_SHA:errors.append('6A manifest sha drift')
    manifest=load(S6A/'delivery-manifest.json')
    drift=[p for p,h in manifest['artifacts_sha256'].items() if sha(ROOT/p)!=h]
    if drift:errors.append(f'6A artifact drift {drift[:5]}')
    verification=load(S6A/'delivery-verification-r01.json')
    if verification['status']!='passed' or load(S6A/'verification-e5-r01.json')['status']!='passed':errors.append('6A verification not passed')
    records=sorted((S6A/'generation').glob('*.json'))
    returned=[load(p) for p in records]
    if len(returned)!=720 or any(r['generation_status']!='returned' or r['record_kind']!='real' for r in returned):errors.append('6A records not 720 returned real')
    evaluation=load(S5B/'evaluation-versions-r01.json')
    frozen={}
    for layer in ('layer3','layer4'):
        for key,value in evaluation[layer].items():
            if key.endswith('_sha256') and key[:-7] in evaluation[layer]:
                path=ROOT/evaluation[layer][key[:-7]]
                ok=sha(path)==value;frozen[evaluation[layer][key[:-7]]]=dict(sha256=value,match=ok)
                if not ok:errors.append(f'frozen evaluation drift {path}')
    anchors={}
    for name in ('judge-blind-packets-r01.json','expected-freeze-r01.json','calibration-gate-r01.json','anchors-r01.json'):
        anchors['L3/'+name]=sha(L3CAL/name)
    for name in ('anchors-r01.json','expected-r01.json','comparison-r02.json','context-judge-prompt-addendum-r02.json'):
        anchors['L4/'+name]=sha(L4CAL/name)
    packets=sorted((L4CAL/'judge-packets').rglob('*.json'))
    if len(packets)!=160:errors.append(f'L4 judge packets {len(packets)} != 160')
    return dict(time_utc=datetime.now(timezone.utc).isoformat(),status='passed' if not errors else 'failed',errors=errors,
                s6a_status_file='outputs/pearl-chunking-chain-20261006/status-6A-a3.json',
                s6a_manifest_sha256=sha(S6A/'delivery-manifest.json'),s6a_artifacts_checked=len(manifest['artifacts_sha256']),
                s6a_artifact_drift=len(drift),s6a_records=len(returned),frozen_evaluation=frozen,
                evaluation_versions_sha256=sha(S5B/'evaluation-versions-r01.json'),calibration_assets_sha256=anchors,
                l4_judge_packets=len(packets),provider_calls=0)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);a=ap.parse_args()
    result=check();save_json(a.out,result);print(json.dumps({k:result[k] for k in ('status','errors','s6a_artifacts_checked','s6a_artifact_drift','s6a_records')}))
    raise SystemExit(0 if result['status']=='passed' else 1)
