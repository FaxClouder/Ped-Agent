"""Query-only execution boundary. Never import custody or open Gold/review content."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'experiments/pearl-retrieval-dev80-20261003'
METHODS = ('R1', 'R2', 'R3', 'R4')
KS = (1, 5, 10, 20)
SEED = 20260929
SPLITS = {'development_80':80, 'evaluation_200':200}
STRATA = ('single_source', 'numeric_table', 'within_paper_multi', 'cross_paper')
POLICY = dict(protocol='retrieval-v0.2', depth=100, k=list(KS), primary='CEGR@10',
              seed=SEED, rrf_k=60, tie_break='chunk_id ascending', passes=3,
              comparisons=['R2-R1','R3-R2','R4-R3'], bootstrap_repeats=10000)
CATEGORIES = {'protocol','statistics','code','method','model','index','child','source','view','dependencies'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding='utf8'))
def rows(path): return [json.loads(x) for x in Path(path).read_text(encoding='utf8').splitlines() if x.strip()]


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,sort_keys=True,indent=2,ensure_ascii=False);f.write('\n')


def write_rows(path, values):
    with Path(path).open('x',encoding='utf8',newline='\n') as f:
        for value in values:f.write(json.dumps(value,sort_keys=True,ensure_ascii=False)+'\n')


def dependency_files(names):
    result=[]
    for name in names:
        dist=importlib.metadata.distribution(name)
        chosen=[f for f in (dist.files or []) if str(f).endswith('.dist-info/METADATA') or str(f).lower()==name.lower().replace('-','_')+'/__init__.py']
        if not chosen:raise ValueError('dependency installation identity unavailable: '+name)
        result.extend(Path(dist.locate_file(f)).resolve() for f in chosen)
    return result


def algorithm():
    spec = importlib.util.spec_from_file_location('query_only_original_runner',OLD/'run.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def validate_contract(c):
    if c.get('identity_kind') != 'raw-run': raise ValueError('raw-run identity required; revision-analysis is separate')
    count = SPLITS.get(c.get('split'))
    if count is None or c.get('expected_count') != count: raise ValueError('split/count mismatch')
    if c.get('stratum_quotas') != {h:count//4 for h in STRATA}: raise ValueError('stratum quota mismatch')
    forbidden = {'gold','gold_path','atoms','requirements','reference_answer','labels','support_labels','author_log','qc'}
    def safe(v):
        if isinstance(v,dict):
            if set(v)&forbidden: raise ValueError('Gold custody content in query-only contract')
            for x in v.values():safe(x)
        elif isinstance(v,list):
            for x in v:safe(x)
    safe(c)
    if sha(c['queries_path']) != c['queries_sha256']: raise ValueError('query-only hash mismatch')
    queries=rows(c['queries_path'])
    if len(queries)!=count or len({q.get('intent_id') for q in queries})!=count:raise ValueError('missing/duplicate query')
    if any(set(q)!= {'intent_id','query'} or any(not isinstance(v,str) or not v.strip() for v in q.values()) for q in queries):raise ValueError('query-only fields')
    if [q['intent_id'] for q in queries] != c.get('intent_ids'): raise ValueError('cross-split input identity')
    if c.get('policy')!=POLICY:raise ValueError('fixed method/protocol/statistics policy drift')
    warmups=rows(c['warmup_queries_path'])
    if len(warmups)!=5 or len({q.get('intent_id') for q in warmups})!=5 or any(set(q)!= {'intent_id','query'} for q in warmups):raise ValueError('warmup query-only input')
    if sha(c['warmup_queries_path'])!=c['warmup_queries_sha256']:raise ValueError('warmup hash drift')
    if any(i not in c['warmup_development_ids'] for i in [q['intent_id'] for q in warmups]):raise ValueError('warmup must use explicitly bound development IDs')
    return queries,warmups


def verify_actual_method_metadata(manifest,config,freeze):
    methods=freeze['methods']
    if methods['R2']!=manifest['dense'] or methods['R4']!=config or methods['R3']!={'depth':100,'rrf_k':60,'equal_weights':True}:raise ValueError('frozen actual method configuration drift')
    for k in ('analyzer_fingerprint','bm25','fields','ordering'):
        if manifest['sparse'][k]!=methods['R1'][k]:raise ValueError('frozen actual R1 method drift')


def verify_release(path, expected_sha256, contract_path, c):
    if not expected_sha256 or sha(path)!=expected_sha256:raise ValueError('selected release manifest hash drift')
    release=read(path)
    if release.get('status')!='frozen' or release.get('policy')!=POLICY or release.get('split')!=c['split']:raise ValueError('release protocol/split drift')
    if release.get('contract_sha256')!=sha(contract_path):raise ValueError('release input view drift')
    files=release.get('files',[])
    if {x['category'] for x in files}!=CATEGORIES:raise ValueError('release asset category coverage')
    seen=set()
    for item in files:
        p=Path(item['path']).resolve()
        key=(item['category'],str(p))
        if key in seen:raise ValueError('duplicate selected release asset')
        seen.add(key)
        if sha(p)!=item['sha256']:raise ValueError('release '+item['category']+' drift: '+str(p))
    selected={str(Path(x['path']).resolve()) for x in files}
    required={str(Path(x).resolve()) for x in c['runtime_files']}
    # Verify the actual code used, including dependency implementation, rather than arbitrary category placeholders.
    actual_code={Path(__file__).resolve(),OLD/'run.py',ROOT/'experiments/pearl-index-106-adobe-20260929/build.py',
                 ROOT/'experiments/pearl-index-106-adobe-20260929/compare_pilot.py',ROOT/'experiments/pearl-index-106-adobe-20260929/rerank_pilot.py'}
    actual_code |= set((ROOT/'Knowledge-Base/src/ped_knowledge').rglob('*.py'))
    actual_code |= set((ROOT/'Contracts/src/ped_contracts').rglob('*.py'))
    actual_code |= {Path(__file__).with_name('custody.py'),OLD/'score.py',OLD/'protocol.py',OLD/'analyze.py',OLD/'verify.py',OLD/'blind.py',ROOT/'experiments/pearl-index-106-adobe-20260929/score_pilot.py'}
    actual_code |= {ROOT/'paper/pearl-framework/layer-1-retrieval/experiments.md',ROOT/'paper/pearl-framework/layer-1-retrieval/metrics.md'}
    if c['backend']=='synthetic-stub':actual_code.add(Path(__file__).with_name('stub_backend.py'))
    required |= {str(p.resolve()) for p in actual_code}
    packages={'numpy'} if c['backend']=='synthetic-stub' else {'numpy','torch','FlagEmbedding','transformers','tokenizers'}
    if set(release.get('dependencies',{}))!=packages:raise ValueError('dependency coverage drift')
    required |= {str(p) for p in dependency_files(packages)}
    index=Path(c['index_dir'])
    if Path(c['index_manifest']).resolve()!=(index/'build_manifest.json').resolve():raise ValueError('consumed index manifest path differs from gated index')
    required |= {str((index/n).resolve()) for n in ('build_manifest.json','verification.json','child_chunks.jsonl','dense_ids.json','dense_vectors.npy','fts.sqlite3')}
    required |= {str(Path(c[k]).resolve()) for k in ('index_manifest','model_config','queries_path','warmup_queries_path')}
    if release.get('model_revisions')!=c.get('model_revisions'):raise ValueError('model revision drift')
    manifest=read(index/'build_manifest.json');config=read(c['model_config'])
    verification=read(index/'verification.json')
    if verification.get('status')!='passed' or verification.get('build_manifest_sha256')!=sha(index/'build_manifest.json'):raise ValueError('actual index verification drift')
    for name,h in manifest['output_sha256'].items():
        if sha(index/name)!=h:raise ValueError('selected index/manifest drift')
    if c['backend']=='actual':
        dense_assets=manifest['dense']['actual_asset_sha256'];rerank_assets=config['verified_files_sha256']
        dense_minimum={'pytorch_model.bin','model_manifest.json','config.json','tokenizer.json','tokenizer_config.json','sentencepiece.bpe.model'}
        rerank_minimum={'model.safetensors','config.json','tokenizer.json','tokenizer_config.json','sentencepiece.bpe.model'}
        if not dense_minimum<=set(dense_assets) or not rerank_minimum<=set(rerank_assets):raise ValueError('actual model asset set incomplete or empty')
        source_rows=rows(index/'sources.jsonl');child_rows=rows(index/'child_chunks.jsonl')
        if manifest.get('source_count')!=106 or manifest.get('child_count')!=6433 or len(source_rows)!=106 or len(child_rows)!=6433:raise ValueError('actual corpus/source/child membership incomplete')
        if len({s['source_id'] for s in source_rows})!=106 or len({s['sha256'] for s in source_rows})!=106 or len({s['chunk_id'] for s in child_rows})!=6433:raise ValueError('actual corpus duplicate identity')
        method_freeze=ROOT/'experiments/pearl-dev-review-freeze-20261003/method-freeze.json'
        required.add(str(method_freeze.resolve()))
        verify_actual_method_metadata(manifest,config,read(method_freeze))
        if list((ROOT/'memPed/knowledge/models/bge-m3').glob('*.safetensors')):raise ValueError('competing dense model weights drift')
        required.add(str((index/'sources.jsonl').resolve()))
        for source in source_rows:
            for relative,h in [(source['source_path'],source['sha256']),(source['document_path'],source['document_sha256'])]:
                path=(ROOT/relative).resolve();required.add(str(path))
                if sha(path)!=h:raise ValueError('actual source/canonical drift')
        for relative,h in manifest['input_sha256'].items():
            path=(ROOT/relative).resolve();required.add(str(path))
            if sha(path)!=h:raise ValueError('actual index source/input drift')
        required |= {str((ROOT/'memPed/knowledge/models/bge-m3'/n).resolve()) for n in manifest['dense']['actual_asset_sha256']}
        required |= {str((ROOT/config['local_model_dir']/n).resolve()) for n in config['verified_files_sha256']}
        for name,h in manifest['dense']['actual_asset_sha256'].items():
            if sha(ROOT/'memPed/knowledge/models/bge-m3'/name)!=h:raise ValueError('actual dense model drift')
        for name,h in config['verified_files_sha256'].items():
            if sha(ROOT/config['local_model_dir']/name)!=h:raise ValueError('actual reranker model drift')
        if c['model_revisions']!={'dense':manifest['dense']['model_manifest']['revision'],'reranker':config['revision']}:raise ValueError('selected actual model revision drift')
    if not required<=selected:raise ValueError('release missing consumed actual assets/code')
    for name,version in release['dependencies'].items():
        if importlib.metadata.version(name)!=version:raise ValueError('dependency version drift: '+name)
    if release.get('backend')!=c['backend']:raise ValueError('release backend/model revision drift')
    return dict(status='passed',release_sha256=expected_sha256,checked_files=len(files),contract_sha256=sha(contract_path))


class ActualBackend:
    """Reuse original real retrieval and captured forward-token validation after the release gate."""
    def __init__(self,c):
        import numpy as np
        import torch
        self.old=algorithm();self.index=Path(c['index_dir'])
        manifest=read(c['index_manifest']);config=read(c['model_config'])
        if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable; no fallback')
        for key in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE'):os.environ[key]='1'
        os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
        random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.cuda.manual_seed_all(SEED)
        torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
        torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        if manifest['seed']!=SEED or config['seed']!=SEED:raise ValueError('model seed drift')
        self.old.reject_competing_dense_weights(ROOT/'memPed/knowledge/models/bge-m3')
        child_rows=rows(self.index/'child_chunks.jsonl');self.children={x['chunk_id']:x for x in child_rows}
        if len(self.children)!=len(child_rows):raise ValueError('duplicate frozen child IDs')
        self.ids=read(self.index/'dense_ids.json');self.vectors=np.load(self.index/'dense_vectors.npy',allow_pickle=False)
        if set(self.ids)!=set(self.children) or len(set(self.ids))!=len(self.ids):raise ValueError('index membership')
        self.old.build.validate_vectors(self.vectors,len(self.ids))
        self.old.build.verify_fts(self.index/'fts.sqlite3',list(self.children.values()))
        self.models=self.old.Models(manifest,config)

    def __call__(self,q):
        results,union,vector,dense,pairs,times=self.old.retrieve(self.models,self.index,self.vectors,self.ids,self.children,q['query'])
        # Independently reconstruct the tokenized query/full-child pairs with the loaded, release-bound tokenizer.
        expected=self.old.rerank.audit_inputs(self.models.reranker.tokenizer,q['query'],results['R3'],self.models.config)
        if [p['model_input_ids'] for p in pairs]!=[p['model_input_ids'] for p in expected]:raise ValueError('adapter model token reconstruction mismatch')
        return dict(backend='actual',results=results,union=union,vector=vector.tolist(),dense_audit=dense,pair_audits=pairs,times=times)


def validate_result(q,result,old):
    if set(result['results'])!=set(METHODS):raise ValueError('unrun method')
    for m,rs in result['results'].items():
        if len(rs)>100 or len({x['chunk_id'] for x in rs})!=len(rs):raise ValueError('candidate depth/duplicate')
        if [x['rank'] for x in rs]!=list(range(1,len(rs)+1)):raise ValueError('original ranks')
        for x in rs:
            if old.text_sha(x['text'])!=x['text_sha256']:raise ValueError('candidate body hash')
            if not isinstance(x['score'],(int,float)) or not math.isfinite(x['score']):raise ValueError('nonfinite candidate score')
        if rs!=sorted(rs,key=lambda x:(-x['score'],x['chunk_id'])):raise ValueError('score/tie order')
    old.assert_candidate_identity(result['results']['R3'],result['results']['R4'])
    if result['results']['R3']!=old.compare.attach_children(result['union'][:100],{x['chunk_id']:x for x in result['results']['R3']}):raise ValueError('R3 union mismatch')
    d=result['dense_audit']
    if d.get('truncated') or not d.get('actual_forward_inputs_verified') or d.get('query')!=q['query']:raise ValueError('dense forward input audit')
    if d.get('query_sha256')!=old.text_sha(q['query']) or d.get('token_count')!=len(d.get('token_ids',[])):raise ValueError('dense query/token identity')
    import numpy as np
    vector=np.asarray(result['vector'],dtype=np.float32)
    if vector.shape!=(1024,) or not np.isfinite(vector).all() or not np.isclose(np.linalg.norm(vector),1.,atol=1e-5):raise ValueError('dense query vector input')
    pairs=result['pair_audits']
    if len(pairs)!=len(result['results']['R3']):raise ValueError('actual R4 pair count')
    if any(not x.get('actual_forward_inputs_verified') or any(x.get(k) for k in ('query_truncated','child_truncated_initial','child_truncated_pair')) for x in pairs):raise ValueError('R4 forward truncation/input audit')
    if [p.get('chunk_id') for p in pairs]!=[c['chunk_id'] for c in result['results']['R3']]:raise ValueError('R4 pair IDs/order differ from R3')
    for pair,child in zip(pairs,result['results']['R3']):
        if (pair.get('r3_rank'),pair.get('query_text'),pair.get('query_sha256'),pair.get('child_text'),pair.get('child_text_sha256'))!=(child['rank'],q['query'],old.text_sha(q['query']),child['text'],child['text_sha256']):raise ValueError('R4 full query/child input identity')
        ids=pair.get('model_input_ids',[])
        if not ids or any(type(x) is not int or x<0 for x in ids) or pair.get('model_input_length')!=len(ids) or pair.get('model_input_ids_sha256')!=old.json_hash(ids):raise ValueError('R4 input token/hash/length mismatch')
        if result.get('backend')=='synthetic-stub' and ids!=list((q['query']+' '+child['text']).encode()):raise ValueError('stub forward tokens differ from complete query/child')


def execute(contract_path,release_path,output,backend_factory=None,retries=0,*,expected_release_sha256):
    if not isinstance(retries,int) or retries<0:raise ValueError('retries must be nonnegative integer')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    try:
        c=read(contract_path);queries,warmups=validate_contract(c)
        gate=verify_release(release_path,expected_release_sha256,contract_path,c)
    except Exception as exc:
        write(output/'prelaunch-rejection.json',dict(status='rejected_before_backend',error_type=type(exc).__name__,message=str(exc),quality_scores=None))
        raise
    write(output/'release-gate.json',gate)
    # This is the first backend/model access. Contract and gate consume query-only and runtime assets.
    old=algorithm()
    order=list(queries);random.Random(SEED).shuffle(order)
    manifest=dict(status='running',identity_kind='raw-run',run_id=output.name,split=c['split'],expected_count=len(queries),
                  policy=POLICY,contract_path=str(Path(contract_path).resolve()),contract_sha256=sha(contract_path),
                  release_path=str(Path(release_path).resolve()),release_sha256=expected_release_sha256,
                  gate_sha256=sha(output/'release-gate.json'),query_order=[q['intent_id'] for q in order],
                  queries_sha256=c['queries_sha256'],scoring_pass=1,execution_failures=[],attempt_failures=[],
                  completed_queries_by_pass={},quality_scores=None,warmup_queries=0,warmup_pairs=0,timed_queries=0,r4_pairs=0)
    journal=old.Journal(output)
    def checkpoint():old.save_json(output/'checkpoint.json',manifest)
    manifest['pending']={'phase':'loading_backend','pass_number':None,'intent_id':None}
    checkpoint()
    failure=False
    if backend_factory is None:
        if c['backend']=='synthetic-stub':
            from stub_backend import Backend
            backend_factory=Backend
        elif c['backend']=='actual':backend_factory=ActualBackend
        else:raise ValueError('unknown backend')
    try:backend=backend_factory(c)
    except Exception as exc:
        manifest['status']='failed';manifest['execution_failures'].append(dict(pass_number=None,error_type=type(exc).__name__,message=str(exc)))
        checkpoint();journal.close()
        write(output/'run_manifest.json',manifest)
        return manifest
    def call(q,p):
        for attempt in range(retries+1):
            manifest['pending']=dict(intent_id=q['intent_id'],pass_number=p,attempt=attempt+1,phase='retrieving')
            checkpoint()
            try:
                start=time.perf_counter();result=backend(q);validate_result(q,result,old)
                result['wall_seconds']=time.perf_counter()-start
                return result
            except BaseException as exc:
                record=dict(intent_id=q['intent_id'],pass_number=p,attempt=attempt+1,error_type=type(exc).__name__,message=str(exc))
                manifest['attempt_failures'].append(record)
                if not isinstance(exc,Exception):
                    manifest['status']='interrupted';manifest['execution_failures'].append(record)
                    checkpoint();journal.close();write(output/'run_manifest.json',manifest)
                    raise
                if attempt==retries:
                    manifest['execution_failures'].extend([x for x in manifest['attempt_failures'] if x['intent_id']==q['intent_id'] and x['pass_number']==p])
                    return None
    warm=[]
    for q in warmups:
        result=call(q,0)
        if result is None:failure=True;break
        warm.append(dict(intent_id=q['intent_id'],result=result));manifest['warmup_queries']+=1;manifest['warmup_pairs']+=len(result['pair_audits'])
        journal.append('completed-query-journal.jsonl',dict(intent_id=q['intent_id'],query=q['query'],pass_number=0,result=result));journal.flush()
        manifest['pending']=None;checkpoint()
    write_rows(output/'warmups.jsonl',warm)
    first={};first_vectors={}
    for p in (1,2,3):
        if failure:break
        directory=output/f'pass-{p}';directory.mkdir()
        rankings=[];audits=[];unions=[];vectors={};completed=0
        manifest['completed_queries_by_pass'][str(p)]=0
        for q in order:
            result=call(q,p)
            if result is None:failure=True;break
            for m in METHODS:
                row=old.result_row(q,m,p,result['results'][m]);rankings.append(row)
                if p==1:first[q['intent_id'],m]=row['results']
                elif not old.ranking_determinism(first[q['intent_id'],m],row['results'])['scores_exact']:
                    manifest['execution_failures'].append(dict(intent_id=q['intent_id'],pass_number=p,error_type='Nondeterminism'));failure=True
            vectors[q['intent_id']]=result['vector']
            if p==1:first_vectors[q['intent_id']]=result['vector']
            elif result['vector']!=first_vectors[q['intent_id']]:
                manifest['execution_failures'].append(dict(intent_id=q['intent_id'],pass_number=p,error_type='VectorNondeterminism'))
                failure=True;break
            audits.append(dict(intent_id=q['intent_id'],pass_number=p,query=q['query'],dense=result['dense_audit'],pairs=result['pair_audits'],timing=result['times'],wall_seconds=result['wall_seconds']))
            unions.append(dict(intent_id=q['intent_id'],pass_number=p,results=result['union']))
            completed+=1;manifest['timed_queries']+=1;manifest['r4_pairs']+=len(result['pair_audits'])
            journal.append('completed-query-journal.jsonl',dict(intent_id=q['intent_id'],query=q['query'],pass_number=p,result=result));journal.flush()
            manifest['completed_queries_by_pass'][str(p)]=completed;manifest['pending']=None;checkpoint()
        write_rows(directory/'rankings.jsonl',rankings);write_rows(directory/'audits.jsonl',audits);write_rows(directory/'rrf-union.jsonl',unions);write(directory/'query-vectors.json',vectors)
        manifest['completed_queries_by_pass'][str(p)]=completed
        if p==1:write_rows(output/'rankings.jsonl',rankings)
    manifest['status']='failed' if failure else 'retrieval_complete'
    if not failure:manifest['pending']=None
    journal.close();checkpoint()
    manifest['output_sha256']={p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file()}
    write(output/'run_manifest.json',manifest)
    seal=dict(identity_kind='raw-run',run_manifest_sha256=sha(output/'run_manifest.json'),rankings_sha256=sha(output/'rankings.jsonl') if (output/'rankings.jsonl').exists() else None,
              release_sha256=expected_release_sha256,scoring_pass=1)
    write(output/'ranking-seal.json',seal)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contract',type=Path,required=True);p.add_argument('--release',type=Path,required=True)
    p.add_argument('--release-sha256',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--retries',type=int,default=0)
    p.add_argument('--verify-release-only',action='store_true')
    a=p.parse_args()
    if a.verify_release_only:
        a.output.mkdir(parents=True,exist_ok=False);c=read(a.contract);validate_contract(c)
        result=verify_release(a.release,a.release_sha256,a.contract,c);write(a.output/'release-gate.json',result)
        print(json.dumps(result))
    else:
        result=execute(a.contract,a.release,a.output,retries=a.retries,expected_release_sha256=a.release_sha256)
        print(json.dumps({'status':result['status'],'timed_queries':result['timed_queries']}))
        if result['status']!='retrieval_complete':raise SystemExit(1)
