"""Session 3B: blind review of actual visible E1 evidence universes and r06 rescoring.

Offline only: no index build, retrieval, assembly, generation or remote judge.
Certificate-based r05 semantics are kept; a requirement whose certificate is
not fully visible is resolved only from an explicit blind review of the union of
actual visible text ("universe") across the E1 selection cells of that intent:
  yes      - a reviewed minimal supporting alternative is fully visible;
  unknown  - reviewer left the universe unresolved, or an uncertain passage is
             (partly) visible, or visible text lies outside the reviewed universe;
  no       - all visible text lies inside the reviewed universe and none of the
             reviewed alternatives is fully visible.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import statistics
from runtime import sha, cache_identity, save_json, save_rows, load_queries
from assemble import union_spans, subtract_spans, key
from support import visible_support
from score import score_support, aggregate
from e1 import configurations
from e1_score import rows, candidate_decision, select_equivalent_representatives, execution_row

VERSION='e1-visible-universe-review-r06'
SELECTION_CELLS=('fixed_budget_main/P0/4096/final','layer1_raw/R4/10')
REVIEW_STATUSES=('yes','no','unknown')

def load(p):return json.loads(Path(p).read_text('utf8'))

def overlaps(spans,visible):
    return any(key(s)==key(v) and min(s['end'],v['end'])>max(s['start'],v['start']) for s in spans for v in visible)

def contained(spans,visible):
    return bool(spans) and not subtract_spans(spans,visible)

def portion(spans,visible):
    """Characters of spans that are visible (merged source spans)."""
    out=[]
    for s in union_spans(spans):
        for v in visible:
            if key(s)==key(v):
                a,b=max(s['start'],v['start']),min(s['end'],v['end'])
                if a<b:out.append(dict(s,start=a,end=b))
    return union_spans(out) if out else []

def uncertain_blocks(item,visible):
    part=portion(item['source_spans'],visible)
    if not part:return False
    if 'adjudicated_variants' not in item:return True
    return not any(v['verdict']=='does_not_support' and contained(part,v['source_spans']) for v in item['adjudicated_variants'])

def requirement_basis(requirement,certificate_status,visible):
    """Return (status, basis) for one requirement given certificate status and visible spans."""
    review=requirement.get('visible_universe_review')
    if certificate_status!='unknown' or review is None:return certificate_status,'certificate'
    if any(contained(a['source_spans'],visible) for a in review['alternatives']):return 'yes','reviewed_visible_alternative'
    if any(v['verdict']=='supports' and contained(v['source_spans'],visible) for u in review['uncertain'] for v in u.get('adjudicated_variants',[])):return 'yes','adjudicated_visible_variant'
    adjudicated=bool(review['uncertain']) and all('adjudicated_variants' in u for u in review['uncertain'])
    if review['universe_status']=='unknown' and not adjudicated:return 'unknown','reviewed_universe_unresolved'
    if any(uncertain_blocks(u,visible) for u in review['uncertain']):return 'unknown','reviewed_uncertain_passage_visible'
    if not subtract_spans(visible,review['universe_spans']):return 'no','reviewed_universe_without_visible_alternative'
    return 'unknown','visible_text_outside_reviewed_universe'

def support_r06(visible_spans,mapping):
    visible=union_spans(visible_spans) if visible_spans else []
    base=visible_support(visible_spans,mapping)
    support={};basis={}
    for req in mapping['requirements']:
        rid=req['requirement_id'];support[rid],basis[rid]=requirement_basis(req,base[rid],visible)
    return support,basis,base

def prefix_metrics_r06(ranked,mapping,k):
    prefix=[];states=[];first_yes=first_possible=None
    for rank,child in enumerate(ranked[:k],1):
        prefix+=child['core_spans']+child.get('overlap_spans',[])
        support,basis,_=support_r06(prefix,mapping);values=score_support(mapping['groups'],support)
        states.append(dict(rank=rank,support=support,support_basis=basis,**values))
        if values['sufficient']=='yes' and first_yes is None:first_yes=rank
        if values['sufficient']!='no' and first_possible is None:first_possible=rank
    if not states:
        support={r['requirement_id']:'no' for r in mapping['requirements']}
        final=dict(support=support,support_basis={r:'empty_ranking' for r in support},**score_support(mapping['groups'],support))
    else:final=states[-1]
    return dict(support=final['support'],support_basis=final['support_basis'],**{k2:final[k2] for k2 in final if k2 not in ('rank','support','support_basis')},complete_rr_lower=1/first_yes if first_yes else 0.,complete_rr_upper=1/first_possible if first_possible else 0.,prefix_evidence=states)

# ---------------------------------------------------------------- export
def export(source_run,output):
    output.mkdir(parents=False,exist_ok=True)
    if (output/'visible-universe-export-r06.json').exists():raise FileExistsError('export already exists')
    map_path=source_run/'common-support-map-e1-r05.json';unknown_path=source_run/'unknown-evidence-e1-r01.jsonl';views_path=source_run/'source-views-prepared.json'
    mapping=load(map_path);records={r['intent_id']:r for r in mapping['records']}
    unknown=[r for r in rows(unknown_path) if r['cell'] in SELECTION_CELLS]
    if any(r['mapping_sha256']!=sha(map_path) for r in unknown):raise ValueError('unknown evidence/map r05 binding drift')
    views=load(views_path);docs={(v['doc_id'],v['source_version']):v for v in views}
    elements={(v['doc_id'],v['source_version'],e['element_id']):(i,e) for v in views for i,e in enumerate(v['elements'])}
    by_intent={}
    for r in unknown:by_intent.setdefault(r['intent_id'],[]).append(r)
    pdir=output/'visible-universe-packets-r06';pdir.mkdir()
    index=[]
    for intent,cells in sorted(by_intent.items()):
        raw=[s for c in cells for s in c['visible_spans']];universe=union_spans(raw)
        gap_ids=sorted({g['requirement_id'] for c in cells for g in c['certificate_gaps']})
        rec=records[intent]
        doc_ids=sorted({(s['doc_id'],s['source_version']) for s in universe});labels={d:f'D{i+1}' for i,d in enumerate(doc_ids)}
        ordered=sorted(universe,key=lambda s:(labels[(s['doc_id'],s['source_version'])],elements[key(s)][0],s['start']))
        segments=[];bindings=[]
        for n,s in enumerate(ordered,1):
            order,e=elements[key(s)];text=e['text'][s['start']:s['end']]
            cuts=sorted({x-s['start'] for v in raw if key(v)==key(s) for x in (v['start'],v['end']) if s['start']<x<s['end']})
            seg=dict(segment_id=f'S{n}',document=labels[(s['doc_id'],s['source_version'])],element_type=e.get('element_type'),heading_path=e.get('heading_path'),page_number=e.get('page_number'),element_text_complete=s['start']==0 and s['end']==len(e['text']),text=text,cut_points=cuts,cut_previews=[dict(offset=x,before=text[max(0,x-60):x],after=text[x:x+60]) for x in cuts])
            segments.append(seg);bindings.append(dict(segment_id=seg['segment_id'],span=s,text_sha256=cache_identity(text)))
        requirements=[]
        for req in rec['requirements']:
            if req['requirement_id'] not in gap_ids:continue
            refs=[dict(alternative_index=i,passages=[docs[(s['doc_id'],s['source_version'])]['title']+' :: '+elements[key(s)][1]['text'][s['start']:s['end']] for s in g['necessary_spans']]) for i,g in enumerate(req['evidence_groups']) if g['status']=='yes']
            requirements.append(dict(requirement_id=req['requirement_id'],description=req['description'],scope=req.get('scope'),reference_evidence=refs))
        packet=dict(schema_version=VERSION+'-packet',intent_id=intent,query=rec['query'],requirements=requirements,documents=[dict(document=labels[d],title=docs[d]['title']) for d in doc_ids],segments=segments)
        packet['packet_sha256']=cache_identity(packet)
        path=pdir/f'{intent}.json';save_json(path,packet)
        index.append(dict(intent_id=intent,packet_file=path.name,packet_file_sha256=sha(path),packet_sha256=packet['packet_sha256'],requirement_ids=[r['requirement_id'] for r in requirements],universe_spans=universe,segment_bindings=bindings,characters=sum(len(s['text']) for s in segments),source_cells=sorted((c['configuration_id'],c['cell']) for c in cells)))
    save_json(output/'visible-universe-export-r06.json',dict(schema_version=VERSION+'-export',status='exported',source_run=source_run.name,inputs_sha256={map_path.name:sha(map_path),unknown_path.name:sha(unknown_path),views_path.name:sha(views_path)},selection_cells=list(SELECTION_CELLS),blind_fields_hidden=['configuration_id','rank','ranking/context identity','scores','which cell saw which segment'],intents=len(index),requirements=sum(len(i['requirement_ids']) for i in index),characters=sum(i['characters'] for i in index),packets=index))
    print('exported',len(index),'visible-universe packets',flush=True)

# --------------------------------------------------- render / normalize
CUT='\u27e6|\u27e7'

def render(source_run,output):
    """Deterministic reviewer view of each packet; cut markers are display-only."""
    exported=load(output/'visible-universe-export-r06.json');vdir=output/'visible-universe-review-views-r06';vdir.mkdir()
    views=load(source_run/'source-views-prepared.json');lengths={(v['doc_id'],v['source_version'],e['element_id']):len(e['text']) for v in views for e in v['elements']}
    receipt=[]
    for entry in exported['packets']:
        ppath=output/'visible-universe-packets-r06'/entry['packet_file']
        if sha(ppath)!=entry['packet_file_sha256']:raise ValueError('packet file drift')
        p=load(ppath);b={x['segment_id']:x['span'] for x in entry['segment_bindings']}
        lines=[f"# Visible evidence universe: {p['intent_id']}",'',f"packet_sha256: {p['packet_sha256']}",'',f"Query: {p['query']}",'','## Requirements to judge','']
        for r in p['requirements']:
            lines+= [f"### {r['requirement_id']}: {r['description']}",f"Scope: {r['scope']}",'','Reference evidence from the source paper (Gold reference; it may be absent or only partly present in the visible segments below; judge ONLY visible text):']
            for ref in r['reference_evidence']:
                for t in ref['passages']:lines.append(f"- {t}")
            lines.append('')
        lines+=['## Documents','']+[f"- {d['document']}: {d['title']}" for d in p['documents']]+['','## Visible segments','',f"Display marker {CUT} = a place where some actual visible context starts or ends. It is NOT part of the text; never include it in quotes.",'']
        for seg in p['segments']:
            span=b[seg['segment_id']];n=lengths[key(span)];t=seg['text']
            shown=''.join(t[i:j]+(CUT if j<len(t) else '') for i,j in zip([0]+seg['cut_points'],seg['cut_points']+[len(t)]))
            lines+=[f"### {seg['segment_id']} | {seg['document']} | {seg['element_type']} | page {seg['page_number']} | heading {seg['heading_path']} | element chars {span['start']}-{span['end']} of {n}"+(' | starts mid-element' if span['start']>0 else '')+(' | ends mid-element' if span['end']<n else ''),'',shown,'']
        path=vdir/(p['intent_id']+'.md')
        with path.open('x',encoding='utf8',newline='\n') as f:f.write('\n'.join(lines))
        receipt.append(dict(intent_id=p['intent_id'],view_file=path.name,view_sha256=sha(path),packet_sha256=p['packet_sha256'],characters=len('\n'.join(lines))))
    save_json(output/'visible-universe-review-views-r06.json',dict(status='rendered',views=receipt,marker=CUT,note='Display view of packets; reviewer quotes are re-bound to raw packet text by normalize.'))
    print('rendered',len(receipt),flush=True)

def normalize(output):
    """Bind reviewer literal quotes to packet segment offsets; fail on absent/ambiguous quotes."""
    exported=load(output/'visible-universe-export-r06.json');raw_dir=output/'visible-universe-reviews-raw-r06';out_dir=output/'visible-universe-reviews-r06';out_dir.mkdir()
    receipt=[]
    for entry in exported['packets']:
        p=load(output/'visible-universe-packets-r06'/entry['packet_file']);segs={s['segment_id']:s['text'] for s in p['segments']}
        rpath=raw_dir/entry['packet_file'];r=load(rpath)
        for j in r.get('requirements',[]):
            for x in j.get('alternatives',[])+j.get('uncertain',[]):
                for s in x.get('spans',[]):
                    text=segs.get(s.get('segment_id'))
                    if text is None:raise ValueError(f"{p['intent_id']}: unknown segment {s.get('segment_id')}")
                    q=s['quote'].replace(CUT,'');hits=[];i=text.find(q)
                    while q and i>=0:hits.append(i);i=text.find(q,i+1)
                    occ=s.get('occurrence')
                    if not hits:raise ValueError(f"{p['intent_id']}/{s['segment_id']}: quote not literal: {q[:80]!r}")
                    if len(hits)>1 and not occ:raise ValueError(f"{p['intent_id']}/{s['segment_id']}: ambiguous quote")
                    start=hits[(occ or 1)-1];s.update(quote=q,start=start,end=start+len(q))
        save_json(out_dir/entry['packet_file'],r);receipt.append(dict(intent_id=p['intent_id'],raw_sha256=sha(rpath),normalized_sha256=sha(out_dir/entry['packet_file'])))
    save_json(output/'visible-universe-normalization-r06.json',dict(status='passed',reviews=receipt))
    print('normalized',len(receipt),flush=True)

# ------------------------------------------------------------ integrate
def _source_spans(spans,segments,bindings):
    out=[]
    for s in spans:
        seg=segments.get(s.get('segment_id'))
        if seg is None:raise ValueError('review cites unknown segment')
        a,b=s.get('start'),s.get('end')
        if not isinstance(a,int) or not isinstance(b,int) or not 0<=a<b<=len(seg['text']):raise ValueError('review span outside segment')
        if seg['text'][a:b]!=s.get('quote'):raise ValueError('review quote is not literal visible text')
        base=bindings[s['segment_id']]['span'];out.append(dict(base,start=base['start']+a,end=base['start']+b))
    return union_spans(out)

def validate_review(packet,entry,review):
    if review.get('packet_sha256')!=packet['packet_sha256'] or review.get('intent_id')!=packet['intent_id']:raise ValueError('review packet binding drift')
    if not review.get('reviewer_id'):raise ValueError('explicit reviewer required')
    segments={s['segment_id']:s for s in packet['segments']};bindings={b['segment_id']:b for b in entry['segment_bindings']}
    judged={j.get('requirement_id'):j for j in review.get('requirements',[])}
    if len(judged)!=len(review.get('requirements',[])) or set(judged)!=set(entry['requirement_ids']):raise ValueError('complete requirement judgment set required')
    result={}
    for rid,j in judged.items():
        status=j.get('universe_status');alts=j.get('alternatives',[]);unc=j.get('uncertain',[])
        if status not in REVIEW_STATUSES or not j.get('rationale') or j.get('exhaustive') is not True:raise ValueError('three-valued status, rationale and exhaustive declaration required')
        if status=='yes' and not alts:raise ValueError('yes requires a visible alternative')
        if status=='no' and (alts or unc):raise ValueError('no cannot list support or uncertain passages')
        if status=='unknown' and alts:raise ValueError('listed alternatives make the universe yes; uncertain passages go in uncertain')
        for x in alts+unc:
            if not x.get('spans') or not x.get('rationale'):raise ValueError('alternative/uncertain passage needs spans and rationale')
        result[rid]=dict(universe_status=status,rationale=j['rationale'],exhaustive=True,
            alternatives=[dict(source_spans=_source_spans(a['spans'],segments,bindings),review_spans=a['spans'],rationale=a['rationale']) for a in alts],
            uncertain=[dict(source_spans=_source_spans(u['spans'],segments,bindings),review_spans=u['spans'],rationale=u['rationale']) for u in unc],
            caveats=j.get('caveats',[]),reviewer_id=review['reviewer_id'],packet_sha256=packet['packet_sha256'],universe_spans=entry['universe_spans'])
    return result

def integrate(source_run,output):
    export_path=output/'visible-universe-export-r06.json';exported=load(export_path)
    map_path=source_run/'common-support-map-e1-r05.json'
    if exported['inputs_sha256'][map_path.name]!=sha(map_path):raise ValueError('map r05 drift since export')
    base=load(map_path);records={r['intent_id']:r for r in base['records']}
    rdir=output/'visible-universe-reviews-r06';bindings={};flags=[];counts={s:0 for s in REVIEW_STATUSES};reviewers=set()
    for entry in exported['packets']:
        ppath=output/'visible-universe-packets-r06'/entry['packet_file']
        if sha(ppath)!=entry['packet_file_sha256']:raise ValueError('packet file drift')
        packet=load(ppath)
        if cache_identity({k:v for k,v in packet.items() if k!='packet_sha256'})!=packet['packet_sha256']:raise ValueError('packet content drift')
        rpath=rdir/entry['packet_file'];review=load(rpath)
        judged=validate_review(packet,entry,review);bindings[rpath.name]=sha(rpath);reviewers.add(review['reviewer_id'])
        for req in records[entry['intent_id']]['requirements']:
            j=judged.get(req['requirement_id'])
            if j is None:continue
            counts[j['universe_status']]+=1;req['visible_universe_review']=j
            for gi,g in enumerate(req['evidence_groups']):
                if g['status']=='yes' and contained(g['necessary_spans'],entry['universe_spans']) and j['universe_status']!='yes':
                    flags.append(dict(intent_id=entry['intent_id'],requirement_id=req['requirement_id'],evidence_group=gi,issue='full r05 certificate lies inside universe but review is not yes'))
    if flags:
        adj=output/'visible-universe-adjudication-r06.json'
        if not adj.exists():save_json(output/'visible-universe-integration-flags-r06.json',dict(status='blocked_needs_adjudication',flags=flags));raise ValueError('certificate/review disagreement requires recorded adjudication')
    base.update(schema_version='e1-common-source-support-r06',previous_map_sha256=sha(map_path),visible_universe_export_sha256=sha(export_path),visible_universe_review_bindings=bindings,visible_universe_semantics=__doc__,legacy_chunk_labels_inherited=False,visible_universe_reviewers=sorted(reviewers))
    base.pop('map_sha256',None);base['map_sha256']=cache_identity(base)
    out_map=output/'common-support-map-e1-r06.json';save_json(out_map,base)
    save_json(output/'visible-universe-integration-r06.json',dict(status='passed',intents=len(exported['packets']),requirement_judgments=sum(counts.values()),universe_status_counts=counts,certificate_consistency_flags=flags,reviewers=sorted(reviewers),map_sha256=sha(out_map),review_bindings=bindings,export_sha256=sha(export_path)))
    print('integrated',len(exported['packets']),'reviews',counts,flush=True)

# ------------------------------------------------- r07 targeted adjudication
ADJ_VERDICTS=('supports','does_not_support','uncertain')

def adjudication_export(source_run,output):
    """Export, blind to configuration, every exact visible portion of an r06 uncertain passage that keeps a
    selection cell unknown; one adjudication item per distinct portion."""
    map_path=output/'common-support-map-e1-r06.json';rem_path=output/'unknown-remaining-e1-r06.jsonl';ev_path=source_run/'unknown-evidence-e1-r01.jsonl';views_path=source_run/'source-views-prepared.json'
    mapping=load(map_path);reqs={(r['intent_id'],q['requirement_id']):(r,q) for r in mapping['records'] for q in r['requirements']}
    evidence={(r['configuration_id'],r['cell'],r['intent_id']):r['visible_spans'] for r in rows(ev_path) if r['cell'] in SELECTION_CELLS}
    views=load(views_path);text={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in views for e in v['elements']};titles={(v['doc_id'],v['source_version']):v['title'] for v in views}
    variants={}
    for cell in rows(rem_path):
        visible=union_spans(evidence[(cell['configuration_id'],cell['cell'],cell['intent_id'])])
        for rid,status in cell['support'].items():
            if status!='unknown' or cell['support_basis'].get(rid) not in ('reviewed_uncertain_passage_visible','reviewed_universe_unresolved'):continue
            rec,req=reqs[(cell['intent_id'],rid)]
            for ui,u in enumerate(req['visible_universe_review']['uncertain']):
                part=portion(u['source_spans'],visible)
                if part:variants.setdefault((cell['intent_id'],rid,ui),{}).setdefault(cache_identity(part),part)
    adir=output/'adjudication-packets-r07';adir.mkdir()
    index=[]
    for intent in sorted({k[0] for k in variants}):
        rec=next(r for r in mapping['records'] if r['intent_id']==intent);items=[];lines=[f'# Targeted adjudication: {intent}','',f"Query: {rec['query']}",'']
        for (i,rid,ui),parts in sorted((k,v) for k,v in variants.items() if k[0]==intent):
            _,req=reqs[(i,rid)];u=req['visible_universe_review']['uncertain'][ui]
            full=[dict(document=titles[(s['doc_id'],s['source_version'])],text=text[key(s)][s['start']:s['end']]) for s in u['source_spans']]
            for n,(h,part) in enumerate(sorted(parts.items(),key=lambda x:json.dumps(x[1],sort_keys=True)),1):
                vid=f'{rid}-u{ui+1}-v{n}'
                shown=[dict(document=titles[(s['doc_id'],s['source_version'])],text=text[key(s)][s['start']:s['end']]) for s in part]
                items.append(dict(variant_id=vid,requirement_id=rid,uncertain_index=ui,source_spans=part,full_passage=full,visible_portion=shown,first_reviewer_concern=u['rationale']))
        reqs_out=[]
        for rid in sorted({x['requirement_id'] for x in items}):
            _,req=reqs[(intent,rid)]
            refs=[text[key(s)][s['start']:s['end']] for g in req['evidence_groups'] for s in g['necessary_spans']]
            reqs_out.append(dict(requirement_id=rid,description=req['description'],scope=req.get('scope'),reference_evidence=refs))
            lines+=[f"## {rid}: {req['description']}",f"Scope: {req.get('scope')}",'','Reference evidence from the source paper (for understanding the claim only):']+[f'- {t}' for t in refs]+['']
            for x in (y for y in items if y['requirement_id']==rid):
                lines+=[f"### Item {x['variant_id']}",'First reviewer\'s concern: '+x['first_reviewer_concern'],'','Full passage (context only):']+[f"- [{p['document']}] {p['text']}" for p in x['full_passage']]+['','VISIBLE PORTION TO JUDGE (exactly what a reader sees of this passage):']+[f"- [{p['document']}] {p['text']}" for p in x['visible_portion']]+['']
        packet=dict(schema_version='e1-targeted-adjudication-r07-packet',intent_id=intent,query=rec['query'],requirements=reqs_out,items=items)
        packet['packet_sha256']=cache_identity(packet);lines.insert(2,f"packet_sha256: {packet['packet_sha256']}")
        path=adir/f'{intent}.json';save_json(path,packet)
        md=adir/f'{intent}.md'
        with md.open('x',encoding='utf8',newline='\n') as f:f.write('\n'.join(lines))
        index.append(dict(intent_id=intent,packet_file=path.name,packet_file_sha256=sha(path),view_file=md.name,view_sha256=sha(md),packet_sha256=packet['packet_sha256'],items=len(items)))
    save_json(output/'adjudication-export-r07.json',dict(status='exported',inputs_sha256={map_path.name:sha(map_path),rem_path.name:sha(rem_path),ev_path.name:sha(ev_path)},intents=len(index),items=sum(i['items'] for i in index),packets=index,blind_fields_hidden=['configuration_id','cell','scores']))
    print('exported adjudication',len(index),'intents',sum(i['items'] for i in index),'items',flush=True)

def adjudication_integrate(output):
    exported=load(output/'adjudication-export-r07.json');map_path=output/'common-support-map-e1-r06.json'
    if exported['inputs_sha256'][map_path.name]!=sha(map_path):raise ValueError('r06 map drift since adjudication export')
    base=load(map_path);reqs={(r['intent_id'],q['requirement_id']):q for r in base['records'] for q in r['requirements']}
    bindings={};counts={v:0 for v in ADJ_VERDICTS};reviewers=set()
    for entry in exported['packets']:
        p=load(output/'adjudication-packets-r07'/entry['packet_file'])
        if sha(output/'adjudication-packets-r07'/entry['packet_file'])!=entry['packet_file_sha256'] or cache_identity({k:v for k,v in p.items() if k!='packet_sha256'})!=p['packet_sha256']:raise ValueError('adjudication packet drift')
        rpath=output/'adjudication-reviews-r07'/entry['packet_file'];r=load(rpath)
        if r.get('packet_sha256')!=p['packet_sha256'] or r.get('intent_id')!=p['intent_id'] or not r.get('reviewer_id'):raise ValueError('adjudication binding')
        judged={j['variant_id']:j for j in r['judgments']}
        if len(judged)!=len(r['judgments']) or set(judged)!={x['variant_id'] for x in p['items']}:raise ValueError('complete adjudication set required')
        for x in p['items']:
            j=judged[x['variant_id']]
            if j.get('verdict') not in ADJ_VERDICTS or not j.get('rationale'):raise ValueError('adjudication verdict shape')
            counts[j['verdict']]+=1
            u=reqs[(p['intent_id'],x['requirement_id'])]['visible_universe_review']['uncertain'][x['uncertain_index']]
            u.setdefault('adjudicated_variants',[]).append(dict(variant_id=x['variant_id'],source_spans=x['source_spans'],verdict=j['verdict'],rationale=j['rationale'],reviewer_id=r['reviewer_id'],packet_sha256=p['packet_sha256']))
        bindings[rpath.name]=sha(rpath);reviewers.add(r['reviewer_id'])
    for q in reqs.values():
        rv=q.get('visible_universe_review')
        if rv:
            for u in rv['uncertain']:u.setdefault('adjudicated_variants',[])  # unexported items: no variant => any visible portion still blocks
    base.update(schema_version='e1-common-source-support-r07',previous_map_sha256=sha(map_path),adjudication_export_sha256=sha(output/'adjudication-export-r07.json'),adjudication_review_bindings=bindings,adjudication_reviewers=sorted(reviewers),adjudication_semantics='supports variant fully visible => yes; an uncertain passage stops blocking only where its visible portion lies inside a does_not_support variant; uncertain verdict or unadjudicated portion keeps unknown.')
    base.pop('map_sha256',None);base['map_sha256']=cache_identity(base)
    out_map=output/'common-support-map-e1-r07.json';save_json(out_map,base)
    save_json(output/'adjudication-integration-r07.json',dict(status='passed',verdicts=counts,reviewers=sorted(reviewers),map_sha256=sha(out_map),review_bindings=bindings))
    print('integrated adjudication',counts,flush=True)

# ---------------------------------------------------------------- score
def write_csv(path,records):
    with path.open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)

def detail_key(r):return (r['kind'],r['intent_id'],r.get('method'),r.get('k'),r.get('budget'),r.get('stage'))

def stream(path):
    with Path(path).open(encoding='utf8') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def _inputs(source_run,map_path):
    mapping=load(map_path);maps={r['intent_id']:r for r in mapping['records']}
    query_ids={r['intent_id'] for r in load_queries(source_run/'queries.jsonl',80)}
    if set(maps)!=query_ids:raise ValueError('common map must cover exactly 80 query intents')
    verified=load(source_run/'verification-e1-r01.json')
    if verified.get('status')!='passed':raise ValueError('r05 saved-output verification must have passed')
    return maps,query_ids,verified

def score_config(source_run,output,map_path,config,rev='r06'):
    """Score one configuration by streaming its frozen rankings/contexts (memory and time bounded)."""
    if config not in configurations():raise ValueError('unknown configuration')
    maps,query_ids,verified=_inputs(source_run,map_path);mapping_sha256=sha(map_path)
    src=source_run/('index-'+config);dst=output/('index-'+config);dst.mkdir(exist_ok=rev!='r06')
    bindings={n:sha(src/n) for n in ('rankings.jsonl','contexts.jsonl','score-details-e1-r01.jsonl')}
    expected=verified['checks'][config]['artifact_sha256']
    for n,h in bindings.items():
        if expected.get(n)!=h:raise ValueError(f'{config}/{n} differs from r05-verified artifact')
    prior_by={detail_key(r):r for r in stream(src/'score-details-e1-r01.jsonl')}
    per_intent={i:[] for i in query_ids};rank_meta=[];context_meta=[];times=[]
    for ranking in stream(src/'rankings.jsonl'):
        intent=ranking['intent_id'];m=maps[intent];h=cache_identity(ranking);failed=ranking['status']!='success'
        rank_meta.append(dict(intent_id=intent,status=ranking['status']))
        if not failed:times.append(ranking['times']['r4_total_seconds'])
        for method in ('R1','R2','R3','R4'):
            for kk in (1,5,10,20):
                v=prefix_metrics_r06(ranking['results'][method],m,kk) if not failed else dict(support={r['requirement_id']:'unknown' for r in m['requirements']},support_basis={},sufficient='unknown',coverage_lower=0.,coverage_upper=1.,complete_rr_lower=0.,complete_rr_upper=1.,prefix_evidence=[])
                per_intent[intent].append(dict(configuration_id=config,kind='layer1_raw',intent_id=intent,main_stratum=m['main_stratum'],method=method,k=kk,cell=f'layer1_raw/{method}/{kk}',groups=m['groups'],mapping_sha256=mapping_sha256,ranking_sha256=h,failure='missing_or_failed_retrieval' if failed else None,**v))
    for context in stream(src/'contexts.jsonl'):
        intent=context['intent_id'];B=context['budget'];m=maps[intent];h=cache_identity(context)
        context_meta.append(dict(intent_id=intent,budget=B))
        for stage in ('raw','expanded','final'):
            support,basis,_=support_r06([s for u in context[stage]['units'] for s in u['spans']],m)
            per_intent[intent].append(dict(configuration_id=config,kind='context',intent_id=intent,main_stratum=m['main_stratum'],budget=B,stage=stage,cell=f'fixed_budget_main/P0/{B}/{stage}',groups=m['groups'],mapping_sha256=mapping_sha256,context_id=context['context_id'],context_sha256=h,support=support,support_basis=basis,failure=None,**score_support(m['groups'],support)))
    if len(rank_meta)!=len({r['intent_id'] for r in rank_meta}) or len(context_meta)!=len({(r['intent_id'],r['budget']) for r in context_meta}):raise ValueError('duplicate intent/context cell')
    order={(me,kk):i for i,(me,kk) in enumerate((me,kk) for me in ('R1','R2','R3','R4') for kk in (1,5,10,20))}
    details=[]
    for intent in sorted(query_ids):
        rows_i=per_intent[intent]
        details+=sorted([r for r in rows_i if r['kind']=='layer1_raw'],key=lambda r:order[(r['method'],r['k'])])+sorted([r for r in rows_i if r['kind']=='context'],key=lambda r:(r['budget'],('raw','expanded','final').index(r['stage'])))
    if len(details)!=len(prior_by):raise ValueError('r05/r06 detail coverage drift')
    transitions=[]
    for d in details:
        p=prior_by[detail_key(d)]
        if p.get('ranking_sha256')!=d.get('ranking_sha256') or p.get('context_sha256')!=d.get('context_sha256'):raise ValueError('r05/r06 ranking/context binding drift')
        for rid,b in d['support_basis'].items():
            if b=='certificate' and d['support'][rid]!=p['support'][rid]:raise ValueError('certificate support drift vs r05')
            if b!='certificate' and p['support'][rid]!='unknown':raise ValueError('review touched a resolved r05 requirement')
        if p['sufficient']!='unknown' and p['sufficient']!=d['sufficient']:raise ValueError('non-monotone r05->r06 transition')
        transitions.append(dict(cell=d['cell'],intent_id=d['intent_id'],r05=p['sufficient'],r06=d['sufficient']))
    save_rows(dst/f'score-details-e1-{rev}.jsonl',details)
    save_json(dst/f'score-meta-e1-{rev}.json',dict(configuration_id=config,mapping_sha256=mapping_sha256,input_sha256=bindings,details_sha256=sha(dst/f'score-details-e1-{rev}.jsonl'),rank_meta=rank_meta,context_meta=context_meta,retrieval_mean_seconds=statistics.mean(times),transitions=transitions))
    print('scored',config,flush=True)

def finalize(source_run,output,map_path,rev='r06'):
    maps,query_ids,verified=_inputs(source_run,map_path);mapping_sha256=sha(map_path)
    profiles_path=source_run/'chunk-profiles-e1-r01.json';costs_path=source_run/'costs-e1-r01.json';verify_path=source_run/'verification-e1-r01.json';r05_sel_path=source_run/'candidate-selection-e1-r01.json'
    profiles={r['configuration_id']:r for r in load(profiles_path)};prior_costs={r['configuration_id']:r for r in load(costs_path)};r05_sel=load(r05_sel_path)
    r05_sig={r['configuration_id']:{k:r[k] for k in ('source_partition_signature','ranking_contract_signature','context_contract_signature','strict_equivalence_signature')} for r in r05_sel['nonduplicate_metrics']}
    summaries=[];execution=[];candidate_records=[];transitions=[];remaining=[];comparison=[];all_compact=[];bindings={}
    for config in configurations():
        dst=output/('index-'+config);meta=load(dst/f'score-meta-e1-{rev}.json');src=source_run/('index-'+config)
        if meta['mapping_sha256']!=mapping_sha256 or sha(dst/f'score-details-e1-{rev}.jsonl')!=meta['details_sha256']:raise ValueError('per-config score drift '+config)
        for n,h in meta['input_sha256'].items():
            if verified['checks'][config]['artifact_sha256'].get(n)!=h:raise ValueError('input drift '+config)
        bindings[config]=dict(meta['input_sha256'],**{f'score-details-e1-{rev}.jsonl':meta['details_sha256'],f'score-meta-e1-{rev}.json':sha(dst/f'score-meta-e1-{rev}.json')})
        details=rows(dst/f'score-details-e1-{rev}.jsonl')
        transitions+=[dict(configuration_id=config,**t) for t in meta['transitions']]
        remaining+=[dict(configuration_id=config,intent_id=d['intent_id'],cell=d['cell'],support=d['support'],support_basis=d['support_basis']) for d in details if d['cell'] in SELECTION_CELLS and d['sufficient']=='unknown']
        for cell in sorted({r['cell'] for r in details}):
            vals=[r for r in details if r['cell']==cell];s=dict(configuration_id=config,cell=cell,**aggregate(vals),coverage_lower_mean=statistics.mean(r['coverage_lower'] for r in vals),coverage_upper_mean=statistics.mean(r['coverage_upper'] for r in vals))
            s['complete_mrr_lower']=statistics.mean(r['complete_rr_lower'] for r in vals) if cell.startswith('layer1') else None;s['complete_mrr_upper']=statistics.mean(r['complete_rr_upper'] for r in vals) if cell.startswith('layer1') else None
            summaries.append(s)
        ex=execution_row(config,query_ids,meta['rank_meta'],meta['context_meta'],len(details));ex['quality_unknown']=sum(r['sufficient']=='unknown' for r in details);execution.append(ex)
        retrieval_mean=meta['retrieval_mean_seconds']
        if abs(retrieval_mean-prior_costs[config]['mean_r4_total_seconds'])>1e-12:raise ValueError('retrieval latency recomputation drift')
        get=lambda c:next(r for r in summaries if r['configuration_id']==config and r['cell']==c)
        a,b8,r10=get('fixed_budget_main/P0/4096/final'),get('fixed_budget_main/P0/8192/final'),get('layer1_raw/R4/10');p=profiles[config];cost=prior_costs[config]
        comparison.append(dict(configuration_id=config,n=80,children=p['children'],table_children=p['table_children'],token_max=p['token_max'],CGC4K_yes=a['yes'],CGC4K_no=a['no'],CGC4K_unknown=a['unknown'],CGC4K_lower=a['complete_group_lower'],CGC4K_possible_upper=a['complete_group_upper'],CGC8K_yes=b8['yes'],CGC8K_no=b8['no'],CGC8K_unknown=b8['unknown'],CGC8K_lower=b8['complete_group_lower'],CGC8K_possible_upper=b8['complete_group_upper'],CEGR10_yes=r10['yes'],CEGR10_no=r10['no'],CEGR10_unknown=r10['unknown'],CEGR10_lower=r10['complete_group_lower'],CEGR10_possible_upper=r10['complete_group_upper'],CompleteMRR10_lower=r10['complete_mrr_lower'],CompleteMRR10_possible_upper=r10['complete_mrr_upper'],mean_R4_seconds=retrieval_mean,build_seconds=cost['stages']['build']['wall_seconds'],context_seconds=cost['stages']['context']['wall_seconds']))
        if ex['status']=='scored' and not config.startswith('B0'):
            candidate_records.append(dict(configuration_id=config,cgc4_lower=a['complete_group_lower'],cgc4_upper=a['complete_group_upper'],cegr10_lower=r10['complete_group_lower'],cegr10_upper=r10['complete_group_upper'],retrieval_mean_seconds=retrieval_mean,signatures=r05_sig[config]))
        all_compact+=[{k:r.get(k) for k in ('configuration_id','kind','intent_id','main_stratum','method','k','budget','stage','sufficient','coverage_lower','coverage_upper','complete_rr_lower','complete_rr_upper','failure','mapping_sha256','ranking_sha256','context_sha256')} for r in details]
    metrics,equivalent=select_equivalent_representatives(candidate_records);decision=candidate_decision(metrics)
    if any(r['status']!='scored' for r in execution):decision.update(status='pending_failed_matrix',selected=[])
    decision.update(revision=rev,mapping_sha256=mapping_sha256,baseline_retained='B0-regex320-overlap48-M0',nonduplicate_metrics=metrics,equivalent_configs=equivalent,generation_calls=0,remote_judge_calls=0,signature_source=dict(file=r05_sel_path.name,sha256=sha(r05_sel_path),basis='byte-identical r05-verified rankings/contexts; signatures do not depend on the support map'),
        candidate_purposes=None if decision['status']!='frozen' else {decision['selected'][0]:'primary: best 4K CGC under frozen rule',**({decision['selected'][1]:'second non-duplicate candidate under frozen rule'} if len(decision['selected'])>1 else {})})
    save_json(output/f'candidate-selection-e1-{rev}.json',decision)
    save_json(output/f'scores-e1-{rev}.json',dict(schema_version=f'e1-layer1-layer2-source-score-{rev}',source_run=source_run.name,mapping_path=map_path.name,mapping_sha256=mapping_sha256,input_bindings=bindings,auxiliary_inputs={n.name:sha(n) for n in (profiles_path,costs_path,verify_path,r05_sel_path)},summaries=summaries,execution=execution,independent_intents=80,unknown_semantics=__doc__,generation_calls=0))
    write_csv(output/f'main-table-e1-{rev}.csv',summaries);write_csv(output/f'comparison-e1-{rev}.csv',comparison);write_csv(output/f'per-intent-table-e1-{rev}.csv',all_compact);write_csv(output/f'transitions-r05-{rev}.csv',transitions)
    save_rows(output/f'unknown-remaining-e1-{rev}.jsonl',remaining);save_json(output/f'execution-e1-{rev}.json',execution)
    print('candidate',decision['status'],decision['selected'],flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['export','render','normalize','integrate','score-config','finalize','adjudication-export','adjudication-integrate'])
    p.add_argument('--source-run',type=Path,required=True,help='frozen E1 run (read-only), e.g. outputs/pearl-chunking-dev80-20261005-05')
    p.add_argument('--output',type=Path,required=True,help='new Session 3B run directory');p.add_argument('--mapping',type=Path);p.add_argument('--config',action='append',help='score-config: configuration id (repeatable)');p.add_argument('--revision',default='r06',choices=['r06','r07']);a=p.parse_args()
    src=a.source_run.resolve();out=a.output.resolve()
    if a.stage=='export':export(src,out)
    elif a.stage=='render':render(src,out)
    elif a.stage=='normalize':normalize(out)
    elif a.stage=='integrate':integrate(src,out)
    elif a.stage=='adjudication-export':adjudication_export(src,out)
    elif a.stage=='adjudication-integrate':adjudication_integrate(out)
    else:
        m=(a.mapping or out/f'common-support-map-e1-{a.revision}.json').resolve()
        if a.stage=='finalize':finalize(src,out,m,a.revision)
        else:
            if not a.config:p.error('--config required')
            for c in a.config:score_config(src,out,m,c,a.revision)

if __name__=='__main__':main()
