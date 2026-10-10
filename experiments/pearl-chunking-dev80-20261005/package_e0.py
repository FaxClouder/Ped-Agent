"""Read-only preservation recheck and exclusive E0 handoff packaging."""
import argparse
import json
import re
import subprocess
from pathlib import Path
import yaml
from runtime import ROOT,EXP,sha,save_json,cache_identity,verify_index

def load(path):return json.loads(Path(path).read_text('utf8'))
def preservation(output):
    previous=ROOT/'outputs/pearl-chunking-dev80-20261005-02'
    delivery=load(previous/'delivery-manifest.json');audit=load(previous/'asset-audit.json');baseline=load(previous/'workspace-baseline.json')
    collections={'session1_delivery':delivery['artifacts_sha256'],'historical_protected':load(previous/'protected-assets-sha256.json'),'assets':{p:a['sha256'] for p,a in audit['assets'].items()},'legacy_code':baseline['code_sha256']}
    checks={}
    for name,files in collections.items():
        drift=[p for p,h in files.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
        checks[name]={'count':len(files),'drift':drift}
        if drift:raise ValueError('preservation drift '+name+': '+repr(drift))
    result={'status':'passed','checks':checks,'session1_manifest_sha256':sha(previous/'delivery-manifest.json')}
    save_json(output/'preservation-final-r01.json',result);print('preservation passed',checks,flush=True)

def package(output):
    # Fail before any completion marker/navigation mutation if packaging is not ready.
    targets=[output/p for p in ('command-ledger.json','workspace-final.json','docs-navigation-session1-original.md','navigation-update.json','document-verification.json','delivery-manifest.json','delivery-verification.json')]+[EXP/'resolved_manifest_session2.yaml']
    if any(p.exists() for p in targets):raise FileExistsError('fresh exclusive package targets required')
    nav=ROOT/'docs/README.md'
    if 'session2-execution.md' in nav.read_text('utf8'):raise ValueError('navigation already modified')
    links=[]
    for p in (EXP/'session2-execution.md',EXP/'reproduction_commands.md',output/'handoff.md'):
        text=p.read_text('utf8')
        if len(re.findall(r'^# ',text,re.M))!=1 or 'status: current' not in text:raise ValueError('document contract '+str(p))
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'):continue
            dest=(p.parent/target.split('#')[0]).resolve();valid=dest.exists() or dest==output/'delivery-manifest.json' or dest==EXP/'resolved_manifest_session2.yaml'
            links.append({'file':p.relative_to(ROOT).as_posix(),'target':target,'exists':valid})
    if not all(x['exists'] for x in links):raise ValueError('broken delivery links')
    verified=load(output/'verification-r01.json');assets=load(output/'assets-verification-r03.json');preserved=load(output/'preservation-final-r01.json');scores=load(output/'score-smoke-r01.json');visible=load(output/'visible-review-verification-r01.json')
    if any(r['status']!='passed' for r in (verified,assets,preserved,visible)):raise ValueError('E0 gates incomplete')
    if visible['review_sha256']!=sha(output/'independent-visible-context-reviews-r01.json') or visible['contexts_sha256']!=sha(output/'contexts.jsonl') or visible['packet_file_sha256']!=sha(output/'visible-context-review-packets-r01.json'):raise ValueError('visible review binding drift')
    for name,h in verified['artifacts_sha256'].items():
        if sha(output/name)!=h:raise ValueError('saved verification input changed '+name)
    for name,h in assets['input_sha256'].items():
        path=output/'calibration-r02'/name if name in ('semantic-threshold.json','sentence-model-inputs.jsonl','sentence-vectors.npy') else output/name
        if sha(path)!=h:raise ValueError('saved source/calibration audit input changed '+name)
    verify_index(output/'index-C1-L384-O0-M0/manifest.json')
    tests=load(output/'command-targeted-tests-final-r02.json')
    if tests['exit_code']!=0 or '179 passed' not in tests['stdout']:raise ValueError('test receipt mismatch')
    ranks=[json.loads(l) for l in (output/'rankings.jsonl').read_text('utf8').splitlines()];contexts=[json.loads(l) for l in (output/'contexts.jsonl').read_text('utf8').splitlines()]
    if len(ranks)!=8 or any(r['status']!='success' for r in ranks) or len(contexts)!=96 or len(scores['details'])!=416:raise ValueError('actual counts incomplete')
    index=load(output/'index-C1-L384-O0-M0/manifest.json');threshold=load(output/'calibration-r02/semantic-threshold.json')
    for name,h in index['configuration']['code'].items():
        if name!=(EXP/'assemble.py').relative_to(ROOT).as_posix() and sha(ROOT/name)!=h:raise ValueError('runtime code drift '+name)
    equivalence=load(output/'assembly-optimization-equivalence-review-r01.json')
    if equivalence['status']!='passed' or sha(EXP/'assemble.py')!=equivalence['current_assembly_sha256']:raise ValueError('reviewed assembly phase code drift')
    if any(sha(output/name)!=h for name,h in equivalence['input_sha256'].items()):raise ValueError('assembly equivalence input drift')
    commands=[]
    for p in sorted(output.glob('command-*.json')):
        r=load(p);commands.append({'receipt':p.name,'receipt_sha256':sha(p),**r})
    save_json(output/'command-ledger.json',{'commands':commands,'all_attempts_retained':True,'scope':'All recorded stage attempts present at freeze; package command receipt is an explicitly external post-freeze envelope.','external_package_receipt':'command-package-final-r01.json','final_success_receipts':['command-prepare-r01.json','command-calibrate-r02.json','command-build-r02.json','command-retrieve-r01.json','command-contexts-r02.json','command-score-r01.json','command-verify-r01.json','command-assets-audit-r03.json','command-targeted-tests-final-r02.json']})
    code={p.relative_to(ROOT).as_posix():sha(p) for p in EXP.glob('*.py')}
    save_json(output/'workspace-final.json',{'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'status_porcelain':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),'experiment_code_sha256':code,'legacy_code_unchanged':True})
    phase={'index_and_retrieval_code_sha256':index['configuration']['code'],'assembly_code_sha256':sha(EXP/'assemble.py'),'evaluation_code_sha256':{p:sha(EXP/p) for p in ('evaluate.py','score.py','support.py','verify.py')},'equivalence_receipts':['parent-filter-equivalence-review-r01.json','assembly-optimization-equivalence-review-r01.json'],'assembly_change_scope':'P2 document prefilter and lazy equivalent source hash; index/rankings preserved, no model re-execution required','current_retrieve_code_gate':'Rebuilding under current code requires a new output identity; old index manifest is not rewritten.'}
    config={'schema_version':'pearl-chunking-session2-resolved-v1','stage':'Session 2','status':'E0_complete','formal_run_scope':'engineering E0 only; E1 not executed','session1_manifest_sha256':preserved['session1_manifest_sha256'],'input_artifacts_sha256':{p:sha(output/p) for p in ('source-views-prepared.json','table-snapshot.json','public-parent-graph.json','queries.jsonl','smoke-selection.json','common-support-map-r03.json')},'semantic_calibration':{'threshold':threshold['threshold'],'quantile':.9,'method':'linear','sentences':len(threshold['sentences']),'pairs':len(threshold['pairs']),'manifest_sha256':sha(output/'calibration-r02/semantic-threshold.json'),'model_inputs_max_length':2048},'tokenizer':index['configuration']['tokenizer'],'models':index['configuration']['models'],'index_configuration':index['configuration'],'phase_code_provenance':phase,'panels':['fixed_budget_main','seed10_diagnostic'],'strategies':['P0','P1','P2'],'budgets':[4096,8192],'table':{'row_budget':256,'repeated_header':'none'},'parents':{'max_tokens':1536,'independent_of_child_boundaries':True},'support':{'reviewed':8,'pending_unknown':72,'map_revision':'r03','missing_certificate_coverage':'unknown','runtime_gold_access':False},'calls':{'generation':0,'remote_judge':0,'authorization_evidence':None,'authorized_call_ceiling':None},'selection':'C1-L384-O0-M0 smoke configuration fixed before scores; no strategy selected','next':'Separate Session 3 only after user authorization and hash checks; unresolved semantic support must remain unknown or be reviewed before affected claims.'}
    with (EXP/'resolved_manifest_session2.yaml').open('x',encoding='utf8') as f:yaml.safe_dump(config,f,allow_unicode=True,sort_keys=False)
    # Navigational maintenance is explicit and occurs after the old hash receipt.
    nav=ROOT/'docs/README.md';old=sha(nav)
    with (output/'docs-navigation-session1-original.md').open('xb') as f:f.write(nav.read_bytes())
    addition='\n- [PEARL 切片 Session 2 E0 执行交接](../experiments/pearl-chunking-dev80-20261005/session2-execution.md)、[重现命令](../experiments/pearl-chunking-dev80-20261005/reproduction_commands.md)：8个固定开发意图真实冒烟、公共来源/表格/parent、双面板与独立复算完成；停止于E0，72题语义映射仍pending/unknown，未运行E1（current）。\n'
    nav.write_text(nav.read_text('utf8')+addition,encoding='utf8')
    save_json(output/'navigation-update.json',{'path':'docs/README.md','before_sha256':old,'original_bytes_preserved':'docs-navigation-session1-original.md','original_copy_sha256':sha(output/'docs-navigation-session1-original.md'),'after_sha256':sha(nav),'session1_delivery_exception':'Only current docs navigation intentionally appended after all36 were reverified; original36 byte identities preserved via this copy. All old output and experiment documents unchanged.','reason':'Register new maintained Session 2 documents; Session 1 manifest unchanged.'})
    save_json(output/'document-verification.json',{'status':'passed','links':links})
    paths=[p for p in output.rglob('*') if p.is_file()]+[p for p in EXP.glob('*') if p.is_file()]+[nav]
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}
    manifest={'schema_version':'pearl-chunking-session2-delivery-v1','stage':'Session 2','status':'E0_complete','inputs':{'session1_manifest':'outputs/pearl-chunking-dev80-20261005-02/delivery-manifest.json','sha256':preserved['session1_manifest_sha256']},'artifacts_sha256':hashes,'artifact_count':len(hashes),'checks':{'saved_outputs':'verification-r01.json','source_and_calibration':'assets-verification-r03.json','preservation_before_navigation':'preservation-final-r01.json','tests':'command-targeted-tests-final-r02.json','independent_review':'code-review-r05.md'},'counts':{'sources':106,'tables':502,'parents':3734,'children':5388,'real_smoke_intents':8,'successful_retrieval_methods':32,'rerank_pairs':800,'contexts':96,'score_details':416,'score_cells':52,'tests_passed':179,'source_reviewed_intents':8,'source_pending_unknown_intents':72,'generation_calls':0,'remote_judge_calls':0,'E1_units':0},'phase_code_provenance':phase,'budget':config['calls'],'decisions':config['selection'],'next':config['next'],'hash_exclusions':['delivery-manifest.json itself','delivery-verification.json generated after packaging','command-package-final-r01.json: post-freeze command envelope captured in memory, never an active hashed log','future newly appended reproduction receipts']}
    save_json(output/'delivery-manifest.json',manifest)
    # Reopen saved manifest independently of in-memory hashes.
    saved=load(output/'delivery-manifest.json');drift=[p for p,h in saved['artifacts_sha256'].items() if sha(ROOT/p)!=h]
    if drift:raise ValueError('delivery saved-file drift '+repr(drift))
    save_json(output/'delivery-verification.json',{'status':'passed','artifact_count':len(saved['artifacts_sha256']),'drift':drift,'delivery_manifest_sha256':sha(output/'delivery-manifest.json'),'E1':'not executed','generation_calls':0})
    print('E0 delivery passed',len(hashes),'saved files',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['preservation','package']);p.add_argument('--output',type=Path,required=True);a=p.parse_args();globals()[a.stage](a.output.resolve())

if __name__=='__main__':main()
