"""Freeze E3 delivery and reopen every artifact and preserved output binding."""
import argparse
import re
import shutil
from pathlib import Path
from e3 import load
from runtime import ROOT,EXP,sha,save_json

def run(out):
    assert load(out/'stage-boundary-e3-r01.json')['status']=='complete'
    tests=out/'tests-final-r07.json';assert load(tests)['exit_code']==0
    snapshot=out/'code-snapshot-r01';snapshot.mkdir(exist_ok=False)
    files={p for pattern in ('e3*.py','test_e3*.py','verify_e3*.py') for p in EXP.glob(pattern)}
    files.update(EXP/n for n in ('assemble.py','e1_batch.py','score.py','e1_visible_review.py','e1_visible_review_verify.py','e1_closeout.py','smoke.py','runtime.py','capture_command.py'))
    for p in sorted(files):shutil.copy2(p,snapshot/p.name)
    prior=load(out/'input-preservation-r01.json');preserved={};document_changes=[]
    for run_name,audit in prior.items():
        for name,expected in audit['artifacts_sha256'].items():
            current=sha(ROOT/name)
            if name.startswith('outputs/'):
                assert current==expected,'Old output overwritten: '+name;preserved[name]=expected
            elif current!=expected:document_changes.append(dict(path=name,old_sha256=expected,new_sha256=current,scope='Current maintained navigation evolved to E3; old output snapshots preserved.'))
    save_json(out/'input-preservation-final-r01.json',dict(status='passed',preserved_output_files=len(preserved),old_output_sha256=preserved,current_source_or_navigation_changes=document_changes,scope='All previous input audit output bindings freshly rehashed; no old output drift.'))
    docs=[EXP/'session4-e3-2026-10-06.md',EXP/'README.md',ROOT/'experiments/README.md',ROOT/'docs/README.md',out/'handoff.md']
    targets=[]
    for p in docs:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text('utf8')):
            if '://' in target or target.startswith('#'):continue
            resolved=(p.parent/target.split('#')[0]).resolve()
            # Manifest and the self-verification are written immediately below.
            if resolved not in (out/'delivery-manifest.json',out/'delivery-verification-r01.json'):assert resolved.exists(),str(resolved)
            targets.append(dict(document=p.relative_to(ROOT).as_posix(),target=target))
    save_json(out/'document-links-r01.json',dict(status='passed',links=len(targets),records=targets,self_records_created_after_link_check=True))
    artifacts=[p for p in out.rglob('*') if p.is_file()]
    artifacts+=docs[:-1]
    artifacts+=sorted(files)
    artifacts += [p for p in (ROOT/'outputs').glob('e3-*') if p.is_file()]
    artifacts=sorted(set(artifacts));hashes={p.relative_to(ROOT).as_posix():sha(p) for p in artifacts}
    inputs={name:dict(path=name,sha256=digest) for name,digest in preserved.items()}
    save_json(out/'delivery-manifest.json',dict(stage='E3',status='complete',artifact_count=len(hashes),artifacts_sha256=hashes,inputs=inputs,independent_intents=80,contexts=2880,top100_main_contexts=1440,top10_diagnostic_contexts=1440,scoring_versions=['r07','r08','r09','r10'],selected_recovery=load(out/'stage-boundary-e3-r01.json')['selected_recovery'],test_receipt=tests.relative_to(ROOT).as_posix(),E2_started=False,generation_calls=0,retrieval_calls=0,index_builds=0,scope='Final -11 plus code, current navigation and attempt logs; prior -07/-08 partials preserved but not accepted as final comparison cells. Manifest and its final verifier are self-excluded.'))
    reopened=load(out/'delivery-manifest.json')
    for name,digest in reopened['artifacts_sha256'].items():assert sha(ROOT/name)==digest
    for item in reopened['inputs'].values():assert sha(ROOT/item['path'])==item['sha256']
    for x in targets:
        p=ROOT/x['document'];resolved=(p.parent/x['target'].split('#')[0]).resolve()
        if resolved!=out/'delivery-verification-r01.json':assert resolved.exists()
    save_json(out/'delivery-verification-r01.json',dict(status='passed',artifact_count=len(hashes),input_bindings=len(inputs),artifact_drift=[],input_drift=[],document_links=len(targets),test_exit_code=0,manifest_sha256=sha(out/'delivery-manifest.json'),self_excluded=True,E2_started=False,generation_calls=0,retrieval_calls=0,code_sha256=sha(__file__)))
    assert (out/'delivery-verification-r01.json').exists()
    print('Delivery reopened',len(hashes),'artifacts',len(inputs),'input bindings',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output.resolve())
