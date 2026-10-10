"""Independent reopen verification for Session 5B (E4 + final freeze); no models, no retrieval, no generation.

Reopens saved files only: input bindings, the M1 index (core equal to E1, prefix spans
title/heading only, prefix rule re-derived independently, <=64 tokens, model input
limit), rankings, every context of the four scored configurations (recounted with the
frozen tokenizer), Layer 1/Layer 2 details recomputed from saved spans with the
independent projection, aggregates/transitions/bootstrap/decision, strict-equivalence
parity with E2 r11, and the E5 request inputs rebuilt from the historical prompt record.
"""
from __future__ import annotations
import argparse
import collections
import json
import random
from pathlib import Path
from runtime import ROOT, sha, save_json, verify_index, load_queries
from smoke import counter
from source_view import text_for_spans
from assemble import serialize, digest, key, unit, views_by_id, _expand
from e1_visible_review_verify import intervals, all_inside, sufficient
import e3_scope_revision as rev

E1=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
E2=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-13'
M0='C2-L384-O0-M0';M1='C2-L384-O0-M1';C3='C3-L256-O0-M0';B0='B0-regex320-overlap48-M0'
ALL=(M0,M1,C3,B0)
PANELS=('fixed_budget_main','seed10_diagnostic');BUDGETS=(4096,8192);STAGES=('raw','expanded','deduplicated','final')
METHODS=('R1','R2','R3','R4');KS=(1,5,10,20)

def load(p):return json.loads(Path(p).read_text('utf8'))
def rows(p):
    with Path(p).open(encoding='utf8') as f:return [json.loads(l) for l in f if l.strip()]
def index_dir(c):return (OUT if c==M1 else E1)/('index-'+c)
def ctx_path(c,B,panel):return (OUT if c==M1 else E3)/f'contexts-{c}-P0-{B}-{panel}.jsonl'

def check_inputs():
    i=load(OUT/'e4-inputs-r01.json');drift=[n for n,h in i['inputs_sha256'].items() if sha(ROOT/n)!=h]
    assert not drift,drift
    assert i['selection_rule_sha256']==sha(OUT/'e4-prefix-selection-rule-r01.md')
    assert load(OUT/'input-check-5A-r01.json')['status']=='passed'
    for p,h in i['m0_reuse']['e3_p0_contexts_sha256'].items():assert sha(ROOT/p)==h
    assert sha(OUT/'queries.jsonl')==i['queries_copy_sha256'];load_queries(OUT/'queries.jsonl',80)
    # the rule must predate every M1 index file
    rule_time=(OUT/'e4-prefix-selection-rule-r01.md').stat().st_mtime
    assert all(p.stat().st_mtime>rule_time for p in index_dir(M1).iterdir())
    return dict(status='passed',bindings=len(i['inputs_sha256']),rule_saved_before_index=True)

def expected_prefix(core,view,c):
    """Independent re-derivation of the frozen M1 allocation rule (chunkers.render_prefix r01)."""
    els=view['elements'];heads=[e for e in els if e['element_type'] in ('title','heading')]
    first=next(e for e in els if e['element_id']==core['core_spans'][0]['element_id'])
    order=heads[:1]
    for name in first['heading_path'][::-1]:
        h=next((x for x in heads if x['text']==name),None)
        if h is not None and all(h is not o for o in order):order.append(h)
    spans=[]
    for h in order:
        trial=spans+[h['span']]
        if c.count(text_for_spans(view,trial))<=64:spans=trial;continue
        _,offs=c.encode_with_offsets(h['text']);best=None
        for a,b in offs:
            if b>a and c.count(text_for_spans(view,spans+[dict(h['span'],start=0,end=b)]))<=64:best=b if best is None else max(best,b)
        if best is not None:spans.append(dict(h['span'],start=0,end=best))
        break
    return spans

def check_m1_index(c,views):
    d=index_dir(M1);verify_index(d/'manifest.json');m=load(d/'manifest.json')
    new=rows(d/'child_chunks.jsonl');old=rows(index_dir(M0)/'child_chunks.jsonl');assert len(new)==len(old)==m['child_count']
    vs={v['doc_id']:v for v in views};with_prefix=0;maxlen=0;cache={}
    for a,b in zip(new,old):
        for f in ('core_spans','overlap_spans','core_text','source_text','core_sha256','parent_ids','doc_id','source_version','is_table'):assert a[f]==b[f],f
        assert a['base_chunk_id']==b['chunk_id']
        v=vs[a['doc_id']];hid={e['element_id'] for e in v['elements'] if e['element_type'] in ('title','heading')}
        assert all(s['element_id'] in hid for s in a['prefix_spans'])
        assert a['prefix_spans']==expected_prefix(b,v,c),a['chunk_id']
        if a['prefix_spans']:
            with_prefix+=1;pt=text_for_spans(v,a['prefix_spans']);assert pt==a['prefix_text'] and c.count(pt)<=64
            assert a['text']==a['retrieval_text']==pt+'\n\n'+a['source_text']
        else:assert a['text']==a['source_text']
        n=c.count(a['text']);maxlen=max(maxlen,n);assert n<=1024
    ident=m['configuration']['E4'];assert ident['base_child_chunks_sha256']==sha(index_dir(M0)/'child_chunks.jsonl') and ident['prefix']=={'mode':'M1','max_tokens':64}
    return dict(children=len(new),with_prefix=with_prefix,max_model_input_tokens=maxlen,core_equal_to_E1=True,prefix_rule_rederived=True)

def check_rankings():
    out={}
    for config in ALL:
        d=index_dir(config);rs=rows(d/'rankings.jsonl');ids={r['chunk_id']:r for r in rows(d/'child_chunks.jsonl')}
        assert len(rs)==80 and all(r['status']=='success' for r in rs) and len({r['intent_id'] for r in rs})==80
        for r in rs:
            assert r['index_sha256']==sha(d/'manifest.json')
            for ch in r['results']['R4']:assert ch['chunk_id'] in ids and ch['text']==ids[ch['chunk_id']]['text']
        out[config]=dict(rankings_sha256=sha(d/'rankings.jsonl'),intents=80)
    return out

def check_contexts(c,views,parents):
    vs=views_by_id(views);elements={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']}
    cache={};checked=0;files={}
    for config in ALL:
        rp=index_dir(config)/'rankings.jsonl';rh=sha(rp);rankings={r['intent_id']:r for r in rows(rp)}
        for B in BUDGETS:
            for panel in PANELS:
                p=ctx_path(config,B,panel);saved=rows(p);assert len(saved)==80 and len({x['intent_id'] for x in saved})==80;files[p.relative_to(ROOT).as_posix()]=sha(p)
                if config==M1:assert load(p.with_name(p.stem+'-receipt.json'))['contexts_file_sha256']==sha(p)
                for ctx in saved:
                    assert ctx['configuration_id']==config and ctx['strategy']=='P0' and ctx['budget']==B and ctx['panel_id']==panel
                    assert ctx['ranking_file_sha256']==rh and (config!=M1 and 'index_sha256' not in ctx or ctx['index_sha256']==sha(index_dir(config)/'manifest.json'))
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
    scores=load(OUT/f'scores-e4-{revision}.json');mp=ROOT/scores['mapping_path'];assert sha(mp)==scores['mapping_sha256']
    maps={r['intent_id']:r for r in load(mp)['records']};mh=scores['mapping_sha256'];ids=sorted(maps)
    saved={(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']):d for d in rows(OUT/f'score-details-e4-{revision}.jsonl')}
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
    for s in scores['summary']:
        v=[look[s['configuration_id'],s['budget'],s['panel_id'],i,'final'] for i in ids]
        assert (s['yes'],s['no'],s['unknown'],s['n'])==(v.count('yes'),v.count('no'),v.count('unknown'),80)
    # Layer 1 from rankings, independent projection
    l1={(d['configuration_id'],d['intent_id'],d['method'],d['k']):d for d in rows(OUT/f'layer1-details-e4-{revision}.jsonl')};assert len(l1)==len(ALL)*80*4*4==scores['layer1_cells']
    for config in ALL:
        for r in rows(index_dir(config)/'rankings.jsonl'):
            m=maps[r['intent_id']]
            for method in METHODS:
                spans=[]
                for rank,ch in enumerate(r['results'][method][:20],1):
                    spans=spans+ch['core_spans']+ch.get('overlap_spans',[])
                    if rank in KS:
                        iv=intervals(spans);sup={q['requirement_id']:rev.independent_status(q,spans,iv) for q in m['requirements']}
                        d=l1[config,r['intent_id'],method,rank];assert d['support']==sup and d['sufficient']==sufficient(m['groups'],sup) and d['prefix_spans_scored'] is False
    for s in scores['layer1_summary']:
        v=[l1[s['configuration_id'],i,s['method'],s['k']]['sufficient'] for i in ids];assert (s['yes'],s['no'],s['unknown'])==(v.count('yes'),v.count('no'),v.count('unknown'))
    for cfg,v in scores['cegr10'].items():
        for B in BUDGETS:assert v['yes']==sum(look[cfg,B,'seed10_diagnostic',i,'raw']=='yes' for i in ids)
        assert v['yes']==sum(l1[cfg,i,'R4',10]['sufficient']=='yes' for i in ids)
    tr=rows(OUT/f'transitions-e4-{revision}.jsonl');assert len(tr)==4*80
    for t in tr:assert t['before']==look[M0,t['budget'],t['panel_id'],t['intent_id'],'final'] and t['after']==look[M1,t['budget'],t['panel_id'],t['intent_id'],'final']
    strata=collections.defaultdict(list)
    for i,m in maps.items():strata[m['main_stratum']].append(i)
    rng=random.Random(20261005);draws=[[rng.choice(strata[t]) for t in sorted(strata) for _ in strata[t]] for _ in range(10000)]
    for x in scores['statistics']:
        cfg,base,B,panel=x['configuration_id'],x['base'],x['budget'],x['panel_id']
        d={i:int(look[cfg,B,panel,i,'final']=='yes')-int(look[base,B,panel,i,'final']=='yes') for i in ids};vals=sorted(sum(d[i] for i in s)/80 for s in draws)
        assert abs(x['confirmed_yes_difference']-sum(d.values())/80)<1e-12 and x['bootstrap_95']==[vals[249],vals[9749]]
    dec=scores['decision'];rws=[]
    for cfg in (M0,M1):
        v=[look[cfg,4096,'fixed_budget_main',i,'final'] for i in ids];rws.append((cfg,v.count('yes'),v.count('unknown'),scores['cegr10'][cfg]['yes'],0 if cfg==M0 else 1))
    order=sorted(rws,key=lambda r:(-r[1],-r[3],r[4]));best=order[0];threats=[r[0] for r in order[1:] if r[1]+r[2]>=best[1]]
    assert dec['order']==[r[0] for r in order] and dec['threats']==threats and dec['selected']==(None if threats else best[0])
    return dict(revision=revision,mapping_sha256=mh,score_cells=len(saved),layer1_cells=len(l1),summaries=len(scores['summary']),transitions=len(tr),bootstrap_cells=len(scores['statistics']),
        decision=dict(status=dec['status'],selected=dec['selected'],threats=dec['threats']))

def m0_parity(revision):
    """C2/C3 M0 details under r11 must equal E2 r11 cell by cell (strict reuse)."""
    if revision!='r11':return None
    fields=('sufficient','support','support_basis','coverage_lower','coverage_upper','failure','visible_text_sha256','contexts_file_sha256','mapping_sha256','ranking_file_sha256','context_id')
    old={(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']):d for d in rows(E2/'score-details-e2-r11.jsonl') if d['configuration_id'] in (M0,C3)}
    new={(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']):d for d in rows(OUT/'score-details-e4-r11.jsonl') if d['configuration_id'] in (M0,C3)}
    assert set(old)==set(new) and len(new)==2*4*80*4
    for k,v in new.items():assert all(v.get(f)==old[k].get(f) for f in fields),k
    return dict(cells=len(new),fields=list(fields),status='passed')

def check_e5(scores_revision):
    freeze=load(OUT/'final-config-freeze-r01.json');plan=load(OUT/'e5-call-plan-r01.json');ev=load(OUT/'evaluation-versions-r01.json')
    cfgs=[r['configuration_id'] for r in freeze['configurations']];assert len(cfgs)<=3 and B0 in cfgs and len(set(cfgs))==len(cfgs)
    for r in freeze['configurations']:
        d=ROOT/r['index_dir'];assert sha(d/'manifest.json')==r['index_manifest_sha256'] and sha(d/'rankings.jsonl')==r['rankings_sha256'] and sha(ROOT/r['contexts_4096_main'])==r['contexts_4096_main_sha256']
    template=load(ROOT/plan['prompt']['historical_prompt_record'])['prompt_template']
    assert digest(template)==plan['prompt']['template_sha256']
    queries={q['intent_id']:q['query'] for q in load_queries(OUT/'queries.jsonl',80)}
    reqs=rows(OUT/'e5-request-inputs-r01.jsonl');assert len(reqs)==len(cfgs)*80
    ctx={(r['configuration_id']):{x['intent_id']:x for x in rows(ROOT/r['contexts_4096_main'])} for r in freeze['configurations']}
    first={}
    for q in reqs:
        x=ctx[q['configuration_id']][q['intent_id']];text=x['final']['serialized_context']
        content=template.format(query=queries[q['intent_id']],exact_saved_context=text)
        messages=[{'role':'user','content':content}];canon=json.dumps(messages,ensure_ascii=False,sort_keys=True,separators=(',',':'))
        assert digest(content)==q['request_sha256'] and digest(canon)==q['messages_sha256'] and len(canon.encode('utf-8'))==q['request_utf8_bytes']<=plan['request_length']['admission_bound_utf8_bytes']
        assert digest(text)==q['context_sha256'] and x['final']['token_count']==q['context_bge_tokens']<=4096 and q['gold_or_reference_in_request'] is False
        f=first.setdefault(q['request_sha256'],(q['configuration_id'],q['intent_id']))
        assert (q['shares_request_with'] is None)==(f==(q['configuration_id'],q['intent_id']))
    cells=rows(OUT/'e5-cell-order-r01.jsonl');assert len(cells)==len(cfgs)*80*3==plan['calls']['logical_cells']
    assert {(c['configuration_id'],c['intent_id'],c['replicate_id']) for c in cells}=={(a,i,r) for a in cfgs for i in queries for r in ('rep1','rep2','rep3')}
    seen=set();calls=0
    for c in cells:
        k=(c['request_sha256'],c['replicate_id']);assert c['provider_call']==(k not in seen);calls+=c['provider_call'];seen.add(k)
    assert calls==plan['calls']['planned_provider_calls']<=plan['authorization']['authorized_generation_max']
    assert plan['retries']['attempts_per_cell_max']==3 and plan['parameters']['sdk_max_retries']==0 and plan['parameters']['temperature']==0
    for part in ('layer3','layer4'):
        for k,v in ev[part].items():
            if k.endswith('_sha256') and k[:-7] in ev[part]:assert sha(ROOT/ev[part][k[:-7]])==v,(part,k)
    return dict(configurations=cfgs,request_inputs=len(reqs),cells=len(cells),planned_provider_calls=calls,max_request_bytes=max(q['request_utf8_bytes'] for q in reqs),judge_call_cap=ev['judging']['judge_call_cap'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--target',type=Path,required=True);a=p.parse_args()
    if a.target.exists():raise FileExistsError(a.target)
    c=counter();views=load(E1/'source-views-prepared.json');parents=load(E1/'public-parent-graph.json')
    out=dict(inputs=check_inputs());print('inputs ok',flush=True)
    out['m1_index']=check_m1_index(c,views);print('index ok',flush=True)
    out['rankings']=check_rankings();out['contexts']=check_contexts(c,views,parents);print('contexts ok',flush=True)
    out['scores']=recompute_scores(a.revision);out['m0_parity_r11']=m0_parity('r11');print('scores ok',flush=True)
    out['e5']=check_e5(a.revision);out['status']='passed';out['generation_calls']=0;out['judge_calls']=0
    save_json(a.target,out);print('verification passed',flush=True)

if __name__=='__main__':main()
