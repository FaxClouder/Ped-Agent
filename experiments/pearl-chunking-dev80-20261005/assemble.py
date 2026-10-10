"""Gold-isolated source-coordinate assembly, experiment-local contract r01."""
from __future__ import annotations
import copy
import hashlib
import json
import time

VERSION='source-assembly-r01'
KEYS=('doc_id','source_version','element_id')

def digest(obj):
    text=obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def key(s): return tuple(s[k] for k in KEYS)

def union_spans(spans):
    groups={}
    for s in spans:
        if not isinstance(s['start'],int) or not isinstance(s['end'],int) or s['start']<0 or s['end']<=s['start']:
            raise ValueError('invalid Unicode half-open source span')
        groups.setdefault(key(s),[]).append(copy.deepcopy(s))
    out=[]
    for values in groups.values():
        merged=[]
        for s in sorted(values,key=lambda x:(x['start'],x['end'])):
            if merged and s['start']<=merged[-1]['end']:
                merged[-1]['end']=max(merged[-1]['end'],s['end'])
            else: merged.append(s)
        out.extend(merged)
    return out

def subtract_spans(spans,seen):
    out=[]
    for s in union_spans(spans):
        intervals=[(s['start'],s['end'])]
        for old in seen:
            if key(s)!=key(old): continue
            intervals=[piece for a,b in intervals for piece in ((a,min(b,old['start'])),(max(a,old['end']),b)) if piece[0]<piece[1]]
        out.extend(dict(s,start=a,end=b) for a,b in intervals)
    return out

def views_by_id(views):
    if isinstance(views,dict):
        values=[views] if 'elements' in views else list(views.values())
    else: values=list(views)
    result={}
    for v in values:
        identity=(v['doc_id'],v['source_version'])
        if identity in result: raise ValueError('duplicate source view identity')
        result[identity]=v
    return result

def source_order(spans,views):
    spans=union_spans(spans)
    source_first={k:i for i,k in enumerate(dict.fromkeys((s['doc_id'],s['source_version']) for s in spans))}
    def order(s):
        v=views[(s['doc_id'],s['source_version'])]
        ids={e['element_id']:i for i,e in enumerate(v['elements'])}
        if s['element_id'] not in ids: raise ValueError('unknown source element')
        e=v['elements'][ids[s['element_id']]]
        if s['end']>len(e['text']): raise ValueError('span exceeds source')
        return source_first[(s['doc_id'],s['source_version'])],ids[s['element_id']],s['start']
    return sorted(spans,key=order)

def unit(spans,views,chunk_id,rank):
    spans=source_order(spans,views)
    text=''; parts=[]
    previous=None
    for s in spans:
        v=views[(s['doc_id'],s['source_version'])]
        element=next(e for e in v['elements'] if e['element_id']==s['element_id'])
        if previous is not None:
            separator='' if key(previous)==key(s) and previous['end']==s['start'] else '\n\n'
            text+=separator
        begin=len(text); text+=element['text'][s['start']:s['end']]
        parts.append(dict(span=copy.deepcopy(s),text_start=begin,text_end=len(text)))
        previous=s
    return dict(seed_chunk_id=chunk_id,rank=rank,spans=spans,text=text,parts=parts,text_sha256=digest(text),truncated=False)

def serialize(units):
    return '\n\n'.join('[Source '+json.dumps([list(key(s))+[s['start'],s['end']] for s in u['spans']],ensure_ascii=False,separators=(',',':'))+']\n'+u['text'] for u in units)

def snapshot(units,counter):
    serialized=serialize(units)
    return dict(units=copy.deepcopy(units),serialized_context=serialized,text_sha256=digest(serialized),token_count=counter.count(serialized))

def prefix_unit(u,n,views):
    spans=[]
    for part in u['parts']:
        available=max(0,min(n,part['text_end'])-part['text_start'])
        if available:
            s=part['span']; spans.append(dict(s,end=s['start']+available))
    if not spans: return None
    out=unit(spans,views,u['seed_chunk_id'],u['rank'])
    # Never end in a separator which has no evidence identity.
    if len(out['text'])!=n: return None
    out['truncated']=n<len(u['text'])
    return out

def truncate_with_offsets(u,kept,views,budget,counter):
    # Token offsets are audited when available. Exhaustive Unicode boundaries also
    # handle partial-token BPE merges and guarantee maximality without monotonicity.
    offsets=counter.encode_with_offsets(u['text'])[1] if hasattr(counter,'encode_with_offsets') else list(counter.offsets(u['text'])) if hasattr(counter,'offsets') else []
    for n in range(len(u['text'])-1,0,-1):
        candidate=prefix_unit(u,n,views)
        if candidate is not None and counter.count(serialize(kept+[candidate]))<=budget:
            return candidate,dict(retained_characters=n,token_offset_boundary=n in {b for a,b in offsets},search='descending_exhaustive_unicode_source_prefix')
    return None,dict(retained_characters=0,token_offset_boundary=False,search='descending_exhaustive_unicode_source_prefix')

def _expand(c,views,parents,P):
    core=c['core_spans']; overlap=c.get('overlap_spans',[])
    if P=='P0': return core+overlap
    expanded=list(core)
    if P=='P1':
        for s in core:
            v=views[(s['doc_id'],s['source_version'])]; es=v['elements']
            i=next(i for i,e in enumerate(es) if e['element_id']==s['element_id'])
            e=es[i]
            if e.get('element_type')=='table': continue
            for j in (i-1,i,i+1):
                if 0<=j<len(es):
                    other=es[j]
                    if other.get('element_type') in ('table','heading','image') or other.get('heading_path',[])!=e.get('heading_path',[]): continue
                    if other['text']: expanded.append(dict(doc_id=s['doc_id'],source_version=s['source_version'],element_id=other['element_id'],start=0,end=len(other['text'])))
    else:
        if isinstance(parents,dict) and 'parents' in parents: values=parents['parents']
        elif isinstance(parents,dict):
            values=[]
            for v in parents.values(): values.extend(v['parents'] if 'parents' in v else [v])
        else: values=parents
        matched=[]
        core_sources={(s['doc_id'],s['source_version']) for s in core}
        for p in values:
            if not p['spans'] or (p['spans'][0]['doc_id'],p['spans'][0]['source_version']) not in core_sources:continue
            if any(key(a)==key(b) and a['start']<b['end'] and b['start']<a['end'] for a in core for b in p['spans']):
                matched.extend(p['spans'])
        # A partial graph must never silently report P2 success.
        if subtract_spans(core,union_spans(matched)): raise ValueError('public parent graph does not cover core')
        expanded+=matched
    return expanded+overlap

def assemble(ranking,views,parents,P,B,panel,counter):
    started=time.perf_counter()
    if P not in ('P0','P1','P2') or B<=0 or panel not in ('fixed_budget_main','seed10_diagnostic','layer1_raw'):
        raise ValueError('invalid strategy, budget or panel')
    rows=ranking.get('chunks',ranking.get('ranking',[])) if isinstance(ranking,dict) else ranking
    rows=list(rows)[:10 if panel in ('seed10_diagnostic','layer1_raw') else 100]
    if len({c['chunk_id'] for c in rows})!=len(rows): raise ValueError('duplicate ranked chunk ID')
    vs=views_by_id(views); raw=[]; expanded=[]; dedup=[]; seen=[]
    for rank,c in enumerate(rows,1):
        raw.append(unit(c['core_spans']+c.get('overlap_spans',[]),vs,c['chunk_id'],rank))
        expanded.append(unit(_expand(c,vs,parents,P),vs,c['chunk_id'],rank))
        residual=subtract_spans(expanded[-1]['spans'],seen)
        if residual: dedup.append(unit(residual,vs,c['chunk_id'],rank))
        seen=union_spans(seen+expanded[-1]['spans'])
    final=[]; truncation=[]; stopped=False
    for u in dedup:
        if stopped:
            truncation.append(dict(seed_chunk_id=u['seed_chunk_id'],reason='after_budget_stop',retained_characters=0)); continue
        if counter.count(serialize(final+[u]))<=B:
            final.append(u); continue
        stopped=True
        candidate,trace=truncate_with_offsets(u,final,vs,B,counter)
        if candidate: final.append(candidate)
        truncation.append(dict(seed_chunk_id=u['seed_chunk_id'],reason='prefix_truncated' if candidate else 'header_or_body_cannot_fit',**trace))
    record=dict(assembly_version=VERSION,panel_id=panel,strategy=P,budget=B,ranking_sha256=digest(rows),source_views_sha256=digest({str(k):v['view_sha256'] if 'view_sha256' in v else digest(v) for k,v in vs.items()}),parent_graph_sha256=digest(parents),raw=snapshot(raw,counter),expanded=snapshot(expanded,counter),deduplicated=snapshot(dedup,counter),final=snapshot(final,counter),truncation=truncation,assembly_seconds=time.perf_counter()-started)
    record['dedup']=record['deduplicated']
    if record['final']['token_count']>B: raise ValueError('serialized budget exceeded')
    record['context_id']=digest({k:v for k,v in record.items() if k not in ('assembly_seconds','context_id')})
    return record
