"""Stage C custodian-only release; never retrieves or runs model forward."""
from pathlib import Path
import importlib.metadata as md
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / 'experiments/pearl-retrieval-eval-entry-20261003'
sys.path.insert(0, str(ENTRY))
import runtime as rt
import custody

OUT = ROOT / 'outputs/pearl-retrieval-eval200-release-20261003-03'
DATA = ROOT / 'outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01'
GOLD = DATA / 'pearl-retrieval-eval-200-adobe106-gold-20261003-r01.json'
INDEX = ROOT / 'outputs/pearl-index-106-adobe-20260929-01'
EXPERIMENT = Path(__file__).resolve().parent
CONFIG = ROOT / 'experiments/pearl-index-106-adobe-20260929/reranker-config.json'
FREEZE = ROOT / 'experiments/pearl-dev-review-freeze-20261003/method-freeze.json'

def checked(p, digest, readonly=False):
    assert rt.sha(p) == digest, 'immutable byte identity drift: ' + str(p)
    if readonly:
        assert p.stat().st_file_attributes & 1, 'sealed file is not readonly'

def hardware():
    script = "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); [pscustomobject]@{cpu=(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors);os=(Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,TotalVisibleMemorySize);gpu=(& nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader)} | ConvertTo-Json -Depth 5 -Compress"
    p = subprocess.run(['powershell','-NoProfile','-Command',script], capture_output=True, text=True, encoding='utf-8',check=True)
    import torch
    return dict(captured_at_utc=datetime.now(timezone.utc).isoformat(), actual=json.loads(p.stdout), python=sys.version, executable=sys.executable, torch_version=torch.__version__,torch_cuda=torch.version.cuda, forward_executed=False)

def main():
    assert not OUT.exists(), 'exclusive release output already exists'
    checked(DATA/'seal_manifest.json','c3524b0095e610e4ce325166f357903d3319da6dd0de23adc63277381d4a656b',True)
    checked(GOLD,'25c0e5d1d493155f23fdee1ff1d6773e0ea74f7b013e5ad4a2805423f4fd9d70',True)
    seal = rt.read(DATA/'seal_manifest.json')
    sealed = {ROOT/p:h for p,h in seal['sealed_evaluation_provenance_sha256'].items()}
    sealed[GOLD] = seal['artifacts']['eval']['sha256']
    sealed[DATA/'seal_manifest.json'] = rt.sha(DATA/'seal_manifest.json')
    for p,h in sealed.items(): checked(p,h,True)
    OUT.mkdir()
    rt.write(OUT/'seal-byte-verification.json',dict(status='passed',checked_files=len(sealed),readonly_files=len(sealed),gold_sha256=rt.sha(GOLD),seal_manifest_sha256=rt.sha(DATA/'seal_manifest.json'),note='Author/QC content not parsed; files only hashed.'))
    manifest=rt.read(INDEX/'build_manifest.json');config=rt.read(CONFIG)
    rt.verify_actual_method_metadata(manifest,config,rt.read(FREEZE))
    dev = DATA/'pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json'
    checked(dev,'4b118700b2ec810dd57d342ab3d5447b7d313c11aea73535dff160bfaba2d56c')
    # Development data is permitted only to produce five query-only warmups.
    development=rt.read(dev)
    development_order=list(development['intents'])
    random.Random(rt.SEED).shuffle(development_order)
    warm=[dict(intent_id=q['intent_id'],query=q['query']) for q in development_order[:5]]
    rt.write_rows(OUT/'warmup-queries.jsonl',warm)
    revisions={'dense':manifest['dense']['model_manifest']['revision'],'reranker':config['revision']}
    cfg=dict(backend='actual',policy=rt.POLICY,index_dir=str(INDEX),index_manifest=str(INDEX/'build_manifest.json'),model_config=str(CONFIG),model_revisions=revisions,warmup_queries_path=str(OUT/'warmup-queries.jsonl'),warmup_queries_sha256=rt.sha(OUT/'warmup-queries.jsonl'),warmup_development_ids=[q['intent_id'] for q in warm],runtime_files=[str(INDEX/n) for n in ('build_manifest.json','verification.json','child_chunks.jsonl','dense_ids.json','dense_vectors.npy','fts.sqlite3','sources.jsonl')]+[str(CONFIG),str(OUT/'warmup-queries.jsonl')])
    rt.write(OUT/'runtime-config.json',cfg)
    del development
    rt.write(OUT/'hardware.json',hardware())
    rt.write(OUT/'access-scope.json',dict(status='current',custodian='independent stage_c_custodian Agent; not retrieval executor or semantic reviewer',executor_inputs=['query-only/contract.json','query-only/queries.jsonl','warmup-queries.jsonl','release.json and external pin','frozen code/index/models/source assets'],executor_forbidden=['sealed Gold content','answers','atoms','requirements','support labels','author/QC judgments','custody module execution'],reviewer_inputs='Only per-intent neutral actual-child packet after retrieval; no rankings/methods/scores/old judgments',isolation='Independent Agent context and explicit input/subprocess contract; shared Windows account and unrestricted filesystem, no OS ACL security isolation claimed',sealed_materials='Existing readonly preserved; author/QC only byte hashed; Gold read only by sanctioned custody export; no content returned to executor',export_at_utc=datetime.now(timezone.utc).isoformat()))
    # Freeze the entire installed dependency inventory and installed-byte identity.
    installed=sorted((d.metadata['Name'],d.version) for d in md.distributions() if d.metadata.get('Name'))
    rt.write(OUT/'installed-dependencies.json',dict(python=sys.version,packages=[dict(name=n,version=v) for n,v in installed]))
    core={'numpy','torch','FlagEmbedding','transformers','tokenizers'}
    dep_paths=set(rt.dependency_files(core))
    # RECORD/METADATA for all packages plus all non-cache core installed files.
    for dist in md.distributions():
        for f in dist.files or []:
            name=str(f)
            if name.endswith(('.dist-info/METADATA','.dist-info/RECORD','.dist-info/WHEEL')) or (dist.metadata.get('Name','').lower() in {n.lower() for n in core} and not name.endswith('.pyc') and '__pycache__' not in name):
                p=Path(dist.locate_file(f)).resolve()
                if p.is_file(): dep_paths.add(p)
    files={}
    def add(p,category):
        p=Path(p).resolve()
        if p not in files: files[p]=dict(path=str(p),category=category,sha256=rt.sha(p),bytes=p.stat().st_size)
    protocol=ROOT/'paper/pearl-framework/layer-1-retrieval'
    for n in ('experiments.md','metrics.md','README.md'):add(protocol/n,'protocol')
    add(protocol/'statistical-methods.md','statistics')
    for base in (ROOT/'Knowledge-Base/src/ped_knowledge',ROOT/'Contracts/src/ped_contracts',ENTRY,rt.OLD,ROOT/'experiments/pearl-index-106-adobe-20260929'):
        for p in base.rglob('*.py'):add(p,'code')
    add(Path(__file__),'code')
    add(FREEZE,'method');add(CONFIG,'method')
    for p in INDEX.iterdir():
        if p.is_file():add(p,'child' if p.name=='child_chunks.jsonl' else 'index')
    for s in rt.rows(INDEX/'sources.jsonl'):
        for name,h in ((s['source_path'],s['sha256']),(s['document_path'],s['document_sha256'])):
            checked(ROOT/name,h);add(ROOT/name,'source')
    for name,h in manifest['input_sha256'].items():checked(ROOT/name,h);add(ROOT/name,'source')
    for base,assets in ((ROOT/'memPed/knowledge/models/bge-m3',manifest['dense']['actual_asset_sha256']),(ROOT/config['local_model_dir'],config['verified_files_sha256'])):
        for name,h in assets.items():checked(base/name,h);add(base/name,'model')
    for p in dep_paths:add(p,'dependencies')
    for p in (OUT/'warmup-queries.jsonl',OUT/'runtime-config.json',OUT/'hardware.json',OUT/'access-scope.json',OUT/'installed-dependencies.json',EXPERIMENT/'README.md',EXPERIMENT/'preregistration.md'):add(p,'view')
    # Gold and old-review identities are opaque external SHA bindings, never executor file inputs.
    r02=ROOT/'outputs/pearl-retrieval-dev80-gold-r02-20261003-01'
    prereg=dict(development_gold_r02_sha256=rt.sha(r02/'gold-r02.json'),development_selected_review_manifest_sha256=rt.sha(r02/'selected-review-manifest.json'),development_delivery_manifest_sha256=rt.sha(r02/'delivery-manifest.json'),sealed_evaluation_gold_sha256=rt.sha(GOLD),seal_manifest_sha256=rt.sha(DATA/'seal_manifest.json'),annotation_status='agent_reviewed_preliminary',human_verified=False,alternative_complete_groups=0,alternative_target_met=False,source_split='Authoring source-disjoint development/evaluation; all 106 sources remain jointly searchable; not unseen-literature generalization',limitations=['dev034 processing loss and denominator retained','dev030 within-source contradiction retained','pilot006 denominator retained','dev079 model-subgroup scope retained','three existing R4 regressions retained','D21-100 unreviewed unknown; absence is not negative evidence','gross measured latency and audit-adjusted estimates reported separately'],counts=dict(evaluation_intents=200,strata_each=50,source_count=106,child_count=6433,warmup_queries=5,timed_queries_target=600,scoring_cells_target=800,prefixes_target=3200,overall_metrics_target=48),output_directory='outputs/pearl-retrieval-eval200-20261003-01',actual_retrieval_queries_executed=0)
    rt.write(OUT/'preregistration.json',prereg);add(OUT/'preregistration.json','view')
    # Byte-only development and B bindings are opaque custodian evidence, not runtime input files.
    private_bindings={str((r02/n).resolve()):rt.sha(r02/n) for n in ('gold-r02.json','revision-manifest.json','selected-review-manifest.json','analysis-r02-01/support-map.json','analysis-r02-01/score-details.json','delivery-manifest.json')}
    revision=ROOT/'experiments/pearl-retrieval-gold-revision-r02'
    for p in revision.rglob('*.py'):add(p,'code')
    add(ROOT/'outputs/pearl-retrieval-eval200-audit-20261003-01/timing_and_inputs.py','code')
    add(ROOT/'outputs/pearl-retrieval-eval200-release-20261003-01/stage-C-preparation-failure.json','view')
    add(ROOT/'outputs/pearl-retrieval-eval200-release-20261003-02/stage-C-preexport-rejection.json','view')
    b_delivery=ROOT/'outputs/pearl-retrieval-eval-entry-synthetic-20261003-01/delivery-manifest.json'
    if b_delivery.exists():private_bindings[str(b_delivery.resolve())]=rt.sha(b_delivery)
    rt.write(OUT/'preexport-inputs-verified.json',dict(status='preexport_inputs_verified',backend='actual',split='evaluation_200',policy=rt.POLICY,model_revisions=revisions,dependencies={n:md.version(n) for n in sorted(core)},files=sorted(files.values(),key=lambda x:(x['category'],x['path'])),created_at_utc=datetime.now(timezone.utc).isoformat(),private_byte_bindings=private_bindings,sealed_readonly_byte_bindings={str(p.resolve()):h for p,h in sealed.items()},hardware_sha256=rt.sha(OUT/'hardware.json'),access_scope_sha256=rt.sha(OUT/'access-scope.json'),preregistration_sha256=rt.sha(OUT/'preregistration.json'),target_run_directory=str(ROOT/'outputs/pearl-retrieval-eval200-20261003-01'),target_audit_directory=str(OUT/'gate-verification'),actual_retrieval_queries_executed=0,model_forward_executed=False))
    print(json.dumps(dict(status='preexport_inputs_verified',candidate_path=str(OUT/'preexport-inputs-verified.json'),candidate_sha256=rt.sha(OUT/'preexport-inputs-verified.json'),files=len(files),sealed_readonly=len(sealed))))

def finalize(expected_candidate_sha256):
    candidate_path=OUT/'preexport-inputs-verified.json'
    checked(candidate_path,expected_candidate_sha256)
    candidate=rt.read(candidate_path)
    assert candidate['status']=='preexport_inputs_verified'
    for item in candidate['files']:checked(Path(item['path']),item['sha256'])
    for name,h in candidate['private_byte_bindings'].items():checked(Path(name),h)
    for name,h in candidate['sealed_readonly_byte_bindings'].items():checked(Path(name),h,True)
    contract=custody.export_queries(GOLD,OUT/'runtime-config.json',OUT/'query-only',200)
    rt.write(OUT/'enhanced-export-receipt.json',dict(status='query_only_exported',candidate_sha256=expected_candidate_sha256,export_at_utc=datetime.now(timezone.utc).isoformat(),role='independent custodian',contract_sha256=rt.sha(contract),queries_sha256=rt.sha(OUT/'query-only/queries.jsonl'),warmup_queries_sha256=rt.sha(OUT/'warmup-queries.jsonl'),gold_sha256=rt.sha(GOLD),expected_count=200,strata_each=50,fields=['intent_id','query'],no_retrieval_or_forward=True))
    files=list(candidate['files'])
    for p in (contract,OUT/'query-only/queries.jsonl',candidate_path,OUT/'enhanced-export-receipt.json'):
        files.append(dict(path=str(p.resolve()),category='view',sha256=rt.sha(p),bytes=p.stat().st_size))
    release={k:v for k,v in candidate.items() if k not in ('status','private_byte_bindings','sealed_readonly_byte_bindings','files')}
    release.update(status='frozen',contract_sha256=rt.sha(contract),files=files,candidate_sha256=expected_candidate_sha256,private_binding_receipt_sha256=expected_candidate_sha256,created_at_utc=datetime.now(timezone.utc).isoformat())
    rt.write(OUT/'release.json',release)
    rt.write(OUT/'release-pin.json',dict(release_sha256=rt.sha(OUT/'release.json'),note='External receipt fixed before gate; never recompute pin in run command.'))
    cmd=[sys.executable,str(ENTRY/'runtime.py'),'--contract',str(contract),'--release',str(OUT/'release.json'),'--release-sha256',rt.sha(OUT/'release.json'),'--output',str(OUT/'gate-verification'),'--verify-release-only']
    p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    rt.write(OUT/'gate-command-receipt.json',dict(command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError('existing Stage B actual release gate rejected; inspect gate receipt; do not change B')
    for name,h in candidate['sealed_readonly_byte_bindings'].items():checked(Path(name),h,True)
    rt.write(OUT/'stage-C-completion.json',dict(status='passed',release_sha256=rt.sha(OUT/'release.json'),contract_sha256=rt.sha(contract),queries_sha256=rt.sha(OUT/'query-only/queries.jsonl'),release_file_count=len(files),release_category_counts=dict(Counter(x['category'] for x in files)),sealed_readonly_hashes_verified=len(candidate['sealed_readonly_byte_bindings']),actual_retrieval_queries_executed=0,model_forward_executed=False,gate=rt.read(OUT/'gate-verification/release-gate.json')))
    print(json.dumps(rt.read(OUT/'stage-C-completion.json'),sort_keys=True))

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--approved-candidate-sha256':finalize(sys.argv[2])
    elif len(sys.argv)==1:main()
    else:raise SystemExit('Use no arguments for preexport candidate; finalize only with independently audited --approved-candidate-sha256 SHA')
