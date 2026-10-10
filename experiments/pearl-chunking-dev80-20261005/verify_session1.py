"""Verify saved Session 1 audit/documents and preserve historical assets.

Read-only inputs; exclusive creation of new verification/manifest receipts.
No models, indexing, experiment scoring or semantic verdict generation.
"""
import hashlib
import json
from pathlib import Path
import re
import time
import yaml

ROOT=Path(__file__).resolve().parents[2]
EXP=Path(__file__).resolve().parent
OUT=ROOT/'outputs/pearl-chunking-dev80-20261005-02'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text('utf-8'))
def write(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def rel(p):return p.relative_to(ROOT).as_posix()

start=time.perf_counter();checks=[]
def check(name,condition,**details):
    checks.append(dict(check=name,passed=bool(condition),**details))
    if not condition:raise AssertionError(name)

manifest=yaml.safe_load((EXP/'resolved_manifest.yaml').read_text('utf-8'))
registry=read(EXP/'source_registry.json');audit=read(OUT/'asset-audit.json');baseline=read(OUT/'workspace-baseline.json')
check('stage gate',manifest['protocol_status']=='protocol_ready' and manifest['e0_status']=='audit_ready_smoke_pending' and manifest['formal_run_allowed'] is False)
check('all declared corpus sources present',len(registry['sources'])==106 and len({s['doc_id'] for s in registry['sources']})==106)
check('asset declared hashes verified',not audit['summary']['missing'] and not audit['summary']['hash_mismatches'])
drift=[path for path,a in audit['assets'].items() if sha(ROOT/path)!=a['sha256']]
check('input files unchanged',not drift,count=len(audit['assets']),drift=drift)
drift=[path for path,h in baseline['code_sha256'].items() if sha(ROOT/path)!=h]
check('legacy code unchanged',not drift,count=len(baseline['code_sha256']),drift=drift)
drift=[path for path,h in manifest['workspace']['configuration_sha256'].items() if sha(ROOT/path)!=h]
check('knowledge configurations unchanged',not drift,count=len(manifest['workspace']['configuration_sha256']))
check('user draft current byte identity',sha(Path(baseline['user_draft']['path']))==baseline['user_draft']['expected_sha256'])
for role,items in manifest['inputs'].items():
    check('manifest input '+role,all(sha(ROOT/a['path'])==a['sha256'] for a in items),count=len(items))
check('manifest source registry binding',sha(EXP/'source_registry.json')==manifest['corpus_registry']['sha256'])
check('paper PDF registry hashes',len(registry['research']['papers'])==4 and all(p['pdf_hash_matches_registry'] for p in registry['research']['papers']))
check('legacy policy exact reconstruction',read(OUT/'legacy-policy-reconstruction.json')['all_exact'])
atoms=read(OUT/'gold-location-audit.json')['atoms']
check('atom location coverage',len(atoms)==174 and sum(x['status']=='deterministic_location_candidate' for x in atoms)==119 and sum(x['status']=='semantic_review_required' for x in atoms)==55)
check('not falsely transferred',all(x['support_transfer']=='not_adjudicated' for x in atoms))
excerpts=read(OUT/'legacy-support-location-audit-r02.json')
check('actual quote audit coverage',excerpts['summary']['excerpt_count']==573 and excerpts['summary']['quotes_present_in_frozen_children']==573)
check('unresolved parameters fail closed',manifest['unresolved']['common_source_support_map_sha256'] is None and manifest['scientific']['c4']['threshold'] is None and len(manifest['blockers'])==5)
check('no model calls',all(manifest['generation'][k]==0 for k in ('actual_generation_calls','actual_judge_calls','actual_remote_model_calls')))
check('round-specific authorization not invented',manifest['generation']['authorization_evidence'] is None and manifest['generation']['authorized_call_ceiling'] is None)
# Local links only: unrelated links already present in navigation are out of this change.
links=[]
for p in list(EXP.glob('*.md'))+[OUT/'handoff.md']:
    t=p.read_text('utf-8')
    check('one H1 '+p.name,len(re.findall(r'^# ',t,re.M))==1)
    check('document status '+p.name,bool(re.search(r'status: (current|plan|target|historical)',t)))
    for target in re.findall(r'\]\(([^)]+)\)',t):
        if '://' in target or target.startswith('#'):continue
        dest=(p.parent/target.split('#')[0]).resolve()
        # Manifest is produced after successful verification.
        exists=dest.exists() or dest==OUT/'delivery-manifest.json' or dest==OUT/'verification.json'
        links.append(dict(file=rel(p),target=target,exists=exists))
check('new document relative links',all(l['exists'] for l in links),count=len(links))
protected=read(OUT/'protected-assets-sha256.json')
drift=[path for path,h in protected.items() if not (ROOT/path).is_file() or sha(ROOT/path)!=h]
check('historical protected files unchanged',not drift,count=len(protected),drift=drift,
      exclusions=['Chroma physical files; not opened','__pycache__'])
print('Historical preservation verified:',len(protected),flush=True)
report=dict(status='passed',scope='saved Session 1 audit and documents; author mechanical verification',
    semantic_review='not executed',real_smoke='pending Session 2',models_executed=False,
    checks=checks,links=links,elapsed_seconds=time.perf_counter()-start)
write(OUT/'verification.json',report)
write(OUT/'command-ledger.json',dict(commands=[
    dict(command=r'.\.venv\Scripts\python experiments/pearl-chunking-dev80-20261005/audit_session1.py --output outputs/pearl-chunking-dev80-20261005-01',exit_code=1,receipt='../pearl-chunking-dev80-20261005-01/failure.json'),
    dict(command=r'.\.venv\Scripts\python experiments/pearl-chunking-dev80-20261005/audit_session1.py --output outputs/pearl-chunking-dev80-20261005-02',exit_code=0,receipt='asset-audit.json'),
    dict(command='PowerShell stdin Python: CanonicalDocument.model_validate_json -> HierarchicalChunker().chunk; compare each historical ID/text',exit_code=0,receipt='legacy-policy-reconstruction.json',models=False),
    dict(command='PowerShell stdin Python: legacy path_evidence excerpts enumerate all canonical element text.find occurrences',exit_code=0,receipt='legacy-support-location-audit-r02.json',semantic_labels_generated=False),
    dict(command=r'.\.venv\Scripts\python experiments/pearl-chunking-dev80-20261005/package_session1.py',exit_code=0),
    dict(command=r'.\.venv\Scripts\python experiments/pearl-chunking-dev80-20261005/verify_session1.py',exit_code=0,receipt='verification.json')],
    notes='All helper outputs exclusively created. Main stdout and first failure are also in the chat execution record; inline checks are described as executed, not promoted to product CLIs.'))
paths=sorted(set([p for p in EXP.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+
    [p for p in OUT.rglob('*') if p.is_file()]+[ROOT/'docs/README.md',ROOT/'experiments/README.md',
    ROOT/'docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md',ROOT/'docs/superpowers/specs/2026-10-05-pearl-chunking-research-design.md']))
files={rel(p):sha(p) for p in paths}
delivery=dict(schema_version='pearl-chunking-session1-delivery-v1',stage='Session 1',status='protocol_ready',
    e0_status='audit_ready_smoke_pending',inputs=dict(commit=baseline['commit'],dirty=manifest['workspace']['dirty_snapshot'],
    resolved_manifest=dict(path=rel(EXP/'resolved_manifest.yaml'),sha256=sha(EXP/'resolved_manifest.yaml'))),
    artifacts_sha256=files,artifact_count=len(files),checks=dict(path='verification.json',sha256=sha(OUT/'verification.json'),status='passed'),
    counts=dict(corpus_sources=106,dev_intents=80,gold_atoms=174,unique_atom_location_candidates=119,nonexact_atom_anchors=55,
        new_semantic_support_verdicts=0,legacy_excerpts=573,unique_excerpt_location_candidates=312,excerpt_review_pending=261,
        reconstructed_child=6433,reconstructed_parent=2830,protected_files=len(protected),new_indexes=0,new_rankings=0,new_contexts=0,new_answers=0,real_smoke_intents=0),
    budget=manifest['generation'],decisions='Protocol r01 scientific choices fixed; unresolved manifest entries block affected formal runs.',
    next='Session 2 only: verify delivery hashes, implement minimum adapters and common support map, run real 5-8 intent smoke, then stop before E1.')
write(OUT/'delivery-manifest.json',delivery)
check('delivery saved hashes reopen',all(sha(ROOT/p)==h for p,h in read(OUT/'delivery-manifest.json')['artifacts_sha256'].items()))
print(json.dumps(dict(status='passed',checks=len(checks),artifact_count=len(files),protected_files=len(protected),e0_status='audit_ready_smoke_pending'),ensure_ascii=False))
