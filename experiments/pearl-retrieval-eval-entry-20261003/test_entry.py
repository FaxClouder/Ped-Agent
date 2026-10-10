"""Independent synthetic contracts; no sealed-data fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def module(name):
    path = HERE / (name + '.py')
    assert path.exists(), 'missing Stage B implementation: ' + name
    spec = importlib.util.spec_from_file_location('entry_' + name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.mark.parametrize('n,split', [(80, 'development_80'), (200, 'evaluation_200')])
def test_synthetic_fullchain_and_independent_oracle(tmp_path, n, split):
    s = module('synthetic')
    result = s.deliver(tmp_path / 'new', counts=(n,))
    batch = result['batches'][str(n)]
    assert batch['split'] == split
    assert batch['first_pass_cells'] == n * 4
    assert batch['timed_queries'] == n * 3
    assert batch['r4_pairs'] == n * 3 * 24
    assert batch['warmup_queries'] == 5
    assert batch['warmup_pairs'] == 5 * 24
    assert batch['oracle'] == {'prefixes_verified': n * 16, 'overall_metrics_verified': 48}
    assert result['real_evaluation_runs'] == 0


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'extra', 'split', 'count', 'quota', 'cross_split', 'hash'])
def test_query_contract_fails_closed(tmp_path, mutation):
    s, r = module('synthetic'), module('runtime')
    assets = s.prepare(tmp_path / 'inputs', 80)
    contract = r.read(assets['contract'])
    rows = r.rows(contract['queries_path'])
    if mutation == 'missing': rows.pop()
    if mutation == 'duplicate': rows[-1] = rows[0]
    if mutation == 'extra': rows[0]['atom'] = 'leak'
    if mutation == 'cross_split': rows[0]['intent_id'] = 'syn-eval-001'
    if mutation == 'split': contract['split'] = 'evaluation_200'
    if mutation == 'count': contract['expected_count'] = 200
    if mutation == 'quota': contract['stratum_quotas']['single_source'] = 19
    if mutation == 'hash': contract['queries_sha256'] = '0' * 64
    Path(contract['queries_path']).write_text(''.join(json.dumps(q)+'\n' for q in rows), encoding='utf8')
    if mutation != 'hash': contract['queries_sha256'] = r.sha(contract['queries_path'])
    with pytest.raises(ValueError): r.validate_contract(contract)


@pytest.mark.parametrize('category', ['protocol', 'statistics', 'code', 'method', 'model', 'index', 'child', 'source', 'view', 'dependencies'])
def test_release_drift_rejected_before_backend(tmp_path, category):
    s, r = module('synthetic'), module('runtime')
    assets = s.prepare(tmp_path / 'inputs', 80)
    release = r.read(assets['release'])
    item = next(x for x in release['files'] if x['category'] == category)
    # Copy a selected asset so this test never edits shared source/dependencies.
    copied = tmp_path / 'selected.bin'
    copied.write_bytes(Path(item['path']).read_bytes())
    item['path'] = str(copied)
    r.write(tmp_path / 'release.json', release)
    copied.write_bytes(copied.read_bytes()+b'changed')
    invoked = []
    with pytest.raises(ValueError, match='drift'):
        r.execute(assets['contract'], tmp_path/'release.json', tmp_path/'run', lambda c: invoked.append(c), expected_release_sha256=r.sha(tmp_path/'release.json'))
    assert invoked == []


def test_failed_execution_keeps_failure_and_cannot_score(tmp_path):
    s, r, c = module('synthetic'), module('runtime'), module('custody')
    assets = s.prepare(tmp_path/'inputs', 80)
    class Fails:
        def __call__(self, query): raise RuntimeError('injected fixed failure')
    result = r.execute(assets['contract'], assets['release'], tmp_path/'run', lambda _: Fails(), retries=1, expected_release_sha256=r.sha(assets['release']))
    assert result['status'] == 'failed'
    assert len(result['execution_failures']) == 2
    assert result['quality_scores'] is None
    with pytest.raises(ValueError, match='execution'): c.load_run(tmp_path/'run', assets['gold'], 80)


def test_successful_retry_preserves_attempt_record(tmp_path):
    s, r = module('synthetic'), module('runtime')
    assets = s.prepare(tmp_path/'inputs', 80)
    backend = s.Backend(r.read(assets['contract']))
    class Flaky:
        failed = False
        def __call__(self, query):
            if not self.failed:
                self.failed = True
                raise RuntimeError('first attempt')
            return backend(query)
    result = r.execute(assets['contract'], assets['release'], tmp_path/'run', lambda _: Flaky(), retries=1, expected_release_sha256=r.sha(assets['release']))
    assert result['status'] == 'retrieval_complete'
    assert result['attempt_failures'] and not result['execution_failures']
    with pytest.raises(FileExistsError): r.execute(assets['contract'], assets['release'], tmp_path/'run', lambda _: backend, expected_release_sha256=r.sha(assets['release']))


def test_empty_short_rankings_valid_but_unrun_failed_rejected(tmp_path):
    s, c = module('synthetic'), module('custody')
    assets = s.prepare(tmp_path/'inputs', 80)
    q = c.read(assets['gold'])['intents'][0]
    for status in ('success', 'failed', 'not_run'):
        row = dict(intent_id=q['intent_id'], query=q['query'], method='R1', status=status,
                   returned=0, results=[], pass_number=1, empty_result_reason='legal_empty_candidate_set')
        if status == 'success': assert c.old_score.validate_ranking(row,q,{}) == []
        else:
            with pytest.raises(ValueError, match='execution'): c.old_score.validate_ranking(row,q,{})


def test_selected_full_sha_and_mapping_and_ranking_drift(tmp_path):
    s, c, r = module('synthetic'), module('custody'), module('runtime')
    s.deliver(tmp_path/'new', counts=(80,))
    run = tmp_path/'new/batch-80/run'
    gold = tmp_path/'new/batch-80/inputs/gold.json'
    mapping = run/'support-map.json'
    c.load_validated(run, gold, mapping, 80)
    value = r.read(mapping)
    value['intents'][0]['notes'] += 'tamper'
    mapping.write_text(json.dumps(value),encoding='utf8')
    with pytest.raises(ValueError): c.load_validated(run,gold,mapping,80)
    (run/'rankings.jsonl').write_text('',encoding='utf8')
    with pytest.raises(ValueError,match='hash|seal'): c.load_run(run,gold,80)


def test_runtime_static_imports_do_not_include_gold_custody():
    import ast
    tree = ast.parse((HERE/'runtime.py').read_text(encoding='utf8'))
    imports = [n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    assert not {'custody','synthetic','score','prepare','blind'} & set(imports)


def test_forward_tokens_and_candidate_body_checks():
    r = module('runtime')
    old = r.algorithm()
    with pytest.raises(ValueError,match='untruncated'): old.assert_actual_inputs([[1,2,3]],[[1,2]])
    with pytest.raises(ValueError,match='identity'): old.assert_candidate_identity([], [{'chunk_id':'x','text':'x','text_sha256':'bad'}])


@pytest.mark.parametrize('mode', ['init', 'vector', 'forward'])
def test_backend_failure_receipt_survives_non_query_failure(tmp_path, mode):
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',80)
    backend=s.Backend(r.read(assets['contract']))
    calls=0
    def factory(c):
        if mode=='init':raise RuntimeError('model initialization failure')
        def run(q):
            nonlocal calls
            calls+=1;value=backend(q)
            if mode=='forward':value['dense_audit']['truncated']=True
            if mode=='vector' and calls>85:value['vector'][0]=.5
            return value
        return run
    value=r.execute(assets['contract'],assets['release'],tmp_path/'run',factory,expected_release_sha256=r.sha(assets['release']))
    assert value['status']=='failed' and value['execution_failures']
    assert r.read(tmp_path/'run/run_manifest.json')['quality_scores'] is None


def test_saved_score_tamper_and_cli_independent_verify(tmp_path):
    s,c,r=module('synthetic'),module('custody'),module('runtime');s.deliver(tmp_path/'new',counts=(80,))
    run=tmp_path/'new/batch-80/run';gold=tmp_path/'new/batch-80/inputs/gold.json'
    assert c.verify_saved(run,gold,run/'support-map.json',80)['prefixes_verified']==1280
    scores=r.read(run/'score-details.json');scores['details'][0]['scores']['10']['CEGR']=99
    (run/'score-details.json').write_text(json.dumps(scores),encoding='utf8')
    with pytest.raises(ValueError):c.verify_saved(run,gold,run/'support-map.json',80)


@pytest.mark.parametrize('count', [0,3,100])
def test_execute_actual_candidate_counts_and_empty_full_reference(tmp_path,count):
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',200,child_count=count)
    value=r.execute(assets['contract'],assets['release'],tmp_path/'run',s.Backend,expected_release_sha256=r.sha(assets['release']))
    assert value['status']=='retrieval_complete'
    assert value['r4_pairs']==600*count and value['warmup_pairs']==5*count


@pytest.mark.parametrize('mutation',['duplicate','missing','sha','revision'])
def test_explicit_selection_and_raw_identity_reject(tmp_path,mutation):
    s,c,r=module('synthetic'),module('custody'),module('runtime');s.deliver(tmp_path/'new',counts=(80,))
    run=tmp_path/'new/batch-80/run';gold=tmp_path/'new/batch-80/inputs/gold.json'
    selection=r.read(run/'selected-review-manifest.json')
    if mutation=='duplicate':selection['files'][-1]=selection['files'][0]
    if mutation=='missing':selection['files'].pop()
    if mutation=='sha':selection['files'][0]['sha256']='0'*64
    if mutation=='revision':selection['identity_kind']='revision-analysis'
    r.write(tmp_path/'selection.json',selection)
    with pytest.raises(ValueError):c.combine(run,gold,tmp_path/'selection.json',tmp_path/'map.json',80)


def test_fixture_contains_joint_and_or_paths_and_multiple_sources(tmp_path):
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',80)
    gold=r.read(assets['gold'])
    assert any(len(q['requirements'])>1 for q in gold['intents'])
    assert any(len(q['requirements'][0]['support_bundles'])>1 for q in gold['intents'])
    assert any(len({a['source_id'] for a in q['atoms']})>1 for q in gold['intents'])


@pytest.mark.parametrize('change', ['omitted_code','omitted_index','omitted_dependencies','model_revision','manifest_pin','gold_content'])
def test_prelaunch_pins_and_consumed_assets_cannot_be_omitted(tmp_path,change):
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',80)
    release=r.read(assets['release']);contract=r.read(assets['contract'])
    if change=='omitted_code':release['files']=[f for f in release['files'] if not f['path'].endswith('score.py')]
    if change=='omitted_index':release['files']=[f for f in release['files'] if not f['path'].endswith('dense_vectors.npy')]
    if change=='omitted_dependencies':release['dependencies']={}
    if change=='model_revision':release['model_revisions']['dense']='other'
    if change=='gold_content':contract['requirements']=['must not leak']
    if change=='gold_content':
        assets['contract'].write_text(json.dumps(contract),encoding='utf8');release['contract_sha256']=r.sha(assets['contract'])
    r.write(tmp_path/'release.json',release)
    pin='0'*64 if change=='manifest_pin' else r.sha(tmp_path/'release.json')
    called=[]
    with pytest.raises(ValueError):r.execute(assets['contract'],tmp_path/'release.json',tmp_path/'run',lambda c:called.append(c),expected_release_sha256=pin)
    assert not called


def test_raw_run_gold_changes_require_separate_revision_identity(tmp_path):
    s,c,r=module('synthetic'),module('custody'),module('runtime');assets=s.prepare(tmp_path/'inputs',80)
    r.execute(assets['contract'],assets['release'],tmp_path/'run',s.Backend,expected_release_sha256=r.sha(assets['release']))
    gold=r.read(assets['gold']);gold['intents'][0]['requirements'][0]['support_bundles']=[['different']]
    r.write(tmp_path/'changed-gold.json',gold)
    with pytest.raises(ValueError,match='raw-run Gold'):c.load_run(tmp_path/'run',tmp_path/'changed-gold.json',80)


def test_custody_query_export_contains_no_gold_and_rejects_existing_output(tmp_path):
    s,c,r=module('synthetic'),module('custody'),module('runtime');assets=s.prepare(tmp_path/'inputs',80)
    path=c.export_queries(assets['gold'],assets['contract'],tmp_path/'export',80)
    contract=r.read(path);queries,warmups=r.validate_contract(contract)
    assert len(queries)==80 and len(warmups)==5
    assert all(set(q)=={'intent_id','query'} for q in queries)
    assert 'gold_path' not in contract and contract['custody_binding']['gold_sha256']==r.sha(assets['gold'])
    with pytest.raises(FileExistsError):c.export_queries(assets['gold'],assets['contract'],tmp_path/'export',80)


@pytest.mark.parametrize('n,split',[(80,'development'),(200,'sealed_independent_evaluation')])
def test_native_gold_schema_without_child_path(tmp_path,n,split):
    s,c,r=module('synthetic'),module('custody'),module('runtime');assets=s.prepare(tmp_path/'inputs',n)
    gold=r.read(assets['gold']);gold['split']=split;gold.pop('child_path',None)
    r.write(tmp_path/'native-gold.json',gold)
    path=c.export_queries(tmp_path/'native-gold.json',assets['contract'],tmp_path/'export',n)
    assert r.read(path)['expected_count']==n


def test_actual_method_metadata_matches_native_revision_schema():
    r=module('runtime')
    sparse={'analyzer_fingerprint':'fixed','bm25':{'k1':1.2,'b':.75},'fields':'body','ordering':'chunk'}
    dense={'model_manifest':{'revision':'dense-revision'},'actual_asset_sha256':{'weights':'fixedhash'},'max_length':1024}
    config={'revision':'reranker-revision','max_length':1024,'batch_size':8}
    freeze={'methods':{'R1':sparse,'R2':dense,'R3':{'depth':100,'rrf_k':60,'equal_weights':True},'R4':config}}
    r.verify_actual_method_metadata({'sparse':sparse,'dense':dense},config,freeze)
    changed=copy.deepcopy(config);changed['max_length']=512
    with pytest.raises(ValueError,match='method'):r.verify_actual_method_metadata({'sparse':sparse,'dense':dense},changed,freeze)


@pytest.mark.parametrize('change',['stub_code','alternate_index_manifest'])
def test_reviewer_consumed_file_gate_probes(tmp_path,change):
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',80)
    contract=r.read(assets['contract']);release=r.read(assets['release'])
    if change=='stub_code':
        contract['runtime_files']=[p for p in contract['runtime_files'] if not p.endswith('stub_backend.py')]
        release['files']=[f for f in release['files'] if not f['path'].endswith('stub_backend.py')]
    else:
        r.write(tmp_path/'alternate.json',{'max_length':1});contract['index_manifest']=str(tmp_path/'alternate.json')
        release['files'].append({'category':'index','path':str(tmp_path/'alternate.json'),'sha256':r.sha(tmp_path/'alternate.json')})
    r.write(tmp_path/'contract.json',contract);release['contract_sha256']=r.sha(tmp_path/'contract.json');r.write(tmp_path/'release.json',release)
    with pytest.raises(ValueError):r.verify_release(tmp_path/'release.json',r.sha(tmp_path/'release.json'),tmp_path/'contract.json',contract)


@pytest.mark.parametrize('change',['id','text_hash','tokens','query','duplicate'])
def test_pair_audit_identity_and_token_hash_reject(tmp_path,change):
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',80);contract=r.read(assets['contract'])
    query=r.rows(contract['queries_path'])[0];value=s.Backend(contract)(query)
    pair=value['pair_audits'][0]
    if change=='id':pair['chunk_id']='ghost'
    if change=='text_hash':pair['child_text_sha256']='bad'
    if change=='tokens':pair['model_input_ids']=[999]
    if change=='query':pair['query_text']='different query'
    if change=='duplicate':value['pair_audits'][1]=pair
    with pytest.raises(ValueError):r.validate_result(query,value,r.algorithm())


def test_abort_preserves_completed_queries_and_pending_checkpoint(tmp_path):
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',80);backend=s.Backend(r.read(assets['contract']))
    calls=0
    class Abort:
        def __init__(self,c):pass
        def __call__(self,q):
            nonlocal calls
            calls+=1
            if calls==8:raise KeyboardInterrupt('fixed late interruption')
            return backend(q)
    with pytest.raises(KeyboardInterrupt):r.execute(assets['contract'],assets['release'],tmp_path/'run',Abort,expected_release_sha256=r.sha(assets['release']))
    checkpoint=r.read(tmp_path/'run/checkpoint.json')
    assert checkpoint['completed_queries_by_pass']['1']==2
    assert checkpoint['pending']['pass_number']==1 and checkpoint['status']=='interrupted'
    records=r.rows(tmp_path/'run/completed-query-journal.jsonl')
    assert len(records)==7 and records[-1]['pass_number']==1
    assert r.read(tmp_path/'run/run_manifest.json')['status']=='interrupted'


def test_failed_query_only_cli_has_nonzero_exit(tmp_path):
    import subprocess
    s,r=module('synthetic'),module('runtime');assets=s.prepare(tmp_path/'inputs',80)
    contract=r.read(assets['contract']);index=Path(contract['index_dir'])
    ids=r.read(index/'dense_ids.json');ids[0]='missing-child';(index/'dense_ids.json').write_text(json.dumps(ids),encoding='utf8')
    manifest=r.read(index/'build_manifest.json');manifest['output_sha256']['dense_ids.json']=r.sha(index/'dense_ids.json')
    (index/'build_manifest.json').write_text(json.dumps(manifest),encoding='utf8')
    verification=r.read(index/'verification.json');verification['build_manifest_sha256']=r.sha(index/'build_manifest.json')
    (index/'verification.json').write_text(json.dumps(verification),encoding='utf8')
    release=r.read(assets['release'])
    for item in release['files']:item['sha256']=r.sha(item['path'])
    assets['release'].write_text(json.dumps(release),encoding='utf8')
    result=subprocess.run([sys.executable,str(HERE/'runtime.py'),'--contract',str(assets['contract']),'--release',str(assets['release']),
                           '--release-sha256',r.sha(assets['release']),'--output',str(tmp_path/'run')],capture_output=True,text=True)
    assert result.returncode!=0
    assert r.read(tmp_path/'run/run_manifest.json')['status']=='failed'
