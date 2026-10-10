"""Package and verify the Session 5B (E4 + final freeze) delivery; also emit the chain status file."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from runtime import ROOT, sha, save_json

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-13'
EXP=ROOT/'experiments/pearl-chunking-dev80-20261005'
CHAIN=ROOT/'outputs/pearl-chunking-chain-20261006'
SELF={'delivery-manifest.json','delivery-verification-r01.json'}
CODE=['e4.py','e4_score.py','e4_review_export.py','e4_review_results_r12.py','e4_integrate_r12.py','e5_plan.py','verify_e4.py','test_e4.py','e4_delivery.py','e4_check_5a.py',
      'e2.py','e2_integrate_r11.py','capture_command.py','runtime.py','e1.py','e1_batch.py','smoke.py','chunkers.py','source_view.py','assemble.py','score.py',
      'e3_scope_revision.py','e1_visible_review.py','e1_visible_review_verify.py','test_e2.py','test_source_chunks.py']
DOCS=['experiments/pearl-chunking-dev80-20261005/session5b-e4-2026-10-06.md','experiments/pearl-chunking-dev80-20261005/README.md','experiments/README.md','docs/README.md',
      'docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md','outputs/pearl-chunking-dev80-20261006-13/handoff.md']
EXTERNAL=['experiments/pearl-answer-dev80-20261004/generator-config-r01.json','experiments/pearl-answer-dev80-20261004/generate.py','outputs/pearl-chunking-chain-20261006/authorization-e5-r01.json']

def rel(p):return Path(p).relative_to(ROOT).as_posix()

def artifacts():
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in SELF and '__pycache__' not in p.parts]
    out={rel(p):sha(p) for p in files}
    out.update({rel(EXP/c):sha(EXP/c) for c in CODE})
    out.update({d:sha(ROOT/d) for d in DOCS+EXTERNAL})
    return out

def links(doc):
    bad=[];text=(ROOT/doc).read_text('utf8')
    for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)',text):
        if target.startswith(('http://','https://','mailto:')) or Path(target).name in SELF:continue
        if not ((ROOT/doc).parent/target).exists():bad.append(target)
    return bad

def package():
    target=OUT/'delivery-manifest.json'
    if target.exists():raise FileExistsError(target)
    a=artifacts();f=json.loads((OUT/'final-config-freeze-r01.json').read_text('utf8'));plan=json.loads((OUT/'e5-call-plan-r01.json').read_text('utf8'))
    save_json(target,dict(stage='E4+final-freeze',session='5B',status='verified',artifact_count=len(a),artifacts_sha256=a,
        e4_decision=dict(status=f['decision']['status'],selected=f['decision']['selected'],threats=f['decision']['threats'],existing_identity=f['decision']['existing_identity_if_pending']),
        final_configurations=[dict(configuration_id=r['configuration_id'],config_id=r['config_id'],role=r['role']) for r in f['configurations']],
        mapping_sha256=sha(OUT/'common-support-map-e4-r12.json'),e5_call_plan_sha256=sha(OUT/'e5-call-plan-r01.json'),planned_provider_calls=plan['calls']['planned_provider_calls'],
        verification_sha256=sha(OUT/'verification-e4-r01.json'),tests_receipt=rel(OUT/'tests-final-e4-r01.json'),
        generation_calls=0,judge_calls=0,E5_started=False,human_verified=False))
    print('packaged',len(a),flush=True)

def verify():
    target=OUT/'delivery-verification-r01.json'
    if target.exists():raise FileExistsError(target)
    m=json.loads((OUT/'delivery-manifest.json').read_text('utf8'))
    drift=[n for n,h in m['artifacts_sha256'].items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    current=artifacts();missing=sorted(set(current)-set(m['artifacts_sha256']))
    bad={d:links(d) for d in DOCS};bad={k:v for k,v in bad.items() if v}
    tests=json.loads((OUT/'tests-final-e4-r01.json').read_text('utf8'))
    v=json.loads((OUT/'verification-e4-r01.json').read_text('utf8'))
    ok=not drift and not missing and not bad and tests['exit_code']==0 and v['status']=='passed' and m['generation_calls']==0 and m['judge_calls']==0
    save_json(target,dict(status='passed' if ok else 'failed',manifest_sha256=sha(OUT/'delivery-manifest.json'),artifact_count=m['artifact_count'],artifact_drift=drift,unlisted_artifacts=missing,
        broken_links=bad,documents_link_checked=DOCS,test_exit_code=tests['exit_code'],independent_verification=v['status'],generation_calls=0,judge_calls=0,E5_started=False,self_excluded=sorted(SELF)))
    print('delivery verification','passed' if ok else 'FAILED',drift[:3],missing[:3],bad,flush=True)
    return ok

def chain_status():
    target=CHAIN/'status-5B-a1.json'
    if target.exists():raise FileExistsError(target)
    dv=json.loads((OUT/'delivery-verification-r01.json').read_text('utf8'))
    status='passed' if dv['status']=='passed' else 'failed'
    save_json(target,dict(stage='5B',status=status,reason=None if status=='passed' else 'delivery verification failed',run_dir=rel(OUT),handoff=rel(OUT/'handoff.md'),
        delivery_manifest=rel(OUT/'delivery-manifest.json'),delivery_manifest_sha256=sha(OUT/'delivery-manifest.json'),delivery_verification=rel(OUT/'delivery-verification-r01.json'),
        generation_calls=0,judge_calls=0,retries=0,
        cost_summary=dict(remote_calls=0,monetary_cost=None,local_cuda=dict(m1_build_wall_seconds=147.1,m1_dense_seconds=98.1,m1_retrieval_wall_seconds=109.9,model_load_seconds=117.1)),
        notes='E4 M0/M1 pending_review (M0 existing identity). Final freeze: C2-L384-O0-M0, C3-L256-O0-M0, B0-regex320-overlap48-M0 (P0, 4K). Map r12. E5 plan: deepseek-flash, 720 planned calls, global retry cap 144; judge cap 4680 packets. E5 entry: outputs/pearl-chunking-dev80-20261006-13/e5-call-plan-r01.json'))
    print('chain status',status,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','verify','chain-status']);a=p.parse_args()
    {'package':package,'verify':verify,'chain-status':chain_status}[a.stage]()
