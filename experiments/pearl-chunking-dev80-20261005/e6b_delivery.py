"""Session 6B (blocked) delivery: manifest over the run directory, code and frozen inputs; verification; chain status."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from runtime import ROOT, sha, save_json

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-15'
EXP=ROOT/'experiments/pearl-chunking-dev80-20261005'
CHAIN=ROOT/'outputs/pearl-chunking-chain-20261006'
SELF={'delivery-manifest.json','delivery-verification-r01.json'}
CODE=['e6b_inputs.py','e6b_judge.py','e6b_prompts.py','e6b_calibrate.py','e6b_packets.py','e6b_gate.py','e6b_delivery.py','runtime.py']
EXTERNAL=['outputs/pearl-chunking-chain-20261006/authorization-e5-r02.json','outputs/pearl-chunking-chain-20261006/task-6B-a2.md',
          'outputs/pearl-chunking-chain-20261006/chain-contract-r03.md','outputs/pearl-chunking-dev80-20261006-14/delivery-manifest.json',
          'outputs/pearl-chunking-dev80-20261006-13/evaluation-versions-r01.json',
          'experiments/pearl-answer-dev80-20261004/judge-prompt-r01.md','experiments/pearl-answer-dev80-20261004/rubrics.md',
          'experiments/pearl-answer-dev80-20261004/score.py','experiments/pearl-layer4-dev80-20261004/judge-prompt-r01.md',
          'experiments/pearl-layer4-dev80-20261004/rubrics.md','experiments/pearl-layer4-dev80-20261004/compare_calibration.py',
          'outputs/pearl-layer4-dev80-20261004-01/calibration/context-judge-prompt-addendum-r02.json',
          'outputs/pearl-answer-dev80-20261004-01/calibration/judge-blind-packets-r01.json','outputs/pearl-answer-dev80-20261004-01/calibration/expected-freeze-r01.json',
          'outputs/pearl-layer4-dev80-20261004-01/calibration/expected-r01.json']


def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()


def files():
    own=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in SELF]
    return [rel(p) for p in own]+[rel(EXP/c) for c in CODE]+EXTERNAL


def package():
    gate=load(OUT/'calibration-gate-r01.json')
    save_json(OUT/'delivery-manifest.json',{'session':'6B','attempt':'a2','stage':'E5 evaluation','status':'blocked',
        'reason':'judge calibration failed at original thresholds; research judging cost would also exceed account balance',
        'artifacts_sha256':{p:sha(ROOT/p) for p in files()},'artifact_count':len(files()),
        'calibration_gate_sha256':sha(OUT/'calibration-gate-r01.json'),'calibration_status':gate['status'],
        'judge_model':gate['judge_model'],'calibration_calls':gate['calls'],'research_judge_calls':0,'generation_calls':0,
        'retries':gate['retries'],'usage':gate['usage'],'cost_usd':gate['cost_usd'],'human_verified':False,'E6_started':False,
        'scoring':'not performed','final_report':'not produced'})


def verify():
    m=load(OUT/'delivery-manifest.json');errors=[]
    drift=[p for p,h in m['artifacts_sha256'].items() if sha(ROOT/p)!=h]
    unlisted=[rel(p) for p in OUT.rglob('*') if p.is_file() and p.name not in SELF and rel(p) not in m['artifacts_sha256']]
    links={}
    for p in [OUT/'handoff.md']:
        for target in re.findall(r'\]\(([^)#]+)\)',p.read_text(encoding='utf8')):
            if not (p.parent/target).resolve().exists():links.setdefault(rel(p),[]).append(target)
    research=[p for p in OUT.rglob('*.json') if 'research-packets' in str(p) or 'research-judge' in str(p)]
    ledger=[json.loads(l) for l in (OUT/'calibration/judge-ledger-r01.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
    records=list((OUT/'calibration/judge-r01').rglob('*.json'))
    if len(records)!=200 or len(ledger)!=200:errors.append('calibration record/ledger count')
    if any(load(p)['parsed'] is None for p in records):errors.append('unparsed calibration record')
    if load(OUT/'calibration-gate-r01.json')['status']!='failed':errors.append('gate status')
    if drift or unlisted or links or research:errors.append('drift/unlisted/links/research artifacts')
    save_json(OUT/'delivery-verification-r01.json',{'status':'passed' if not errors else 'failed','errors':errors,'artifact_drift':drift,
        'unlisted_artifacts':unlisted,'broken_links':links,'research_judge_artifacts':len(research),'calibration_records':len(records),
        'ledger_rows':len(ledger),'manifest_sha256':sha(OUT/'delivery-manifest.json'),'self_excluded':sorted(SELF)})
    print(json.dumps({'status':'passed' if not errors else 'failed','errors':errors,'links':links,'unlisted':unlisted[:5]}))


def status(name):
    gate=load(OUT/'calibration-gate-r01.json')
    save_json(CHAIN/name,{'stage':'6B','status':'blocked',
        'reason':('deepseek-v4-pro failed the frozen calibration thresholds: Layer 3 sentinels 3/5 (alternative_group_splicing, missing_integration failed); '
                  'Layer 4 citation 31/36=0.861 and behavior 32/40=0.800 < 0.95, sentinels 6/8. Remote calls stopped; no research packet judged; '
                  'thresholds/rubrics/prompts unchanged. Independently, projected research judging cost (~13-53 USD) exceeds the account balance (20.35 CNY). '
                  'User decision required (judge identity/mode, reviewer roles, or budget); do not auto-resume 6B.'),
        'run_dir':rel(OUT),'handoff':rel(OUT/'handoff.md'),'delivery_manifest':rel(OUT/'delivery-manifest.json'),
        'delivery_manifest_sha256':sha(OUT/'delivery-manifest.json'),'delivery_verification':rel(OUT/'delivery-verification-r01.json'),
        'generation_calls':0,'judge_calls':gate['calls'],'judge_calls_note':'200 calibration calls; 0 research judge calls','retries':gate['retries'],
        'cost_summary':{'usage':gate['usage'],'estimated_usd':gate['cost_usd'],'balance_before_cny':20.61,'balance_after_cny':20.35,
                        'note':'source-bound estimate from the official pricing page read 2026-10-07; not an invoice'}})


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['package','verify','status']);ap.add_argument('--name',default='status-6B-a2.json');a=ap.parse_args()
    {'package':package,'verify':verify,'status':lambda:status(a.name)}[a.cmd]()
