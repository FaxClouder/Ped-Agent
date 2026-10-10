"""Session 5 E2 only: core-preserving 0/10/20% overlap for frozen C2-L384/C3-L256.

O0 is the strictly equivalent E1 index/ranking (reused); O10/O20 get independent
real indexes and real 80-intent retrieval through the unchanged E1 functions.
Contexts use the E3-frozen common recovery P0 (alias of the recovery arm).
No E4 prefix, no final rerun, no generation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import shutil
import statistics
import time
from pathlib import Path
import e1
from runtime import ROOT, EXP, sha, save_json, load_queries, runtime_code

E0=ROOT/'outputs/pearl-chunking-dev80-20261005-03'
E1=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
BASES={'C2-L384-O0-M0':('C2',384),'C3-L256-O0-M0':('C3',256)}
RATIOS={'O10':0.1,'O20':0.2}
CONFIGS={f'{b[:-6]}-{o}-M0':(b,r) for b in BASES for o,r in RATIOS.items()}
PANELS=('fixed_budget_main','seed10_diagnostic')
BUDGETS=(4096,8192)
STRATEGY='P0'

def load(p):return json.loads(Path(p).read_text('utf8'))
def jsonl(p):
    with Path(p).open(encoding='utf8') as f:return [json.loads(l) for l in f if l.strip()]

_original_configurations=e1.configurations
_original_make_children=e1.make_children
_original_identity=e1.identity

def configurations():
    out=dict(_original_configurations())
    for config,(base,_) in CONFIGS.items():out[config]=BASES[base]
    return out

def base_children(base):
    return jsonl(E1/('index-'+base)/'child_chunks.jsonl')

def _counts(c,texts):
    """Exactly counter.count for each text, via the same tokenizer's batch encoder."""
    if not texts:return []
    return [len(e.ids) for e in c._tokenizer.encode_batch(texts)]

_SPLIT=frozenset(' \n\t\r')
PRUNE_STATS={'candidates':0,'exactly_counted':0}

def _word_starts(text):
    """Starts of ASCII-whitespace-delimited words that contain an ASCII letter/digit.

    BGE-M3 normalizes these separators to a space and Metaspace splits on it; an
    ASCII alphanumeric survives normalization, so each such word fully inside a
    suffix is a separate non-empty pre-token and yields at least one token.
    """
    out=[];i=0;n=len(text)
    while i<n:
        if text[i] in _SPLIT:i+=1;continue
        j=i;alnum=False
        while j<n and text[j] not in _SPLIT:
            ch=text[j]
            if ch.isascii() and ch.isalnum():alnum=True
            j+=1
        if alnum:out.append(i)
        i=j
    return out

def _fitting(counter,text,starts,limit):
    """Starts a with counter.count(text[a:])<=limit, exactly as the original filter.

    Lower bound count(text[a:]) >= count('') + #words starting at >= a is
    non-increasing in a, so scanning from the end we stop once it exceeds limit;
    every skipped start provably fails the original test. Survivors are counted exactly.
    """
    import bisect
    words=_word_starts(text);base=counter.count('');keep=[]
    for a in sorted(starts,reverse=True):
        if base+len(words)-bisect.bisect_left(words,a)>limit:break
        keep.append(a)
    PRUNE_STATS['candidates']+=len(starts);PRUNE_STATS['exactly_counted']+=len(keep)
    return [a for a,n in zip(keep,_counts(counter,[text[a:] for a in keep])) if n<=limit]

def attach_overlap_batched(core,r,L,view,counter):
    """chunkers.attach_overlap with identical selection; suffix counts batched and pruned.

    Same elements/text/sentence starts; valid = sentence starts whose suffix count
    <= floor(rL), min chosen; token-offset fallback identical. Starts that a sound
    word-count lower bound excludes are never tokenized (see _fitting). Sampled rows
    are rechecked against the original function in overlap_children.
    """
    from copy import deepcopy
    from chunkers import sentence_spans,interval_spans
    from source_view import text_for_spans,text_hash,digest
    result=deepcopy(core);limit=math.floor(r*L)
    if not 0<=r<1:raise ValueError('invalid overlap ratio')
    if limit<=counter.count('') or core['is_table']:return result
    first=core['core_spans'][0];lookup={e['element_id']:e for e in view['elements']}
    run=next(run for run in view['barrier_runs'] if first['element_id'] in run)
    elements=[]
    for eid in run:
        e=lookup[eid]
        if core['policy']['C']=='C3' and e['heading_path']!=lookup[first['element_id']]['heading_path']:
            elements=[];continue
        if eid==first['element_id']:
            e=dict(e,text=e['text'][:first['start']]);elements.append(e);break
        elements.append(e)
    text='\n\n'.join(e['text'] for e in elements)
    starts=[a for a,b in sentence_spans(text)]
    valid=_fitting(counter,text,starts,limit)
    if valid:start=min(valid)
    else:
        _,offsets=counter.encode_with_offsets(text)
        cand=[a for a,b in offsets if b>a]
        valid=_fitting(counter,text,cand,limit)
        if not valid:return result
        start=min(valid)
    result['overlap_spans']=interval_spans(elements,start,len(text))
    result['source_text']=text_for_spans(view,result['overlap_spans']+result['core_spans'])
    result['retrieval_text']=result['source_text'];result['text_sha256']=text_hash(result['source_text'])
    result['config_id']=digest({'base':core['config_id'],'O':r})
    result['chunk_id']='chunk-'+digest({'base':core['chunk_id'],'O':r})[:24]
    return result

SAMPLE_EVERY=40
OVERLAP_EQUIVALENCE={}

def overlap_children(e0,config,c):
    """Recompute E1 core children, prove byte-equality to E1, then attach overlap."""
    from chunkers import attach_overlap
    base,r=CONFIGS[config];C,L=BASES[base]
    views,core=_original_make_children(e0,base,c)
    frozen=base_children(base)
    if len(core)!=len(frozen) or any(json.dumps(a,sort_keys=True,ensure_ascii=False)!=json.dumps(b,sort_keys=True,ensure_ascii=False) for a,b in zip(core,frozen)):
        raise ValueError('E2 core children differ from frozen E1 '+base)
    vs={v['doc_id']:v for v in views};rows=[];checked=0
    for i,ch in enumerate(core):
        o=attach_overlap_batched(ch,r,L,vs[ch['doc_id']],c)
        if i%SAMPLE_EVERY==0:
            if o!=attach_overlap(ch,r,L,vs[ch['doc_id']],c):raise ValueError('batched overlap differs from chunkers.attach_overlap')
            checked+=1
        if o['core_spans']!=ch['core_spans'] or o['core_sha256']!=ch['core_sha256'] or o['core_text']!=ch['core_text'] or o['parent_ids']!=ch['parent_ids']:
            raise ValueError('core changed by overlap')
        o['policy']=dict(ch['policy'],O=r,overlap_limit_tokens=math.floor(r*L))
        o.update(text=o['retrieval_text'],text_sha256=hashlib.sha256(o['retrieval_text'].encode()).hexdigest(),base_chunk_id=ch['chunk_id'],overlap_ratio=r)
        rows.append(o)
    if len({x['chunk_id'] for x in rows})!=len(rows):raise ValueError('duplicate overlap children')
    OVERLAP_EQUIVALENCE[config]=dict(rows=len(rows),original_function_rechecks=checked,sample_every=SAMPLE_EVERY,core_children_equal_E1=True,pruning=dict(PRUNE_STATS,rule='word-count lower bound, see e2._fitting'))
    PRUNE_STATS.update(candidates=0,exactly_counted=0)
    return views,rows

def make_children(e0,config,c):
    if config in CONFIGS:return overlap_children(e0,config,c)
    return _original_make_children(e0,config,c)

def identity(e0,config,c):
    value=_original_identity(e0,config,c)
    if config in CONFIGS:
        base,r=CONFIGS[config]
        value['code']['experiments/pearl-chunking-dev80-20261005/e2.py']=sha(__file__)
        value['E2']=dict(base_configuration=base,overlap_ratio=r,overlap_limit_tokens=math.floor(r*BASES[base][1]),base_index_manifest_sha256=sha(E1/('index-'+base)/'manifest.json'),base_child_chunks_sha256=sha(E1/('index-'+base)/'child_chunks.jsonl'),M='M0',recovery='P0')
    return value

def patch():
    e1.configurations=configurations;e1.make_children=make_children;e1.identity=identity

INPUTS=[E0/'delivery-manifest.json',E1/'delivery-manifest.json',E3/'delivery-manifest.json',E3/'recovery-selection-e3-r10.json',E3/'common-support-map-e3-r10.json',E1/'queries.jsonl']

def verify_e0():return verify_run(E0)

def verify_run(run):
    """Frozen outputs must not drift; later maintained code/navigation drift is recorded."""
    m=load(run/'delivery-manifest.json');out_drift=[];other=[]
    for name,h in m['artifacts_sha256'].items():
        p=ROOT/name;actual=sha(p) if p.is_file() else None
        if actual!=h:(out_drift if name.startswith('outputs/') else other).append(dict(path=name,expected=h,actual=actual))
    if out_drift:raise ValueError(run.name+' frozen output drift '+repr(out_drift[:3]))
    return dict(status='passed',checked=len(m['artifacts_sha256']),output_drift=[],maintained_code_or_navigation_drift=other)

def prepare(out):
    """Light-weight, model-free: input bindings, query copy, O0 strict-equivalence proof."""
    e0check=verify_e0()
    runs={run.name:verify_run(run) for run in (E1,E3)}
    if runs[E3.name]['maintained_code_or_navigation_drift']:raise ValueError('E3 code drift')
    sel=load(E3/'recovery-selection-e3-r10.json')
    if sel['status']!='frozen' or sel['selected']!='P0':raise ValueError('E3 recovery not frozen P0')
    cand=load(ROOT/'outputs/pearl-chunking-dev80-20261005-07/candidate-selection-e1-r07.json')
    if cand['status']!='frozen' or cand['selected']!=list(BASES):raise ValueError('E1 candidate drift')
    shutil.copyfile(E1/'queries.jsonl',out/'queries.jsonl');load_queries(out/'queries.jsonl',80)
    o0={}
    for base in BASES:
        d=E1/('index-'+base);ranks=sha(d/'rankings.jsonl')
        if ranks!=load(E3/'stage-boundary-e3-r01.json')['frozen_ranking_sha256'][base]:raise ValueError('O0 ranking drift')
        ctx={}
        for B in BUDGETS:
            for panel in PANELS:
                p=E3/f'contexts-{base}-P0-{B}-{panel}.jsonl';ctx[p.name]=sha(p)
                if any(r['ranking_file_sha256']!=ranks for r in jsonl(p)):raise ValueError('E3 P0 context/ranking binding drift')
        o0[base]=dict(index_manifest_sha256=sha(d/'manifest.json'),child_chunks_sha256=sha(d/'child_chunks.jsonl'),rankings_sha256=ranks,e3_p0_contexts_sha256=ctx,alias=base.replace('-O0-','-O0-')+' = O0 arm of E2; P0 = frozen recovery arm',reuse='exact: same core children (O=0 attaches no text), same index, same R4 ranking, same P0 assembler and panels')
    save_json(out/'e2-inputs-r01.json',dict(e0_check=e0check,run_checks=runs,inputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in INPUTS},queries_copy_sha256=sha(out/'queries.jsonl'),selection_rule_sha256=sha(out/'e2-overlap-selection-rule-r01.md'),o0_reuse=o0,configs={k:dict(base=v[0],overlap_ratio=v[1]) for k,v in CONFIGS.items()},strategy='P0',budgets=BUDGETS,panels=PANELS,generation_calls=0))
    print('prepared',flush=True)

def overlap_profile(directory,config,c):
    base,r=CONFIGS[config];rows=jsonl(directory/'child_chunks.jsonl');limit=math.floor(r*BASES[base][1])
    from source_view import text_for_spans
    tok=[];core=[];attached=0;body=0
    for x in rows:
        if x['is_table']:continue
        body+=1
        n=0
        if x['overlap_spans']:
            attached+=1;n=c.count(x['source_text'][:len(x['source_text'])-len(x['core_text'])].rstrip('\n'))-c.count('')
        tok.append(n);core.append(c.count(x['core_text'])-c.count(''))
    return dict(configuration_id=config,base=base,overlap_ratio=r,limit_tokens_including_specials=limit,children=len(rows),body_children=body,attached_children=attached,attached_share=attached/body,overlap_content_tokens_mean=statistics.mean(tok),overlap_content_tokens_mean_attached=statistics.mean([t for t in tok if t]) if attached else 0,effective_ratio_mean=sum(tok)/sum(core),max_overlap_content_tokens=max(tok))

def contexts(out,config,ranking_path,index_manifest):
    from assemble import assemble
    from e1_batch import batched_search
    from smoke import counter
    c=counter();views=load(E1/'source-views-prepared.json');parents=load(E1/'public-parent-graph.json')
    ranks=jsonl(ranking_path);assert len(ranks)==80 and all(r['status']=='success' for r in ranks)
    receipts=[]
    with batched_search():
        for B in BUDGETS:
            for panel in PANELS:
                path=out/f'contexts-{config}-P0-{B}-{panel}.jsonl';started=time.perf_counter();secs=[];tokens=[]
                with path.open('x',encoding='utf8',newline='\n') as f:
                    for row in ranks:
                        v=assemble(row['results']['R4'],views,parents,'P0',B,panel,c)
                        v.update(intent_id=row['intent_id'],configuration_id=config,index_sha256=index_manifest,query_sha256=row['query_sha256'],source_sha256=row['source_sha256'],parent_sha256=row['parent_sha256'],ranking_file_sha256=sha(ranking_path))
                        f.write(json.dumps(v,ensure_ascii=False)+'\n');secs.append(v['assembly_seconds']);tokens.append(v['final']['token_count'])
                rec=dict(configuration_id=config,strategy='P0',budget=B,panel_id=panel,contexts=80,wall_seconds=time.perf_counter()-started,mean_seconds=statistics.mean(secs),median_seconds=statistics.median(secs),mean_final_tokens=statistics.mean(tokens),contexts_file_sha256=sha(path))
                save_json(out/(path.stem+'-receipt.json'),rec);receipts.append(rec);print('assembled',config,B,panel,flush=True)
    return receipts

def run(out,configs):
    patch();os.environ['RAYON_NUM_THREADS']=os.environ.get('RAYON_NUM_THREADS','8')
    for k in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE'):os.environ[k]='1'
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8';os.environ['ANONYMIZED_TELEMETRY']='False'
    inputs=load(out/'e2-inputs-r01.json')
    for name,h in inputs['inputs_sha256'].items():
        if sha(ROOT/name)!=h:raise ValueError('E2 input drift '+name)
    verify_e0();queries=out/'queries.jsonl';load_queries(queries,80)
    from smoke import counter
    started=time.perf_counter();m=e1.models();save_json(out/f'model-load-cost-e2-{"_".join(configs)}.json',dict(seconds=time.perf_counter()-started,local_cuda=True))
    ledger=out/'config-ledger.jsonl'
    for config in configs:
        e1.record_stage(ledger,config,'build','running');e1.build(E0,out,config,m);e1.record_stage(ledger,config,'build','completed')
        d=out/('index-'+config);save_json(d/'overlap-profile.json',dict(overlap_profile(d,config,counter()),equivalence=OVERLAP_EQUIVALENCE.get(config)))
        e1.record_stage(ledger,config,'retrieve','running');e1.retrieve(E0,out,config,queries,m);e1.record_stage(ledger,config,'retrieve','completed')
        e1.record_stage(ledger,config,'contexts','running');contexts(out,config,d/'rankings.jsonl',sha(d/'manifest.json'));e1.record_stage(ledger,config,'contexts','completed')
        save_json(out/f'status-e2-{config}.json',dict(configuration_id=config,status='assembled',e2_sha256=sha(__file__),generation_calls=0))
    verify_e0()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['prepare','run','core-check']);p.add_argument('--output',type=Path,required=True);p.add_argument('--config',action='append',choices=list(CONFIGS));a=p.parse_args()
    out=a.output.resolve()
    if not out.is_dir():p.error('output must exist')
    if a.stage=='prepare':prepare(out)
    elif a.stage=='core-check':
        patch();from smoke import counter;c=counter();res={}
        for config in (a.config or list(CONFIGS)):
            t=time.perf_counter();views,rows=overlap_children(E0,config,c)
            res[config]=dict(children=len(rows),attached=sum(bool(r['overlap_spans']) for r in rows),core_equal_to_E1=True,seconds=time.perf_counter()-t)
            print(config,res[config],flush=True)
        save_json(out/f'core-check-{"_".join(sorted(res))}.json',res)
    else:run(out,a.config or list(CONFIGS))

if __name__=='__main__':main()
