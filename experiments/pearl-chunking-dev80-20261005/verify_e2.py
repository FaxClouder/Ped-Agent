"""Independent reopen verification for Session 5 E2 (no models, no retrieval, no generation).

Reopens saved files only: input bindings, O10/O20 index manifests and children
(core equal to E1, overlap limit and barriers), rankings, every context (recounted
with the frozen tokenizer), and the saved score details / aggregates / transitions /
statistics / decisions for one scoring revision, recomputed from saved spans.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
import random
from pathlib import Path
from runtime import ROOT, sha, save_json, verify_index, cache_identity, load_queries
from smoke import counter
from source_view import text_for_spans
from assemble import serialize, digest, key, unit, views_by_id, _expand
from e1_visible_review_verify import intervals, all_inside, sufficient
import e3_scope_revision as rev

E0=ROOT/'outputs/pearl-chunking-dev80-20261005-03'
E1=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
BASES={'C2-L384-O0-M0':('C2',384),'C3-L256-O0-M0':('C3',256)}
RATIOS={'O10':0.1,'O20':0.2}
NEW={b.replace('-O0-',f'-{o}-'):(b,r) for b in BASES for o,r in RATIOS.items()}
ALL=[c for b in BASES for c in (b,b.replace('-O0-','-O10-'),b.replace('-O0-','-O20-'))]
PANELS=('fixed_budget_main','seed10_diagnostic');BUDGETS=(4096,8192);STAGES=('raw','expanded','deduplicated','final')

def load(p):return json.loads(Path(p).read_text('utf8'))
def rows(p):
    with Path(p).open(encoding='utf8') as f:return [json.loads(l) for l in f if l.strip()]
def index_dir(c):return (E1 if '-O0-' in c else OUT)/('index-'+c)
def ctx_path(c,B,panel):return (E3 if '-O0-' in c else OUT)/f'contexts-{c}-P0-{B}-{panel}.jsonl'

def check_inputs():
    inputs=load(OUT/'e2-inputs-r01.json')
    for name,h in inputs['inputs_sha256'].items():assert sha(ROOT/name)==h,name
    assert sha(OUT/'queries.jsonl')==inputs['queries_copy_sha256']
    assert sha(OUT/'e2-overlap-selection-rule-r01.md')==inputs['selection_rule_sha256']
    for base,o in inputs['o0_reuse'].items():
        d=E1/('index-'+base)
        assert sha(d/'manifest.json')==o['index_manifest_sha256'] and sha(d/'child_chunks.jsonl')==o['child_chunks_sha256'] and sha(d/'rankings.jsonl')==o['rankings_sha256']
        for name,h in o['e3_p0_contexts_sha256'].items():assert sha(E3/name)==h,name
    m=load(E3/'delivery-manifest.json')
    drift=[n for n,h in m['artifacts_sha256'].items() if n.startswith('outputs/') and sha(ROOT/n)!=h]
    assert not drift,drift[:3]
    return dict(input_bindings=len(inputs['inputs_sha256']),e3_frozen_outputs_checked=sum(n.startswith('outputs/') for n in m['artifacts_sha256']))

def overlap_suffix(core,view):
    """Rebuild the attach_overlap candidate text; return (text, run-local elements)."""
    first=core['core_spans'][0];lookup={e['element_id']:e for e in view['elements']}
    run=next(run for run in view['barrier_runs'] if first['element_id'] in run);elements=[]
    for eid in run:
        e=lookup[eid]
        if core['policy']['C']=='C3' and e['heading_path']!=lookup[first['element_id']]['heading_path']:elements=[];continue
        if eid==first['element_id']:elements.append(dict(e,text=e['text'][:first['start']]));break
        elements.append(e)
    return '\n\n'.join(e['text'] for e in elements),elements

def check_index(config,c,views):
    base,r=NEW[config];C,L=BASES[base];limit=math.floor(r*L);d=OUT/('index-'+config)
    verify_index(d/'manifest.json');man=load(d/'manifest.json');e2=man['configuration']['E2']
    assert e2['base_configuration']==base and e2['overlap_ratio']==r and e2['overlap_limit_tokens']==limit and e2['M']=='M0' and e2['recovery']=='P0'
    assert e2['base_index_manifest_sha256']==sha(E1/('index-'+base)/'manifest.json') and e2['base_child_chunks_sha256']==sha(E1/('index-'+base)/'child_chunks.jsonl')
    new=rows(d/'child_chunks.jsonl');old=rows(E1/('index-'+base)/'child_chunks.jsonl')
    assert len(new)==len(old)==man['child_count'] and len({x['chunk_id'] for x in new})==len(new)
    vs={v['doc_id']:v for v in views};attached=0;overlap_tokens=[];passage=[];barrier=0
    for o,b in zip(new,old):
        assert o['base_chunk_id']==b['chunk_id']
        for k in ('core_spans','core_text','core_sha256','parent_ids','is_table','doc_id'):assert o[k]==b[k],(config,k)
        assert o['policy']['O']==r and o['policy']['C']==C and o['policy']['L']==L
        assert o['text']==o['retrieval_text']==o['source_text']==text_for_spans(views,o['overlap_spans']+o['core_spans'])
        if o['is_table']:assert not o['overlap_spans'];continue
        if not o['overlap_spans']:assert o['text']==b['text'];continue
        attached+=1;view=vs[o['doc_id']];text,elements=overlap_suffix(o,view)
        ids=[e['element_id'] for e in elements];first=o['core_spans'][0]
        for s in o['overlap_spans']:
            assert s['element_id'] in ids,'overlap crosses barrier/heading'
            if s['element_id']==first['element_id']:assert s['end']<=first['start']
        # overlap spans form one contiguous suffix of the candidate text ending at the core start
        assert not any(e.get('_source_offset') for e in elements)
        offset=0;starts={}
        for e in elements:starts[e['element_id']]=offset;offset+=len(e['text'])+2
        start=starts[o['overlap_spans'][0]['element_id']]+o['overlap_spans'][0]['start'];suffix=text[start:]
        assert suffix.rstrip('\n')==text_for_spans(views,o['overlap_spans']),'overlap is not a contiguous suffix'
        overlap_tokens.append(suffix);barrier+=1
    counts=[len(e.ids) for e in c._tokenizer.encode_batch(overlap_tokens)] if overlap_tokens else []
    assert len(counts)==attached and all(n<=limit for n in counts),('overlap limit',config,max(counts))
    plens=[len(e.ids) for e in c._tokenizer.encode_batch([o['text'] for o in new])]
    assert max(plens)<=1024
    assert sha(d/'child_chunks.jsonl')==man['output_sha256']['child_chunks.jsonl']
    # rankings
    qs={q['intent_id']:q for q in load_queries(OUT/'queries.jsonl',80)};ranks=rows(d/'rankings.jsonl');ids={x['chunk_id'] for x in new}
    assert len(ranks)==80 and {x['intent_id'] for x in ranks}==set(qs) and all(x['status']=='success' for x in ranks)
    for x in ranks:
        assert x['index_sha256']==sha(d/'manifest.json') and x['query_sha256']==cache_identity(qs[x['intent_id']])
        assert x['source_sha256']==sha(E0/'source-views-prepared.json') and x['parent_sha256']==sha(E0/'public-parent-graph.json')
        assert len(x['results']['R4'])==100 and all(h['chunk_id'] in ids for h in x['results']['R4'])
    cost=load(d/'retrieval-cost.json');assert cost['rankings_sha256']==sha(d/'rankings.jsonl') and not cost['failed_intents'] and cost['queries']==80
    return dict(children=len(new),attached=attached,limit_tokens_including_specials=limit,max_overlap_tokens_including_specials=max(counts),max_passage_tokens=max(plens),rankings=80,ranking_failures=0,core_equal_to_E1=True)

def check_contexts(c,views,parents):
    vs=views_by_id(views);elements={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']}
    cache={};checked=0;files={}
    for config in ALL:
        rp=index_dir(config)/'rankings.jsonl';rh=sha(rp);rankings={r['intent_id']:r for r in rows(rp)}
        for B in BUDGETS:
            for panel in PANELS:
                p=ctx_path(config,B,panel);saved=rows(p);assert len(saved)==80 and len({x['intent_id'] for x in saved})==80;files[p.relative_to(ROOT).as_posix()]=sha(p)
                if '-O0-' not in config:assert load(p.with_name(p.stem+'-receipt.json'))['contexts_file_sha256']==sha(p)
                for ctx in saved:
                    assert ctx['configuration_id']==config and ctx['strategy']=='P0' and ctx['budget']==B and ctx['panel_id']==panel
                    # E3 seed10 files (reused O0) bind the ranking file only; new files must also bind the index.
                    assert ctx['ranking_file_sha256']==rh and ('-O0-' in config and 'index_sha256' not in ctx or ctx['index_sha256']==sha(index_dir(config)/'manifest.json'))
                    n=10 if panel=='seed10_diagnostic' else 100;rank=rankings[ctx['intent_id']]['results']['R4'][:n]
                    assert ctx['ranking_sha256']==digest(rank)
                    assert ctx['raw']['units']==[unit(ch['core_spans']+ch.get('overlap_spans',[]),vs,ch['chunk_id'],j) for j,ch in enumerate(rank,1)]
                    assert ctx['expanded']['units']==[unit(_expand(ch,vs,parents,'P0'),vs,ch['chunk_id'],j) for j,ch in enumerate(rank,1)]
                    for stage in STAGES:
                        s=ctx[stage];rendered=serialize(s['units'])
                        assert rendered==s['serialized_context'] and digest(rendered)==s['text_sha256']
                        if s['text_sha256'] not in cache:cache[s['text_sha256']]=c.count(rendered)
                        assert cache[s['text_sha256']]==s['token_count']
                        for u in s['units']:
                            assert digest(u['text'])==u['text_sha256']
                            for part in u['parts']:
                                sp=part['span'];assert u['text'][part['text_start']:part['text_end']]==elements[key(sp)][sp['start']:sp['end']]
                    assert ctx['final']['token_count']<=B
                    exp=[s for u in ctx['expanded']['units'] for s in u['spans']];ds=[s for u in ctx['deduplicated']['units'] for s in u['spans']]
                    iv=intervals(ds);assert sum(s['end']-s['start'] for s in ds)==sum(b-a for v in iv.values() for a,b in v) and intervals(exp)==iv
                    assert all_inside([s for u in ctx['final']['units'] for s in u['spans']],iv)
                    checked+=1
    assert checked==len(ALL)*4*80
    return dict(contexts=checked,unique_serializations_recounted=len(cache),files=files)

def recompute_scores(revision):
    scores=load(OUT/f'scores-e2-{revision}.json');mp=ROOT/scores['mapping_path'];assert sha(mp)==scores['mapping_sha256']
    maps={r['intent_id']:r for r in load(mp)['records']};mh=scores['mapping_sha256']
    saved={(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']):d for d in rows(OUT/f'score-details-e2-{revision}.jsonl')}
    assert len(saved)==len(ALL)*4*80*4==scores['score_cells']
    look={}
    for config in ALL:
        for B in BUDGETS:
            for panel in PANELS:
                p=ctx_path(config,B,panel);fh=sha(p)
                for ctx in rows(p):
                    m=maps[ctx['intent_id']]
                    for stage in STAGES:
                        spans=[s for u in ctx[stage]['units'] for s in u['spans']];iv=intervals(spans)
                        sup={q['requirement_id']:rev.independent_status(q,spans,iv) for q in m['requirements']}
                        suff=sufficient(m['groups'],sup);d=saved[config,B,panel,ctx['intent_id'],stage]
                        assert d['support']==sup and d['sufficient']==suff and d['mapping_sha256']==mh and d['contexts_file_sha256']==fh and d['visible_text_sha256']==ctx[stage]['text_sha256'],(config,B,panel,ctx['intent_id'],stage)
                        look[config,B,panel,ctx['intent_id'],stage]=suff
    ids=sorted(maps)
    for s in scores['summary']:
        v=[look[s['configuration_id'],s['budget'],s['panel_id'],i,'final'] for i in ids]
        assert (s['yes'],s['no'],s['unknown'],s['n'])==(v.count('yes'),v.count('no'),v.count('unknown'),80)
    for cfg,v in scores['cegr10'].items():
        for B in BUDGETS:assert v['yes']==sum(look[cfg,B,'seed10_diagnostic',i,'raw']=='yes' for i in ids)
        assert v['unknown']==sum(look[cfg,4096,'seed10_diagnostic',i,'raw']=='unknown' for i in ids)
    tr=rows(OUT/f'transitions-e2-{revision}.jsonl');assert len(tr)==4*4*80
    for t in tr:assert t['before']==look[t['base'],t['budget'],t['panel_id'],t['intent_id'],'final'] and t['after']==look[t['configuration_id'],t['budget'],t['panel_id'],t['intent_id'],'final']
    # bootstrap reimplemented from the stated protocol
    strata=collections.defaultdict(list)
    for i,m in maps.items():strata[m['main_stratum']].append(i)
    rng=random.Random(20261005);draws=[[rng.choice(strata[t]) for t in sorted(strata) for _ in strata[t]] for _ in range(10000)]
    st={(x['configuration_id'],x['budget'],x['panel_id']):x for x in scores['statistics']};assert len(st)==16
    for (cfg,B,panel),x in st.items():
        base=x['base'];d={i:int(look[cfg,B,panel,i,'final']=='yes')-int(look[base,B,panel,i,'final']=='yes') for i in ids}
        vals=sorted(sum(d[i] for i in s)/80 for s in draws)
        assert abs(x['confirmed_yes_difference']-sum(d.values())/80)<1e-12 and x['bootstrap_95']==[vals[249],vals[9749]]
        a=[look[base,B,panel,i,'final'] for i in ids];b=[look[cfg,B,panel,i,'final'] for i in ids]
        assert x['confirmed_gain']==sum(p=='no' and q=='yes' for p,q in zip(a,b)) and x['confirmed_loss']==sum(p=='yes' and q=='no' for p,q in zip(a,b))
    # decision rule r01
    for base,dec in scores['decisions'].items():
        arms=[base,base.replace('-O0-','-O10-'),base.replace('-O0-','-O20-')];rows_=[]
        for cfg in arms:
            v=[look[cfg,4096,'fixed_budget_main',i,'final'] for i in ids]
            rows_.append((cfg,v.count('yes'),v.count('unknown'),scores['cegr10'][cfg]['yes'],{'O0':0,'O10':.1,'O20':.2}[cfg.split('-')[2]]))
        order=sorted(rows_,key=lambda r:(-r[1],-r[3],r[4]));best=order[0]
        threats=[r[0] for r in order[1:] if r[1]+r[2]>=best[1]]
        assert dec['order']==[r[0] for r in order] and dec['threats']==threats and dec['selected']==(None if threats else best[0])
    return dict(revision=revision,mapping_sha256=mh,score_cells=len(saved),summaries=len(scores['summary']),transitions=len(tr),bootstrap_cells=len(st),decisions={b:dict(status=d['status'],selected=d['selected'],threats=d['threats']) for b,d in scores['decisions'].items()})

def o0_parity(revision):
    """O0 E2 details must equal the -11 E3 r10 P0 details cell by cell (strict reuse)."""
    if revision!='r10':return None
    old={(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']):d for d in rows(E3/'score-details-e3-r10.jsonl') if d['strategy']=='P0' and d['configuration_id'] in BASES}
    new={(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']):d for d in rows(OUT/'score-details-e2-r10.jsonl') if d['configuration_id'] in BASES}
    assert set(old)==set(new) and len(new)==2*4*80*4
    fields=('sufficient','support','support_basis','coverage_lower','coverage_upper','failure','visible_text_sha256','contexts_file_sha256','mapping_sha256','ranking_file_sha256','context_id')
    for k,v in new.items():assert all(v.get(f)==old[k].get(f) for f in fields),k
    return dict(cells=len(new),fields=list(fields),status='passed')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--revision',action='append',required=True);p.add_argument('--receipt',required=True);a=p.parse_args()
    target=OUT/a.receipt
    if target.exists():raise FileExistsError(target)
    c=counter();views=load(E0/'source-views-prepared.json');parents=load(E0/'public-parent-graph.json')
    assert sha(E0/'source-views-prepared.json')==sha(E1/'source-views-prepared.json') and sha(E0/'public-parent-graph.json')==sha(E1/'public-parent-graph.json')
    result=dict(status='passed',inputs=check_inputs())
    result['indexes']={cfg:check_index(cfg,c,views) for cfg in NEW};print('indexes passed',flush=True)
    result['contexts']=check_contexts(c,views,parents);print('contexts passed',flush=True)
    result['scores']={r:recompute_scores(r) for r in a.revision};result['o0_parity_with_e3_r10']=o0_parity('r10') if 'r10' in a.revision else None
    result.update(verifier_sha256=sha(__file__),tokenizer_fingerprint=c.fingerprint,retrieval_calls=0,generation_calls=0,model_calls=0)
    save_json(target,result);print(json.dumps({k:result[k] for k in ('status','scores')},ensure_ascii=False,indent=1),flush=True)

if __name__=='__main__':main()
