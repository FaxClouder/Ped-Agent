"""Package and verify the Session 5A (E2) delivery; also emit the chain status file."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from runtime import ROOT, sha, save_json

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
EXP=ROOT/'experiments/pearl-chunking-dev80-20261005'
CHAIN=ROOT/'outputs/pearl-chunking-chain-20261006'
SELF={'delivery-manifest.json','delivery-verification-r02.json'}
CODE=['e2.py','e2_score.py','e2_prune_check.py','e2_review_export.py','e2_integrate_r11.py','e2_delivery_prep.py','e2_delivery.py','verify_e2.py','test_e2.py',
      'capture_command.py','runtime.py','e1.py','e1_batch.py','smoke.py','chunkers.py','source_view.py','assemble.py','score.py','e3_scope_revision.py','e1_visible_review.py','e1_visible_review_verify.py']
DOCS=['experiments/pearl-chunking-dev80-20261005/session5-e2-2026-10-06.md','experiments/pearl-chunking-dev80-20261005/README.md','experiments/README.md','docs/README.md',
      'docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md','outputs/pearl-chunking-dev80-20261006-12/handoff.md']

def rel(p):return Path(p).relative_to(ROOT).as_posix()

def artifacts():
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in SELF]
    out={rel(p):sha(p) for p in files}
    out.update({rel(EXP/c):sha(EXP/c) for c in CODE})
    out.update({d:sha(ROOT/d) for d in DOCS})
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
    a=artifacts();sel=json.loads((OUT/'e2-overlap-selection-r01.json').read_text('utf8'))
    save_json(target,dict(stage='E2',session='5A',status='verified',artifact_count=len(a),artifacts_sha256=a,
        selection={k:dict(status=v['status'],selected=v['selected'],threats=v['threats']) for k,v in sel['cores'].items()},first_choice_for_5B=sel['first_choice_for_5B'],
        mapping_sha256=sel['mapping_sha256'],verification_sha256=sha(OUT/'verification-e2-r01.json'),tests_receipt=rel(OUT/'tests-final-e2-r01.json'),
        generation_calls=0,judge_calls=0,E4_started=False,E5_started=False,human_verified=False))
    print('packaged',len(a),flush=True)

def verify():
    target=OUT/'delivery-verification-r02.json'
    if target.exists():raise FileExistsError(target)
    m=json.loads((OUT/'delivery-manifest.json').read_text('utf8'))
    drift=[n for n,h in m['artifacts_sha256'].items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    current=artifacts();missing=sorted(set(current)-set(m['artifacts_sha256']))
    bad={d:links(d) for d in DOCS};bad={k:v for k,v in bad.items() if v}
    tests=json.loads((OUT/'tests-final-e2-r01.json').read_text('utf8'))
    v=json.loads((OUT/'verification-e2-r01.json').read_text('utf8'))
    ok=not drift and not missing and not bad and tests['exit_code']==0 and v['status']=='passed' and m['generation_calls']==0
    save_json(target,dict(status='passed' if ok else 'failed',manifest_sha256=sha(OUT/'delivery-manifest.json'),artifact_count=m['artifact_count'],artifact_drift=drift,unlisted_artifacts=missing,
        broken_links=bad,documents_link_checked=DOCS,test_exit_code=tests['exit_code'],independent_verification=v['status'],generation_calls=0,E4_started=False,self_excluded=sorted(SELF)))
    print('delivery verification','passed' if ok else 'FAILED',drift[:3],missing[:3],bad,flush=True)
    return ok

def chain_status():
    target=CHAIN/'status-5A.json'
    if target.exists():raise FileExistsError(target)
    dv=json.loads((OUT/'delivery-verification-r02.json').read_text('utf8'))
    status='passed' if dv['status']=='passed' else 'failed'
    save_json(target,dict(stage='5A',status=status,reason=None if status=='passed' else 'delivery verification failed',run_dir=rel(OUT),handoff=rel(OUT/'handoff.md'),
        delivery_manifest=rel(OUT/'delivery-manifest.json'),delivery_manifest_sha256=sha(OUT/'delivery-manifest.json'),delivery_verification=rel(OUT/'delivery-verification-r02.json'),
        generation_calls=0,judge_calls=0,retries=0,cost_summary=None,
        notes='C2-L384 overlap frozen O0; C3-L256 pending_review. First choice for 5B: C2-L384-O0-M0 + P0 + 4K. Scoring map r11.'))
    print('chain status',status,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','verify','chain-status']);a=p.parse_args()
    {'package':package,'verify':verify,'chain-status':chain_status}[a.stage]()
