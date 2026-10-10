"""Session 5B E4 only: M0/M1 structural prefix for the frozen first candidate C2-L384-O0.

M0 is the strictly equivalent E1 index/ranking with the E3 -11 P0 contexts (reused).
M1 recomputes the frozen E1 core children (byte-equal check), applies the Session 2
chunkers.render_prefix (title/heading spans, <=64 BGE tokens incl. specials) to the
retrieval representation only, builds an independent real index and runs the real
80-intent retrieval through the unchanged E1 functions. P0 contexts read only
core/overlap spans, so the prefix never enters context, support text or scoring.
No final rerun here, no generation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import statistics
import time
from pathlib import Path
import e1
import e2
from runtime import ROOT, sha, save_json, load_queries

E0=e2.E0;E1=e2.E1;E3=e2.E3
E2=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
BASE='C2-L384-O0-M0'
CONFIG='C2-L384-O0-M1'
PREFIX={'mode':'M1','max_tokens':64}
RULE='e4-prefix-selection-rule-r01.md'

_original_configurations=e1.configurations
_original_make_children=e1.make_children
_original_identity=e1.identity

def configurations():
    out=dict(_original_configurations());out[CONFIG]=out[BASE];return out

PREFIX_AUDIT={}

def prefix_children(e0,config,c):
    """Recompute E1 core children, prove byte-equality to E1, then add the M1 prefix."""
    from chunkers import render_prefix
    views,core=_original_make_children(e0,BASE,c)
    frozen=e2.base_children(BASE)
    if len(core)!=len(frozen) or any(json.dumps(a,sort_keys=True,ensure_ascii=False)!=json.dumps(b,sort_keys=True,ensure_ascii=False) for a,b in zip(core,frozen)):
        raise ValueError('E4 core children differ from frozen E1 '+BASE)
    vs={v['doc_id']:v for v in views};rows=[]
    heading_ids={(v['doc_id'],e['element_id']) for v in views for e in v['elements'] if e['element_type'] in ('title','heading')}
    for ch in core:
        o=render_prefix(ch,PREFIX,vs[ch['doc_id']],c)
        if o['core_spans']!=ch['core_spans'] or o['overlap_spans']!=ch['overlap_spans'] or o['source_text']!=ch['source_text'] or o['core_sha256']!=ch['core_sha256'] or o['parent_ids']!=ch['parent_ids']:
            raise ValueError('prefix changed core/overlap/source text')
        if any((s['doc_id'],s['element_id']) not in heading_ids for s in o['prefix_spans']):raise ValueError('prefix span outside title/heading elements')
        if o['prefix_spans'] and c.count(o['prefix_text'])>64:raise ValueError('prefix exceeds 64 BGE tokens')
        o['policy']=dict(ch['policy'],M='M1',prefix_max_tokens=64,prefix_rule='chunkers.render_prefix session2')
        o.update(text=o['retrieval_text'],text_sha256=hashlib.sha256(o['retrieval_text'].encode()).hexdigest(),base_chunk_id=ch['chunk_id'],prefix_mode='M1')
        rows.append(o)
    if len({x['chunk_id'] for x in rows})!=len(rows):raise ValueError('duplicate prefix children')
    PREFIX_AUDIT[config]=dict(rows=len(rows),core_children_equal_E1=True,prefix_spans_title_heading_only=True,chunkers_sha256=sha(e2.EXP/'chunkers.py') if hasattr(e2,'EXP') else None)
    return views,rows

def make_children(e0,config,c):
    if config==CONFIG:return prefix_children(e0,config,c)
    return _original_make_children(e0,config,c)

def identity(e0,config,c):
    value=_original_identity(e0,config,c)
    if config==CONFIG:
        value['code']['experiments/pearl-chunking-dev80-20261005/e4.py']=sha(__file__)
        value['E4']=dict(base_configuration=BASE,prefix=PREFIX,base_index_manifest_sha256=sha(E1/('index-'+BASE)/'manifest.json'),base_child_chunks_sha256=sha(E1/('index-'+BASE)/'child_chunks.jsonl'),O=0,recovery='P0')
    return value

def patch():
    e1.configurations=configurations;e1.make_children=make_children;e1.identity=identity

INPUTS=[E2/'delivery-manifest.json',E2/'e2-overlap-selection-r01.json',E2/'common-support-map-e2-r11.json',E2/'map-lineage-e2-r11.json',E2/'scores-e2-r11.json',E2/'score-details-e2-r11.jsonl',
        E3/'delivery-manifest.json',E3/'recovery-selection-e3-r10.json',E1/'delivery-manifest.json',E1/'queries.jsonl',E2/'queries.jsonl']

def prepare(out):
    """Model-free: input bindings, query copy, M0 strict-equivalence binding."""
    if not (out/RULE).is_file():raise ValueError('selection rule must be saved before E4')
    check=json.loads((out/'input-check-5A-r01.json').read_text('utf8'))
    if check['status']!='passed':raise ValueError('5A delivery not verified')
    e0check=e2.verify_e0();runs={run.name:e2.verify_run(run) for run in (E1,E3)}
    sel=json.loads((E2/'e2-overlap-selection-r01.json').read_text('utf8'))
    if sel['cores'][BASE]['status']!='frozen' or sel['cores'][BASE]['selected']!=BASE:raise ValueError('C2 overlap not frozen O0')
    if sha(E1/'queries.jsonl')!=sha(E2/'queries.jsonl'):raise ValueError('query copy drift')
    shutil.copyfile(E2/'queries.jsonl',out/'queries.jsonl');load_queries(out/'queries.jsonl',80)
    d=E1/('index-'+BASE);ranks=sha(d/'rankings.jsonl')
    if ranks!=sel['cores'][BASE]['configs'][BASE]['rankings_sha256']:raise ValueError('M0 ranking drift')
    ctx={}
    for B in e2.BUDGETS:
        for panel in e2.PANELS:
            p=E3/f'contexts-{BASE}-P0-{B}-{panel}.jsonl';ctx[p.relative_to(ROOT).as_posix()]=sha(p)
            if any(r['ranking_file_sha256']!=ranks for r in e2.jsonl(p)):raise ValueError('M0 context/ranking binding drift')
    save_json(out/'e4-inputs-r01.json',dict(e0_check=e0check,run_checks=runs,inputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in INPUTS},queries_copy_sha256=sha(out/'queries.jsonl'),
        selection_rule_sha256=sha(out/RULE),input_check_5A_sha256=sha(out/'input-check-5A-r01.json'),
        m0_reuse=dict(configuration_id=BASE,index_manifest_sha256=sha(d/'manifest.json'),child_chunks_sha256=sha(d/'child_chunks.jsonl'),rankings_sha256=ranks,e3_p0_contexts_sha256=ctx,
            reuse='exact: E4 M0 arm = E1 C2-L384-O0-M0 index and R4 ranking; contexts = E3 -11 P0 files; scored in E2 under r11'),
        m1=dict(configuration_id=CONFIG,prefix=PREFIX,implementation='chunkers.render_prefix',chunkers_sha256=sha(e2.EXP/'chunkers.py') if hasattr(e2,'EXP') else None),
        strategy='P0',budgets=e2.BUDGETS,panels=e2.PANELS,generation_calls=0))
    print('prepared',flush=True)

def prefix_profile(directory,c):
    rows=e2.jsonl(directory/'child_chunks.jsonl');tok=[];slot={};truncated=0;empty=0
    for x in rows:
        if not x['prefix_spans']:empty+=1;tok.append(0);continue
        tok.append(c.count(x['prefix_text'])-c.count(''))
    lengths=[c.count(x['text']) for x in rows]
    return dict(configuration_id=CONFIG,children=len(rows),with_prefix=len(rows)-empty,without_prefix=empty,prefix_content_tokens_mean=statistics.mean(tok),prefix_content_tokens_max=max(tok),
        prefix_tokens_at_cap=sum(t+c.count('')>=64 for t in tok if t),retrieval_tokens_max=max(lengths),retrieval_tokens_mean=statistics.mean(lengths),limit_including_specials=64)

def run(out):
    patch();os.environ['RAYON_NUM_THREADS']=os.environ.get('RAYON_NUM_THREADS','8')
    for k in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE'):os.environ[k]='1'
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8';os.environ['ANONYMIZED_TELEMETRY']='False'
    inputs=json.loads((out/'e4-inputs-r01.json').read_text('utf8'))
    for name,h in inputs['inputs_sha256'].items():
        if sha(ROOT/name)!=h:raise ValueError('E4 input drift '+name)
    e2.verify_e0();queries=out/'queries.jsonl';load_queries(queries,80)
    from smoke import counter
    started=time.perf_counter();m=e1.models();save_json(out/'model-load-cost-e4.json',dict(seconds=time.perf_counter()-started,local_cuda=True))
    ledger=out/'config-ledger.jsonl'
    e1.record_stage(ledger,CONFIG,'build','running');e1.build(E0,out,CONFIG,m);e1.record_stage(ledger,CONFIG,'build','completed')
    d=out/('index-'+CONFIG);save_json(d/'prefix-profile.json',dict(prefix_profile(d,counter()),audit=PREFIX_AUDIT.get(CONFIG)))
    e1.record_stage(ledger,CONFIG,'retrieve','running');e1.retrieve(E0,out,CONFIG,queries,m);e1.record_stage(ledger,CONFIG,'retrieve','completed')
    e1.record_stage(ledger,CONFIG,'contexts','running');e2.contexts(out,CONFIG,d/'rankings.jsonl',sha(d/'manifest.json'));e1.record_stage(ledger,CONFIG,'contexts','completed')
    save_json(out/f'status-e4-{CONFIG}.json',dict(configuration_id=CONFIG,status='assembled',e4_sha256=sha(__file__),generation_calls=0))
    e2.verify_e0()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['prepare','run','prefix-check']);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve()
    if not out.is_dir():p.error('output must exist')
    if a.stage=='prepare':prepare(out)
    elif a.stage=='prefix-check':
        patch();from smoke import counter;c=counter();t=time.perf_counter();views,rows=prefix_children(E0,CONFIG,c)
        lengths=[c.count(r['text']) for r in rows]
        res=dict(children=len(rows),with_prefix=sum(bool(r['prefix_spans']) for r in rows),max_retrieval_tokens=max(lengths),core_equal_to_E1=True,seconds=time.perf_counter()-t)
        print(res,flush=True);save_json(out/'prefix-check-r01.json',res)
    else:run(out)

if __name__=='__main__':main()
