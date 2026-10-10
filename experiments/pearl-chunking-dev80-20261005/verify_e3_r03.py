"""Reopen E3 files: source text, serialized tokens, ranking, dedup and score parity."""
import argparse
import json
import random
import statistics
from runtime import ROOT, sha, save_json, save_rows
from e3 import rows, load, SOURCE, CONFIGS, STAGES, PANELS
from smoke import counter
from assemble import serialize, digest, key, unit, views_by_id, _expand
from e1_visible_review_verify import intervals, all_inside

def verify(output):
    c=counter();views=load(SOURCE/'source-views-prepared.json')
    elements={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']}
    checked=0;cache={};profile=[];same={};p0=0;sample=[]
    runtime=load(output/'runtime-r01.json')
    for name,h in runtime['code_sha256'].items():assert sha(ROOT/name)==h
    assert sha(SOURCE/'source-views-prepared.json')==runtime['source_views_sha256']
    assert sha(SOURCE/'public-parent-graph.json')==runtime['parent_sha256']
    assert sha(ROOT/'memPed/knowledge/models/bge-m3/tokenizer.json')==runtime['tokenizer_sha256']
    assert c.fingerprint==runtime['tokenizer_fingerprint']
    parents=load(SOURCE/'public-parent-graph.json');vs=views_by_id(views)
    for config in CONFIGS:
        rp=SOURCE/('index-'+config)/'rankings.jsonl';assert sha(rp)==runtime['ranking_inputs'][config]
        rankings={r['intent_id']:r for r in rows(rp)}
        old={(r['intent_id'],r['budget']):r for r in rows(SOURCE/('index-'+config)/'contexts.jsonl')}
        for path in sorted(output.glob('contexts-'+config+'-*.jsonl')):
            counts=[];duplicates=[];sources=[];amp=[];saved=list(rows(path));assert len(saved)==80
            for ctx in saved:
                identity=(config,ctx['intent_id'],ctx['panel_id']);n=10 if ctx['panel_id']=='seed10_diagnostic' else 100
                rank=rankings[ctx['intent_id']]['results']['R4'][:n]
                assert ctx['ranking_sha256']==digest(rank) and ctx['ranking_file_sha256']==sha(rp)
                expected_raw=[unit(ch['core_spans']+ch.get('overlap_spans',[]),vs,ch['chunk_id'],j) for j,ch in enumerate(rank,1)]
                expected_expanded=[unit(_expand(ch,vs,parents,ctx['strategy']),vs,ch['chunk_id'],j) for j,ch in enumerate(rank,1)]
                assert ctx['raw']['units']==expected_raw and ctx['expanded']['units']==expected_expanded
                same.setdefault(identity,set()).add(ctx['ranking_sha256'])
                for stage in STAGES:
                    snapshot=ctx[stage];rendered=serialize(snapshot['units'])
                    assert rendered==snapshot['serialized_context'] and digest(rendered)==snapshot['text_sha256']
                    if snapshot['text_sha256'] not in cache:cache[snapshot['text_sha256']]=c.count(rendered)
                    assert cache[snapshot['text_sha256']]==snapshot['token_count']
                    for u in snapshot['units']:
                        assert digest(u['text'])==u['text_sha256']
                        rebuilt=unit(u['spans'],vs,u['seed_chunk_id'],u['rank'])
                        assert all(rebuilt[k]==u[k] for k in ('spans','text','parts','text_sha256'))
                        for part in u['parts']:
                            s=part['span'];assert u['text'][part['text_start']:part['text_end']]==elements[key(s)][s['start']:s['end']]
                assert ctx['final']['token_count']<=ctx['budget']
                expanded=[s for u in ctx['expanded']['units'] for s in u['spans']]
                ds=[s for u in ctx['deduplicated']['units'] for s in u['spans']]
                total=lambda ss:sum(s['end']-s['start'] for s in ss)
                iv=intervals(ds);merged=sum(b-a for values in iv.values() for a,b in values)
                assert total(ds)==merged and intervals(expanded)==iv
                final=[s for u in ctx['final']['units'] for s in u['spans']]
                assert all_inside(final,iv)
                if ctx['strategy']=='P0' and ctx['panel_id']=='fixed_budget_main':
                    original=old[ctx['intent_id'],ctx['budget']]
                    assert all(ctx[s]==original[s] for s in STAGES);p0+=1
                counts.append(ctx['final']['token_count']);duplicates.append(1-merged/total(expanded) if expanded else 0)
                sources.append(len({(s['doc_id'],s['source_version']) for s in final}))
                amp.append(ctx['expanded']['token_count']/ctx['raw']['token_count'] if ctx['raw']['token_count'] else 0)
                checked+=1
                sample.append(dict(configuration_id=config,intent_id=ctx['intent_id'],panel_id=ctx['panel_id'],strategy=ctx['strategy'],budget=ctx['budget'],context_id=ctx['context_id'],file=path.relative_to(ROOT).as_posix()))
            print('source/token cell verified',path.name,checked,flush=True)
            first=saved[0]
            profile.append(dict(configuration_id=config,strategy=first['strategy'],budget=first['budget'],panel_id=first['panel_id'],n=80,mean_final_tokens=statistics.mean(counts),min_final_tokens=min(counts),max_final_tokens=max(counts),mean_final_sources=statistics.mean(sources),mean_expanded_source_duplicate_fraction=statistics.mean(duplicates),mean_serialized_expansion_ratio=statistics.mean(amp)))
    assert checked==2880 and p0==480 and len(same)==480 and all(len(s)==1 for s in same.values())
    rng=random.Random(20261005);audit=[]
    # Fixed sample from all 36 cells. All source text and offsets are checked above;
    # the retained prefix maximality additionally uses the original single-call search.
    from e1_batch import truncate_batch as truncate_with_offsets
    vs=views_by_id(views)
    for path in sorted(output.glob('contexts-*.jsonl')):
        saved=list(rows(path));ctx=rng.choice(saved)
        if ctx['truncation']:
            stop=ctx['truncation'][0];u=next(x for x in ctx['deduplicated']['units'] if x['seed_chunk_id']==stop['seed_chunk_id'])
            kept=[x for x in ctx['final']['units'] if x['rank']<u['rank']]
            value,trace=truncate_with_offsets(u,kept,vs,ctx['budget'],c)
            actual=next((x for x in ctx['final']['units'] if x['rank']==u['rank']),None)
            assert value==actual and trace['retained_characters']==stop['retained_characters']
            audit.append(dict(context_id=ctx['context_id'],retained_characters=trace['retained_characters'],status='passed'))
            print('maximal prefix verified',path.name,flush=True)
    save_json(output/'assembly-verification-r01.json',dict(status='passed',contexts_checked=checked,ranking_identity_groups=len(same),p0_frozen_context_parity=p0,unique_serializations_recounted=len(cache),source_text_and_offsets='all four stages of all contexts',dedup='source interval union equality and no duplicate character; all contexts',maximal_prefix_reference='frozen e1_batch equivalent descending exhaustive Unicode source search with native batch counts; fixed seed one context per cell, public single-counter recheck at fit',maximal_prefix_checks=audit,seed=20261005,retrieval_calls=0,verifier_revision='r03',verification_code_sha256=sha(__file__)))
    save_json(output/'context-profiles-e3-r01.json',dict(cells=profile))
    print('passed',checked,'contexts;',len(audit),'batched-equivalent exhaustive maximal-prefix checks',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=__import__('pathlib').Path,required=True);a=p.parse_args();verify(a.output.resolve())
