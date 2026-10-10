"""Independent 80/200 fixture authoring and deterministic stub models, never real eval data."""
from pathlib import Path
import argparse
import importlib.metadata
import json
import sys
import subprocess

import numpy as np

from runtime import ROOT, OLD, POLICY, STRATA, algorithm, read, rows, sha, write, write_rows, execute, dependency_files


from stub_backend import Backend


def prepare(output,n,child_count=24):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);index=output/'index';index.mkdir()
    split={80:'development_80',200:'evaluation_200'}[n];prefix={80:'syn-dev',200:'syn-eval'}[n]
    sources=[]
    for group in range(4):
        source=output/f'source-{group}.txt';source.write_text(f'Independent synthetic source {group}. Beacon condition and numeric fact.\n',encoding='utf8');sources.append(source)
    children=[]
    for i in range(1,child_count+1):
        text=f'Beacon independent synthetic fact {i}. Condition held.'
        children.append(dict(chunk_id=f'syn-child-{i:03d}',text=text,text_sha256=algorithm().text_sha(text),
            source_id=f'synthetic-source-{(i-1)//6%4}',source_sha256=sha(sources[(i-1)//6%4]),title='Synthetic source',page_start=1,page_end=1,locator='synthetic:page1',
            resource_id=f'synthetic-source-{(i-1)//6%4}',version_id='synthetic-v1',chunk_level='child',heading_path=[]))
    write_rows(index/'child_chunks.jsonl',children)
    old=algorithm();old.build.build_fts(index/'fts.sqlite3',children,sha(index/'child_chunks.jsonl'),'synthetic-v1')
    ids=[c['chunk_id'] for c in children];write(index/'dense_ids.json',ids)
    vectors=np.zeros((child_count,1024),dtype=np.float32);vectors[:,0]=np.sqrt(.91)
    for i in range(child_count):vectors[i,i+1]=.3
    np.save(index/'dense_vectors.npy',vectors,allow_pickle=False)
    write(index/'build_manifest.json',dict(synthetic=True,seed=20260929,model_revision='synthetic-stub-v1',output_sha256={p.name:sha(p) for p in index.iterdir() if p.is_file()}))
    write(index/'verification.json',dict(status='passed',build_manifest_sha256=sha(index/'build_manifest.json')))
    queries=[dict(intent_id=f'{prefix}-{i:03d}',query=f'Beacon synthetic independent query {i}?') for i in range(1,n+1)]
    write_rows(output/'queries.jsonl',queries)
    warmups=[dict(intent_id=f'syn-dev-warmup-{i}',query=f'Beacon independent development warmup {i}?') for i in range(5)]
    write_rows(output/'warmup-queries.jsonl',warmups)
    intents=[]
    for i,q in enumerate(queries):
        stratum=STRATA[i//(n//4)];base=(1+6*(i%4)) if child_count>=24 else 1
        second=(base+6 if i%4%2==0 else base-6) if stratum=='cross_paper' and child_count>=24 else base+1
        ids=[base] if stratum=='single_source' else [base,second]
        atoms=[dict(atom_id=f'a{x:03d}',source_id=children[x-1]['source_id'] if x<=child_count else 'synthetic-source-0',page=1) for x in ids]
        if stratum=='numeric_table':atoms[0]['atom_id']+='_joint'
        requirements=[dict(requirement_id='r1',support_bundles=[[atoms[0]['atom_id']]])]
        if len(atoms)>1:requirements.append(dict(requirement_id='r2',support_bundles=[[atoms[1]['atom_id']]]))
        if i%7==0 and len(atoms)>1:requirements[0]['support_bundles'].append([atoms[1]['atom_id']])
        intents.append(dict(**q,split='dev_candidate' if n==80 else 'eval_candidate',main_stratum=STRATA[i//(n//4)],reference_answer='Independent synthetic fixture answer.',
                            atoms=atoms,requirements=requirements,
                            evidence_groups=[dict(group_id='g',requirements=[r['requirement_id'] for r in requirements])]))
    write(output/'gold.json',dict(synthetic=True,dataset_id=f'independent-synthetic-{n}',split='development' if n==80 else 'sealed_independent_evaluation',
         intents=intents,frozen_child_library_sha256=sha(index/'child_chunks.jsonl')))
    write(output/'method.json',POLICY);write(output/'protocol.json',POLICY);write(output/'statistics.json',dict(comparisons=POLICY['comparisons'],bootstrap_repeats=10000,seed=20260929))
    write(output/'model-config.json',dict(revision='synthetic-stub-v1',forward='explicit stub token bytes; no GPU/model inference'))
    dependencies={'numpy':importlib.metadata.version('numpy')}
    write(output/'dependencies.json',dependencies)
    contract=dict(identity_kind='raw-run',synthetic=True,split=split,expected_count=n,stratum_quotas={h:n//4 for h in STRATA},
                  queries_path=str((output/'queries.jsonl').resolve()),queries_sha256=sha(output/'queries.jsonl'),intent_ids=[q['intent_id'] for q in queries],
                  warmup_queries_path=str((output/'warmup-queries.jsonl').resolve()),warmup_queries_sha256=sha(output/'warmup-queries.jsonl'),warmup_development_ids=[q['intent_id'] for q in warmups],
                  policy=POLICY,backend='synthetic-stub',model_revisions={'dense':'synthetic-stub-v1','reranker':'synthetic-stub-v1'},
                  custody_binding={'gold_sha256':sha(output/'gold.json'),'child_sha256':sha(index/'child_chunks.jsonl')},
                  index_dir=str(index.resolve()),index_manifest=str((index/'build_manifest.json').resolve()),model_config=str((output/'model-config.json').resolve()))
    categories={
        'protocol':[output/'protocol.json',ROOT/'paper/pearl-framework/layer-1-retrieval/experiments.md',ROOT/'paper/pearl-framework/layer-1-retrieval/metrics.md'],
        'statistics':[output/'statistics.json',OLD/'analyze.py'],
        'method':[output/'method.json'],'model':[output/'model-config.json'],'index':[p for p in index.iterdir() if p.name!='child_chunks.jsonl'],
        'child':[index/'child_chunks.jsonl'],'source':sources,
        'view':[output/'queries.jsonl',output/'warmup-queries.jsonl'],
        'dependencies':[output/'dependencies.json']+dependency_files(dependencies),
        'code':list(Path(__file__).parent.glob('*.py'))+list(OLD.glob('*.py'))+list((ROOT/'experiments/pearl-index-106-adobe-20260929').glob('*.py'))+list((ROOT/'Knowledge-Base/src/ped_knowledge').rglob('*.py'))+list((ROOT/'Contracts/src/ped_contracts').rglob('*.py'))}
    contract['runtime_files']=[str(p.resolve()) for ps in categories.values() for p in ps]
    write(output/'contract.json',contract)
    release=dict(status='frozen',synthetic=True,split=split,backend=contract['backend'],model_revisions=contract['model_revisions'],
                 policy=POLICY,contract_sha256=sha(output/'contract.json'),dependencies=dependencies,
                 files=[dict(category=category,path=str(p.resolve()),sha256=sha(p)) for category,ps in categories.items() for p in ps])
    write(output/'release.json',release)
    write(output/'release-pin.json',dict(release_sha256=sha(output/'release.json'),purpose='External selected manifest identity; pass this pin explicitly at launch'))
    return {key:output/name for key,name in [('contract','contract.json'),('gold','gold.json'),('release','release.json')]}


def reviews(run,gold,expected_count):
    import custody
    inputs=custody.packets(run,gold,expected_count);selected=[]
    for i in inputs['q_by']:
        packet_path=run/'review/packets'/(i+'.json');packet=read(packet_path)
        reviewed=[c['chunk_id'] for c in packet['candidates']];unresolved=[c['chunk_id'] for c in packet['supplementary_candidates']]
        paths={};evidence=[]
        for atom in inputs['q_by'][i]['atoms']:
            aid=atom['atom_id'];number=int(aid[1:4]);ids=[f'syn-child-{number:03d}']
            if aid.endswith('_joint'):ids.append(f'syn-child-{number+1:03d}')
            paths[aid]=[ids] if set(ids)<=set(reviewed) else []
            if paths[aid]:evidence.append(dict(atom_id=aid,chunk_ids=ids,reason='Synthetic fixed reference.',excerpts=[dict(chunk_id=cid,text=inputs['children'][cid]['text']) for cid in ids]))
        decision=dict(intent_id=i,review_type='subagent_blind_content',reviewer_id='synthetic-fixture-oracle-not-semantic-agent',packet_sha256=sha(packet_path),
            reviewed_ids=reviewed,unresolved_ids=unresolved,atom_paths=paths,path_evidence=evidence,
            rejection_summary='Synthetic fixture decision; no empirical semantic judgement.',notes='Unreviewed deeper candidates remain unknown.')
        path=run/'review/decisions'/(i+'.json');write(path,decision);selected.append(dict(intent_id=i,path=str(path.resolve()),sha256=sha(path)))
    selection=run/'selected-review-manifest.json';write(selection,dict(identity_kind='raw-run-review-selection',run_manifest_sha256=sha(run/'run_manifest.json'),files=selected))
    custody.combine(run,gold,selection,run/'support-map.json',expected_count)
    return custody.score_and_verify(run,gold,run/'support-map.json',expected_count)


def deliver(output,counts=(80,200),launch_subprocess=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);result=dict(status='synthetic_verified',real_evaluation_runs=0,batches={})
    for n in counts:
        batch=output/f'batch-{n}';batch.mkdir();assets=prepare(batch/'inputs',n)
        if launch_subprocess:
            command=[sys.executable,str(Path(__file__).with_name('runtime.py')),'--contract',str(assets['contract']),'--release',str(assets['release']),
                     '--release-sha256',sha(assets['release']),'--output',str(batch/'run')]
            completed=subprocess.run(command,capture_output=True,text=True,check=True)
            write(batch/'runtime-subprocess.json',dict(command=command,stdout=completed.stdout,stderr=completed.stderr,access='query-only/runtime assets; no Gold path or custody import supplied'))
            manifest=read(batch/'run/run_manifest.json')
        else:manifest=execute(assets['contract'],assets['release'],batch/'run',Backend,expected_release_sha256=sha(assets['release']))
        oracle=reviews(batch/'run',assets['gold'],n)
        result['batches'][str(n)]={key:manifest[key] for key in ('split','timed_queries','r4_pairs','warmup_queries','warmup_pairs')}
        result['batches'][str(n)].update(first_pass_cells=n*4,oracle=oracle)
    # Fixed failed execution and successful retry references are delivery artifacts, never quality zero.
    failure_dir=output/'failure-reference';failure_dir.mkdir();assets=prepare(failure_dir/'inputs',80)
    class Fails:
        def __init__(self,c):pass
        def __call__(self,q):raise RuntimeError('synthetic fixed execution failure')
    failed=execute(assets['contract'],assets['release'],failure_dir/'run',Fails,retries=1,expected_release_sha256=sha(assets['release']))
    result['failure_reference']=dict(status=failed['status'],attempts=len(failed['attempt_failures']),quality_scores=None)
    class Retry(Backend):
        failed=False
        def __call__(self,q):
            if not self.failed:self.failed=True;raise RuntimeError('synthetic single transient failure')
            return super().__call__(q)
    retried=execute(assets['contract'],assets['release'],failure_dir/'retry-run',Retry,retries=1,expected_release_sha256=sha(assets['release']))
    result['retry_reference']=dict(status=retried['status'],attempt_failures=len(retried['attempt_failures']),terminal_failures=len(retried['execution_failures']))
    write(output/'synthetic-summary.json',result)
    write(output/'synthetic-input-delivery-manifest.json',dict(synthetic=True,files={p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file()}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--prepare-only',action='store_true');p.add_argument('--count',type=int,choices=(80,200),default=200);a=p.parse_args()
    if a.prepare_only:print(json.dumps({k:str(v) for k,v in prepare(a.output,a.count).items()},sort_keys=True))
    else:print(json.dumps(deliver(a.output,launch_subprocess=True),sort_keys=True))
