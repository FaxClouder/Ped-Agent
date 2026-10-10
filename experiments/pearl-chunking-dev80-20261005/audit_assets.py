"""Saved public-source conservation and real semantic calibration audit."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from runtime import ROOT,sha,cache_identity,save_json
from source_view import digest,text_for_spans
from smoke import counter

def read(p):return json.loads(p.read_text('utf8'))
def rows(p):return [json.loads(l) for l in p.read_text('utf8').splitlines() if l.strip()]

def check_model_input(text,a,tokenizer,index):
    expected=tokenizer(text,add_special_tokens=True,truncation=False)['input_ids']
    if a['sentence_index']!=index or a['input_ids']!=expected or not a['actual_forward_inputs_verified'] or a['truncated']:raise ValueError('semantic actual model-tokenizer input mismatch')
    return True

def complete_partition(intervals,length):
    cursor=0
    for a,b in sorted(intervals):
        if a!=cursor or b<=a:raise ValueError('source gap/duplicate/reversed range')
        cursor=b
    if cursor!=length:raise ValueError('source tail not preserved')

def check_calibration_population(t,views,vectors):
    from semantic_threshold import extract_sentences
    sentences=t['sentences'];expected_sentences,expected_pairs,expected_excluded=extract_sentences(views)
    if sentences!=expected_sentences or [(p['left'],p['right']) for p in t['pairs']]!=[(sentences[a]['sentence_id'],sentences[b]['sentence_id']) for a,b in expected_pairs]:raise ValueError('semantic source sentence/eligible adjacent pair population drift')
    if t['excluded']!=expected_excluded:raise ValueError('semantic exclusion count drift')
    if t['sentence_sha256']!=digest(sentences) or t['view_sha256s']!=[v['view_sha256'] for v in views]:raise ValueError('semantic sentence/source hash drift')
    if t['distance_values']!=[p['distance'] for p in t['pairs']] or t['distances']!={p['right']:p['distance'] for p in t['pairs']}:raise ValueError('semantic distance representation drift')
    if t['manifest_sha256']!=digest({k:v for k,v in t.items() if k!='manifest_sha256'}):raise ValueError('semantic internal manifest drift')
    vector_hash=hashlib.sha256(str((np.dtype('float64').str,vectors.shape)).encode('ascii'))
    for start in range(0,len(vectors),128):vector_hash.update(np.asarray(vectors[start:start+128],dtype=np.float64).tobytes())
    if vector_hash.hexdigest()!=t['vectors_sha256']:raise ValueError('semantic vector dtype/shape/byte identity drift')
    return True

def run(output):
    views=read(output/'source-views-prepared.json');registry=read(ROOT/'experiments/pearl-chunking-dev80-20261005/source_registry.json');c=counter()
    vs={v['doc_id']:v for v in views}
    if set(vs)!={s['doc_id'] for s in registry['sources']}:raise ValueError('source membership changed')
    for source in registry['sources']:
        if sha(ROOT/source['canonical']['path'])!=source['canonical']['sha256']:raise ValueError('canonical byte drift')
        original=read(ROOT/source['canonical']['path']);v=vs[source['doc_id']]
        expected=[e for e in sorted(original['elements'],key=lambda e:e.get('order',0)) if e.get('text')]
        if [(e['element_id'],e['text']) for e in v['elements']]!=[(e['element_id'],e['text']) for e in expected]:raise ValueError('raw source view altered')
        if v['source_text']!='\n\n'.join(e['text'] for e in expected):raise ValueError('source separator mapping inconsistent')
    library=rows(output/'index-C1-L384-O0-M0/child_chunks.jsonl');coverage={}
    for ch in library:
        v=vs[ch['doc_id']]
        if text_for_spans(v,ch['core_spans'])!=ch['core_text'] or ch['source_text']!=ch['core_text']:raise ValueError('C1 source roundtrip mismatch')
        if c.count(ch['core_text'])>384:raise ValueError('core length exceeded')
        if ch['overlap_spans'] or ch['prefix_spans']:raise ValueError('smoke configuration drift')
        if hashlib.sha256(ch['text'].encode()).hexdigest()!=ch['text_sha256']:raise ValueError('retrieval text SHA mismatch')
        for s in ch['core_spans']:coverage.setdefault((s['doc_id'],s['element_id']),[]).append((s['start'],s['end']))
    for v in views:
        for e in v['elements']:complete_partition(coverage.get((v['doc_id'],e['element_id']),[]),len(e['text']))
    tables=read(output/'table-snapshot.json')
    if digest({k:v for k,v in tables.items() if k!='snapshot_sha256'})!=tables['snapshot_sha256']:raise ValueError('table snapshot internal hash drift')
    for table in tables['tables']:
        v=vs[table['doc_id']];e=next(e for e in v['elements'] if e['element_id']==table['element_id'])
        if table['mapping_status']!='resolved':raise ValueError('unresolved table cell coordinates')
        for cell in table['cells']:
            s=cell['span']
            if e['text'][s['start']:s['end']]!=cell['text']:raise ValueError('table cell roundtrip mismatch')
        complete_partition([(s['start'],s['end']) for unit in table['chunks'] for s in unit['core_spans']],len(e['text']))
    parents=read(output/'public-parent-graph.json')
    for parent in parents['parents']:
        if text_for_spans(vs[parent['doc_id']],parent['spans'])!=parent['source_text'] or c.count(parent['source_text'])>1536:raise ValueError('public parent source/length mismatch')
    cal=output/'calibration-r02';t=read(cal/'semantic-threshold.json');vectors=np.load(cal/'sentence-vectors.npy',mmap_mode='r',allow_pickle=False);sentences=t['sentences'];inputs=rows(cal/'sentence-model-inputs.jsonl')
    from transformers import AutoTokenizer
    from semantic_threshold import extract_sentences
    model_tokenizer=AutoTokenizer.from_pretrained(str(ROOT/'memPed/knowledge/models/bge-m3'),local_files_only=True)
    if vectors.shape!=(len(sentences),1024) or len(inputs)!=len(sentences):raise ValueError('real calibration cardinality mismatch')
    check_calibration_population(t,views,vectors)
    for index,(s,a) in enumerate(zip(sentences,inputs,strict=True)):
        check_model_input(s['text'],a,model_tokenizer,index)
        if text_for_spans(vs[s['span']['doc_id']],[s['span']])!=s['text']:raise ValueError('semantic sentence/source mismatch')
    lookup={s['sentence_id']:i for i,s in enumerate(sentences)};distances=[]
    for start in range(0,len(t['pairs']),128):
        batch=t['pairs'][start:start+128]
        a=np.asarray(vectors[[lookup[p['left']] for p in batch]],dtype=np.float64);b=np.asarray(vectors[[lookup[p['right']] for p in batch]],dtype=np.float64)
        if not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('nonfinite saved sentence vectors')
        denominator=np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)
        if (denominator<=0).any():raise ValueError('zero-norm sentence vector')
        actual=1-np.clip(np.sum(a*b,axis=1)/denominator,-1,1)
        if any(abs(value-p['distance'])>1e-10 for value,p in zip(actual,batch,strict=True)):raise ValueError('saved semantic pair distance mismatch')
        distances.extend(actual.tolist())
    value=float(np.quantile(distances,.9,method='linear'))
    if not np.isfinite(value) or abs(value-t['threshold'])>1e-10:raise ValueError('real semantic percentile mismatch')
    return {'status':'passed','sources':len(views),'source_elements':sum(len(v['elements']) for v in views),'smoke_C1_chunks':len(library),'tables':len(tables['tables']),'table_mapping_unresolved':0,'public_parents':len(parents['parents']),'semantic_sentences':len(sentences),'semantic_pairs':len(distances),'semantic_threshold_independently_recomputed':value,'model_tokenizer_class':type(model_tokenizer).__name__,'counting_tokenizer':c.fingerprint,'tokenizer_views':'BGE tokenizer.json counter for chunk/context budgets; pinned AutoTokenizer with config for actual forward inputs; both independently verified','input_sha256':{p.name:sha(p) for p in (output/'source-views-prepared.json',output/'table-snapshot.json',output/'public-parent-graph.json',cal/'semantic-threshold.json',cal/'sentence-vectors.npy',cal/'sentence-model-inputs.jsonl')}}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();result=run(a.output);save_json(a.receipt,result);print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
