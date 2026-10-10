"""Verify frozen dev inputs; sealed evaluation files are hashed only, never parsed."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import sqlite3
from collections import Counter
from datetime import datetime, timezone
import numpy as np
from protocol import validate_gold

ROOT=Path(__file__).resolve().parents[2]
INDEX=ROOT/'outputs/pearl-index-106-adobe-20260929-01'
DATA=ROOT/'outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01'
OLD=ROOT/'experiments/pearl-index-106-adobe-20260929'
GOLD=DATA/'pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json'
CORPUS=ROOT/'paper/pearl-framework/datasets/retrieval-corpus/corpus-manifest-v02.jsonl'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def rows(p):return [json.loads(l) for l in Path(p).read_text(encoding='utf8').splitlines()]
def write(p,v):
    with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n')
def check_hash(p,h):
    if sha(p)!=h:raise ValueError('hash mismatch: '+str(p))

def prepare(out):
    if out.exists():raise FileExistsError(out)
    check_hash(GOLD,'4b118700b2ec810dd57d342ab3d5447b7d313c11aea73535dff160bfaba2d56c')
    check_hash(DATA/'seal_manifest.json','c3524b0095e610e4ce325166f357903d3319da6dd0de23adc63277381d4a656b')
    seal=read(DATA/'seal_manifest.json')
    sealed={ROOT/p:h for p,h in seal['sealed_evaluation_provenance_sha256'].items()}
    sealed[DATA/seal['artifacts']['eval']['path']]=seal['artifacts']['eval']['sha256']
    sealed[DATA/'seal_manifest.json']=sha(DATA/'seal_manifest.json')
    for p,h in sealed.items():
        check_hash(p,h)
        if not p.stat().st_file_attributes & 1:raise ValueError('sealed file not readonly: '+str(p))
    m=read(INDEX/'build_manifest.json');v=read(INDEX/'verification.json')
    if v['status']!='passed' or v['build_manifest_sha256']!=sha(INDEX/'build_manifest.json'):raise ValueError('stale verification')
    index_hashes={}
    for name,h in m['output_sha256'].items():
        check_hash(INDEX/name,h);index_hashes[name]=h
    source_rows=rows(INDEX/'sources.jsonl');sources={s['source_id']:s for s in source_rows}
    if len(sources)!=106 or len(source_rows)!=106:raise ValueError('source count')
    for s in source_rows:
        if s['catalog_version']['parser_version']!='adobe-pdf-extract-v1':raise ValueError('wrong parser')
        check_hash(ROOT/s['source_path'],s['sha256']);check_hash(ROOT/s['document_path'],s['document_sha256'])
    g=read(GOLD)
    if g['corpus_manifest_sha256']!=sha(CORPUS) or g['corpus_version']!=m['corpus_version'] or g['frozen_child_library_sha256']!=sha(INDEX/'child_chunks.jsonl'):raise ValueError('Gold binding')
    for s in g['source_bindings']:
        if s['source_sha256']!=sources[s['source_id']]['sha256'] or s['adobe_document_sha256']!=sources[s['source_id']]['document_sha256']:raise ValueError('source binding')
    intents=g['intents'];strata=Counter(q['main_stratum'] for q in intents)
    if len(intents)!=80 or len({q['intent_id'] for q in intents})!=80 or sorted(strata.values())!=[20]*4:raise ValueError('dev quota')
    for q in intents:
        validate_gold(q)
        if any(a['source_id'] not in sources for a in q['atoms']):raise ValueError('unknown atom source')
    pilot=read(ROOT/'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json')
    if intents[:8]!=pilot['intents']:raise ValueError('pilot intents changed')
    children=rows(INDEX/'child_chunks.jsonl');ids=read(INDEX/'dense_ids.json')
    if len(children)!=6433 or len(set(ids))!=6433 or set(ids)!={c['chunk_id'] for c in children}:raise ValueError('child membership')
    for c in children:
        if hashlib.sha256(c['text'].encode()).hexdigest()!=c['text_sha256'] or c['chunk_level']!='child':raise ValueError('child text identity')
    vectors=np.load(INDEX/'dense_vectors.npy',allow_pickle=False)
    if vectors.shape!=(6433,1024) or not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors,axis=1),1,atol=1e-5):raise ValueError('dense shape or norm')
    sys.path.insert(0,str(OLD));import build
    build.verify_fts(INDEX/'fts.sqlite3',children)
    for name,h in m['dense']['actual_asset_sha256'].items():check_hash(ROOT/'memPed/knowledge/models/bge-m3'/name,h)
    rc=read(OLD/'reranker-config.json')
    for name,h in rc['verified_files_sha256'].items():check_hash(ROOT/rc['local_model_dir']/name,h)
    out.mkdir(parents=True,exist_ok=False)
    with (out/'queries.jsonl').open('x',encoding='utf8',newline='\n') as f:
        for q in intents:f.write(json.dumps({'intent_id':q['intent_id'],'query':q['query']},ensure_ascii=False,sort_keys=True)+'\n')
    p={'status':'passed','run_id':out.name,'created_at_utc':datetime.now(timezone.utc).isoformat(),
       'index_dir':str(INDEX),'gold_path':str(GOLD),'gold_sha256':sha(GOLD),'queries_sha256':sha(out/'queries.jsonl'),
       'corpus_manifest_sha256':sha(CORPUS),'index_build_manifest_sha256':sha(INDEX/'build_manifest.json'),
       'frozen_child_sha256':sha(INDEX/'child_chunks.jsonl'),'reranker_config_sha256':sha(OLD/'reranker-config.json'),
       'index_artifact_sha256':index_hashes,'source_count':106,'child_count':6433,'strata':dict(strata),'intent_count':80,
       'sealed_check_count':len(sealed),'sealed_hash_and_readonly_check':'passed; byte hashing only, no evaluation JSON or workpack parsed',
       'seal_manifest_sha256':sha(DATA/'seal_manifest.json'),'sealed_files_sha256':{str(p.relative_to(ROOT)):h for p,h in sealed.items()},
       'fts_content_and_ids':'6433 exact normalized bodies; title/heading empty',
       'dense_id_alignment':'ordered IDs bound to original vectors by both artifact hashes; finite unit norms',
       'models':'all pinned assets independently hashed','seed':20260929,'code_sha256':sha(Path(__file__))}
    write(out/'preflight.json',p)
    print(json.dumps({k:p[k] for k in ('status','run_id','intent_count','strata','sealed_check_count')}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True)
    prepare(parser.parse_args().output_dir.resolve())
