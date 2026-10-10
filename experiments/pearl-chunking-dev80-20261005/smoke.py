"""Stage-limited E0 CLI: public assets, full corpus calibration, one smoke index."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import random
import time
import traceback
from runtime import ROOT,EXP,sha,cache_identity,save_json,save_rows,load_queries,build_fts,build_dense,verify_index,legacy_runtime,model_assets,runtime_code

def counter():
    from ped_knowledge.tokenization import HuggingFaceTokenCounter
    return HuggingFaceTokenCounter.from_local_path(ROOT/'memPed/knowledge/models/bge-m3',expected_sha256='21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08')

def load(path):return json.loads(Path(path).read_text('utf8'))

def models():
    import numpy as np
    import torch
    if not torch.cuda.is_available():raise RuntimeError('real E0 requires CUDA')
    random.seed(20260929);np.random.seed(20260929);torch.manual_seed(20260929);torch.cuda.manual_seed_all(20260929)
    torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    model_assets()
    old=legacy_runtime();config=load(ROOT/'experiments/pearl-index-106-adobe-20260929/reranker-config.json')
    return old.Models({'dense':{'max_length':1024}},config)

def prepare(output):
    from table_snapshot import freeze_tables
    from parent_graph import build_parent_graph
    views=load(output/'source-views.json');c=counter()
    tables=freeze_tables(views,c);save_json(output/'table-snapshot.json',tables)
    graph={'parents':[],'source_view_sha256':sha(output/'source-views.json'),'max_tokens':1536}
    for v in views:
        graph['parents'].extend(build_parent_graph(v,c)['parents'])
    graph['graph_sha256']=cache_identity(graph)
    save_json(output/'public-parent-graph.json',graph);save_json(output/'source-views-prepared.json',views)
    print(json.dumps({'views':len(views),'tables':len(tables['tables']),'table_mapping_unresolved':sum(t['mapping_status']!='resolved' for t in tables['tables']),'parents':len(graph['parents'])}),flush=True)

def calibrate(output,attempt='r01'):
    import numpy as np
    from semantic_threshold import freeze_threshold
    old=legacy_runtime();m=models();views=load(output/'source-views-prepared.json')
    target=output/('calibration-'+attempt);target.mkdir(exist_ok=False)
    class AuditedSentenceModel:
        identity={'model':'BAAI/bge-m3','weight_sha256':model_assets()['memPed/knowledge/models/bge-m3/pytorch_model.bin'],
                  'semantic_max_length':2048,'retrieval_max_length':1024,'batch_size':8,'device':'cuda:0','seed':20260929}
        def encode(self,texts):
            vectors=[]
            with (target/'sentence-model-inputs.jsonl').open('x',encoding='utf8') as f:
                for start in range(0,len(texts),8):
                    batch=texts[start:start+8];tokens=m.dense.tokenizer(batch,add_special_tokens=True,truncation=False)['input_ids']
                    if any(len(t)>2048 for t in tokens):raise ValueError('semantic input exceeds frozen2048 limit')
                    with old.capture_forward_inputs(m.dense.model) as actual:
                        value=m.dense.encode(batch,batch_size=8,max_length=2048,return_dense=True,return_sparse=False,return_colbert_vecs=False)
                    m.sync();old.assert_actual_inputs(tokens,actual)
                    a=np.asarray(value['dense_vecs'],dtype=np.float32)
                    a/=np.linalg.norm(a,axis=1,keepdims=True)
                    old.build.validate_vectors(a,len(batch));vectors.append(a)
                    for i,t in enumerate(tokens):f.write(json.dumps({'sentence_index':start+i,'input_ids':t,'actual_forward_inputs_verified':True,'forward_sha256':cache_identity(actual),'truncated':False})+'\n')
                    if start%512==0:print(f'sentences {min(start+8,len(texts))}/{len(texts)}',flush=True)
            values=np.concatenate(vectors);np.save(target/'sentence-vectors.npy',values,allow_pickle=False)
            return values
    manifest=freeze_threshold(views,None,AuditedSentenceModel());save_json(target/'semantic-threshold.json',manifest)
    print(json.dumps({'threshold':manifest['threshold'],'pairs':len(manifest['distance_values']),'sentences':len(manifest['sentences']),'exclusions':manifest['excluded']}),flush=True)

def build(output):
    from chunkers import chunk
    from parent_graph import parents_for_spans
    views=load(output/'source-views-prepared.json');c=counter();graph=load(output/'public-parent-graph.json')
    # Predeclared before scores: C1 384 O0 M0. One smoke index, never an E1 grid.
    directory=output/'index-C1-L384-O0-M0';directory.mkdir(exist_ok=False)
    rows=[]
    for v in views:
        local_graph={'parents':[p for p in graph['parents'] if p['doc_id']==v['doc_id'] and p['source_version']==v['source_version']]}
        for ch in chunk(v,'C1',384,c):
            ch['parent_ids']=parents_for_spans(ch['core_spans'],local_graph)
            ch.update(text=ch['retrieval_text'],text_sha256=__import__('hashlib').sha256(ch['retrieval_text'].encode()).hexdigest(),source_id=v['doc_id'],resource_id=v['doc_id'],version_id=v['source_version'],title=v.get('title',''),heading_path=[],locator=json.dumps(ch['core_spans']),chunk_level='child')
            rows.append(ch)
    save_rows(directory/'child_chunks.jsonl',rows)
    identity={'policy':'C1-L384-O0-M0','source':sha(output/'source-views-prepared.json'),'table':sha(output/'table-snapshot.json'),'parent':sha(output/'public-parent-graph.json'),'tokenizer':c.fingerprint,'models':model_assets(),'code':runtime_code(),'retrieval':{'depth':100,'RRF_k':60,'dense':'exact_float32_dot','seed':20260929}}
    build_fts(directory/'fts.sqlite3',rows,identity);m=models();build_dense(m,rows,directory)
    manifest={'configuration':identity,'output_sha256':{p.name:sha(p) for p in directory.iterdir() if p.is_file()},'child_count':len(rows),'smoke_only':True,'dense':{'max_length':1024}}
    save_json(directory/'manifest.json',manifest);save_json(directory/'verification.json',verify_index(directory/'manifest.json'))
    print(json.dumps({'children':len(rows),'status':'built','configuration':'C1-L384-O0-M0'}),flush=True)

def retrieve(output):
    import numpy as np
    old=legacy_runtime();directory=output/'index-C1-L384-O0-M0';verify_index(directory/'manifest.json')
    manifest=load(directory/'manifest.json')
    if manifest['configuration']['models']!=model_assets():raise ValueError('index model identity drift')
    identity=manifest['configuration']
    current={'source':sha(output/'source-views-prepared.json'),'table':sha(output/'table-snapshot.json'),'parent':sha(output/'public-parent-graph.json'),'tokenizer':counter().fingerprint}
    if any(identity[k]!=v for k,v in current.items()):raise ValueError('index/source/table/parent/tokenizer drift')
    if any(sha(ROOT/name)!=h for name,h in identity['code'].items()):raise ValueError('index code identity drift')
    queries=load_queries(output/'queries.jsonl');children={r['chunk_id']:r for r in old.compare.read_jsonl(directory/'child_chunks.jsonl')};ids=load(directory/'dense_ids.json');vectors=np.load(directory/'dense_vectors.npy',allow_pickle=False);m=models()
    with (output/'rankings.jsonl').open('x',encoding='utf8') as ranks,(output/'retrieval-audits.jsonl').open('x',encoding='utf8') as audits:
        for q in queries:
            try:
                results,union,vector,dense_audit,r4_audits,times=old.retrieve(m,directory,vectors,ids,children,q['query'])
                record={'intent_id':q['intent_id'],'status':'success','results':results,'rrf_union':union,'times':times,'index_sha256':sha(directory/'manifest.json'),'query_sha256':cache_identity(q),'source_sha256':sha(output/'source-views-prepared.json'),'parent_sha256':sha(output/'public-parent-graph.json')}
                audit={'intent_id':q['intent_id'],'dense':dense_audit,'rerank':r4_audits,'times':times}
            except Exception as e:
                record={'intent_id':q['intent_id'],'status':'failed','error':repr(e)};audit={'intent_id':q['intent_id'],'status':'failed','traceback':traceback.format_exc()}
            ranks.write(json.dumps(record,ensure_ascii=False)+'\n');ranks.flush();audits.write(json.dumps(audit,ensure_ascii=False)+'\n');audits.flush()
            print(q['intent_id'],record['status'],flush=True)
    if any(r['status']!='success' for r in old.compare.read_jsonl(output/'rankings.jsonl')):raise RuntimeError('failed real retrieval units')

def contexts(output):
    from assemble import assemble
    verify_index(output/'index-C1-L384-O0-M0/manifest.json')
    views=load(output/'source-views-prepared.json');parents=load(output/'public-parent-graph.json');c=counter();old=legacy_runtime()
    records=[]
    queries={q['intent_id']:q for q in load_queries(output/'queries.jsonl')}
    for row in old.compare.read_jsonl(output/'rankings.jsonl'):
        if row['status']!='success':raise ValueError('failed rankings cannot assemble')
        bindings={'index_sha256':sha(output/'index-C1-L384-O0-M0/manifest.json'),'query_sha256':cache_identity(queries[row['intent_id']]),'source_sha256':sha(output/'source-views-prepared.json'),'parent_sha256':sha(output/'public-parent-graph.json')}
        if any(row.get(k)!=v for k,v in bindings.items()):raise ValueError('context ranking/input drift')
        for P in ('P0','P1','P2'):
            for B in (4096,8192):
                for panel in ('fixed_budget_main','seed10_diagnostic'):
                    record=assemble(row['results']['R4'],views,parents,P,B,panel,c);record['intent_id']=row['intent_id'];records.append(record)
        print('assembled',row['intent_id'],flush=True)
    save_rows(output/'contexts.jsonl',records);print('saved contexts',len(records),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage',choices=['prepare','calibrate','build','retrieve','contexts']);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--attempt-id',default='r01');args=parser.parse_args()
    if not args.output.is_dir():parser.error('output must be existing fresh Session2 run with frozen selection')
    for k in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE'):os.environ[k]='1'
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8';os.environ['ANONYMIZED_TELEMETRY']='False'
    if args.stage=='calibrate':calibrate(args.output.resolve(),args.attempt_id)
    else:globals()[args.stage](args.output.resolve())

if __name__=='__main__':main()
