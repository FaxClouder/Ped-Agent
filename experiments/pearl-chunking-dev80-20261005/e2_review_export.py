"""Export blind E2 supplement-review packets for unknowns that can change the overlap choice.

Scope: competitor arms (O10/O20) on the 4K Top100 main panel (selection key) plus the
seed10 raw stage (CEGR@10 tie-break) where they are unknown under r10. For each
(intent, requirement) the packet holds the query, requirement text, the existing
reviewed alternatives, the unadjudicated uncertain passages actually visible, and every
actually visible segment outside the r10 reviewed universe (union over the cells).
Configuration identity, scores and cell membership are hidden from the reviewer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from runtime import ROOT, sha, save_json
from assemble import union_spans, subtract_spans, key
from e1_visible_review_verify import intervals, part_of, all_inside
import e3_scope_revision as rev

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
E0=ROOT/'outputs/pearl-chunking-dev80-20261005-03'

def load(p):return json.loads(Path(p).read_text('utf8'))
def rows(p):
    with Path(p).open(encoding='utf8') as f:return [json.loads(l) for l in f if l.strip()]

def main():
    p=argparse.ArgumentParser();p.add_argument('--revision',default='r10');p.add_argument('--tag',default='r11');a=p.parse_args()
    target=OUT/f'review-packets-e2-{a.tag}';target.mkdir(exist_ok=False)
    scores=load(OUT/f'scores-e2-{a.revision}.json');mp=ROOT/scores['mapping_path'];maps={r['intent_id']:r for r in load(mp)['records']}
    views=load(E0/'source-views-prepared.json');text={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']}
    cells={}
    for r in rows(OUT/f'score-details-e2-{a.revision}.jsonl'):
        if '-O0-' in r['configuration_id']:continue
        main=r['budget']==4096 and r['panel_id']=='fixed_budget_main' and r['stage']=='final'
        cegr=r['panel_id']=='seed10_diagnostic' and r['stage']=='raw' and r['budget']==4096
        if (main or cegr) and r['sufficient']=='unknown':
            for rid,s in r['support'].items():
                if s=='unknown':cells.setdefault((r['intent_id'],rid),[]).append((r['configuration_id'],r['budget'],r['panel_id'],r['stage'],r['contexts_file_sha256']))
    ctx={}
    def visible(config,B,panel,stage,intent):
        path=OUT/f'contexts-{config}-P0-{B}-{panel}.jsonl'
        if path not in ctx:ctx[path]={c['intent_id']:c for c in rows(path)}
        return [s for u in ctx[path][intent][stage]['units'] for s in u['spans']]
    index=[]
    for n,((intent,rid),cs) in enumerate(sorted(cells.items()),1):
        m=maps[intent];q=next(x for x in m['requirements'] if x['requirement_id']==rid);vr=rev.active_requirement(q).get('visible_universe_review') or {}
        vis=union_spans([s for c in cs for s in visible(c[0],c[1],c[2],c[3],intent)])
        outside=subtract_spans(vis,vr.get('universe_spans',[])) if vr else vis
        def seg(s):return dict(span=s,text=text[key(s)][s['start']:s['end']])
        unc=[]
        for i,u in enumerate(vr.get('uncertain',[])):
            part=part_of(u['source_spans'],intervals(vis))
            if not part:continue
            # Same blocking condition as req_status: unadjudicated, or the visible portion is
            # not covered by any does_not_support variant (supports variants would already give yes).
            variants=u.get('adjudicated_variants')
            if variants is not None and any(v['verdict']=='does_not_support' and all_inside(part,intervals(v['source_spans'])) for v in variants):continue
            unc.append(dict(index=i,visible_portion=[seg(s) for s in part],full_passage=[seg(s) for s in u['source_spans']],note=u.get('rationale') or u.get('reason'),
                            prior_variants=[dict(verdict=v['verdict'],rationale=v.get('rationale'),text=[seg(s)['text'] for s in v['source_spans']]) for v in variants or []]))
        packet=dict(packet_id=f'E2P{n:03d}',intent_id=intent,requirement_id=rid,query=m['query'],requirement=q['description'],scope=q.get('scope'),
                    universe_status=vr.get('universe_status'),has_visible_universe_review=bool(vr),
                    existing_alternatives=[dict(index=i,rationale=x.get('rationale'),text=[seg(s)['text'] for s in x['source_spans']]) for i,x in enumerate(vr.get('alternatives',[]))],
                    uncertain_visible=unc,outside_segments=[seg(s) for s in sorted(outside,key=lambda s:(key(s),s['start']))],
                    instructions='Judge only this requirement within its scope. For the outside segments (and the visible portion of any uncertain passage), decide: (a) a complete minimal supporting alternative exists in the visible text -> give its exact spans; (b) exhaustively read, no support -> extend reviewed universe with these segments; (c) ambiguous -> keep unknown. Do not use outside knowledge.')
        packet['packet_sha256']=hashlib.sha256(json.dumps(packet,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        path=target/f'{packet["packet_id"]}.json';save_json(path,packet)
        index.append(dict(packet_id=packet['packet_id'],intent_id=intent,requirement_id=rid,packet_file_sha256=sha(path),packet_sha256=packet['packet_sha256'],cells=[dict(configuration_id=c[0],budget=c[1],panel_id=c[2],stage=c[3]) for c in cs],outside_chars=sum(len(s['text']) for s in packet['outside_segments']),uncertain_visible=len(unc)))
    save_json(OUT/f'review-export-e2-{a.tag}.json',dict(base_revision=a.revision,base_mapping_sha256=sha(mp),scores_sha256=sha(OUT/f'scores-e2-{a.revision}.json'),details_sha256=sha(OUT/f'score-details-e2-{a.revision}.jsonl'),scope='competitor O10/O20 unknown requirements on 4K Top100 final (selection key) and 4K seed10 raw (CEGR@10)',blind_fields_hidden=['configuration_id','cell membership','scores'],exporter_sha256=sha(__file__),packets=index))
    print(len(index),'packets;',sum(i['outside_chars'] for i in index),'outside chars;',sum(i['uncertain_visible'] for i in index),'uncertain passages',flush=True)

if __name__=='__main__':main()
