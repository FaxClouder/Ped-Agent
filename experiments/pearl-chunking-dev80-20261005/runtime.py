"""Local query-only E0 runtime. Reuses frozen numerical retrieval implementation."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
EXP=Path(__file__).parent

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def cache_identity(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def save_json(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')

def save_rows(path,rows):
    with Path(path).open('x',encoding='utf8',newline='\n') as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')

def load_queries(path,expected_count=8):
    rows=[json.loads(l) for l in Path(path).read_text('utf8').splitlines() if l.strip()]
    if len(rows)!=expected_count or len({r.get('intent_id') for r in rows})!=expected_count:
        raise ValueError('query count/identity mismatch')
    if any(set(r)!={'intent_id','query'} or any(not isinstance(v,str) or not v.strip() for v in r.values()) for r in rows):
        raise ValueError('runtime requires strict query-only records')
    return rows

def build_fts(path,children,identity):
    from ped_knowledge.indexing import FTSIndex
    from ped_knowledge.tokenization import EnglishLexicalAnalyzer
    if Path(path).exists():raise FileExistsError(path)
    FTSIndex(Path(path),analyzer=EnglishLexicalAnalyzer()).rebuild(
        [dict(r,title='',heading_path=[]) for r in children],source_fingerprint=cache_identity(identity),
        policy_version=identity.get('policy','experimental'),tokenizer_fingerprint=identity.get('tokenizer',''),
        code_revision=cache_identity({'runtime':sha(__file__)}))

def verify_index(manifest_path):
    p=Path(manifest_path);m=json.loads(p.read_text('utf8'))
    for name,h in m['output_sha256'].items():
        if sha(p.parent/name)!=h:raise ValueError('index drift: '+name)
    return {'status':'passed','files':len(m['output_sha256'])}

_MODEL_ASSET_CACHE=None

def model_assets():
    """Hash gate actual model and configuration files against Session1 freeze."""
    import yaml
    frozen=yaml.safe_load((EXP/'resolved_manifest.yaml').read_text('utf8'))
    global _MODEL_ASSET_CACHE
    records=frozen['retrieval']['model_asset_checks']
    signatures={r['path']:(ROOT/r['path']).stat() for r in records}
    expected={r['path']:r['sha256'] for r in records}
    signatures={p:(s.st_size,s.st_mtime_ns,expected[p]) for p,s in signatures.items()}
    if list((ROOT/'memPed/knowledge/models/bge-m3').glob('*.safetensors')):
        raise ValueError('competing unverified dense weight format')
    if _MODEL_ASSET_CACHE and _MODEL_ASSET_CACHE[0]==signatures:
        return dict(_MODEL_ASSET_CACHE[1])
    result={}
    for row in records:
        actual=sha(ROOT/row['path'])
        if actual!=row['sha256']:raise ValueError('model/config drift: '+row['path'])
        result[row['path']]=actual
    config=ROOT/'experiments/pearl-index-106-adobe-20260929/reranker-config.json'
    result[str(config.relative_to(ROOT))]=sha(config)
    if list((ROOT/'memPed/knowledge/models/bge-m3').glob('*.safetensors')):
        raise ValueError('competing unverified dense weight format')
    _MODEL_ASSET_CACHE=(signatures,dict(result))
    return result

def runtime_code():
    names=('runtime.py','smoke.py','source_view.py','table_snapshot.py','parent_graph.py','chunkers.py','semantic_threshold.py','assemble.py')
    paths=[EXP/name for name in names]
    paths.extend((ROOT/'Knowledge-Base/src/ped_knowledge').rglob('*.py'))
    paths.extend((ROOT/'Contracts/src/ped_contracts').rglob('*.py'))
    paths.extend(ROOT/'experiments/pearl-index-106-adobe-20260929'/name for name in ('build.py','compare_pilot.py','rerank_pilot.py'))
    paths.append(ROOT/'experiments/pearl-retrieval-dev80-20261003/run.py')
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))}

def legacy_runtime():
    pilot=ROOT/'experiments/pearl-index-106-adobe-20260929'
    sys.path.insert(0,str(pilot))
    # Loaded once under a distinct module name; do not mutate legacy globals.
    name='pearl_chunking_legacy_runtime'
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,ROOT/'experiments/pearl-retrieval-dev80-20261003/run.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod

def build_dense(models,children,output):
    """Real CUDA encoding with full audited inputs; never truncates."""
    import numpy as np
    old=legacy_runtime();arrays=[];audits=[]
    for start in range(0,len(children),8):
        batch=children[start:start+8];texts=[r['text'] for r in batch]
        inputs=models.dense.tokenizer(texts,add_special_tokens=True,truncation=False,padding=False)
        if any(len(x)>1024 for x in inputs['input_ids']):raise ValueError('dense passage input would truncate')
        with old.capture_forward_inputs(models.dense.model) as actual:
            encoded=models.dense.encode(texts,batch_size=8,max_length=1024,return_dense=True,return_sparse=False,return_colbert_vecs=False)
        models.sync();old.assert_actual_inputs(inputs['input_ids'],actual)
        vectors=np.asarray(encoded['dense_vecs'],dtype=np.float32)
        vectors/=np.linalg.norm(vectors,axis=1,keepdims=True)
        old.build.validate_vectors(vectors,len(batch));arrays.append(vectors)
        audits.extend(dict(chunk_id=r['chunk_id'],token_ids=t,raw_tokens=len(t),actual_forward_inputs_verified=True,
            forward_tokens_sha256=cache_identity(actual),truncated=False) for r,t in zip(batch,inputs['input_ids'],strict=True))
        if start%128==0:print(f'dense {min(start+8,len(children))}/{len(children)}',flush=True)
    vectors=np.concatenate(arrays);np.save(output/'dense_vectors.npy',vectors,allow_pickle=False)
    save_json(output/'dense_ids.json',[r['chunk_id'] for r in children]);save_rows(output/'model_inputs.jsonl',audits)
    return vectors
