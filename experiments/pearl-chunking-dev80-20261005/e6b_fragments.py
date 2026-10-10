"""Session 6B citation redo (6b-work-plan F2): fragment boundaries of every Source block in a context.

The context text is never changed. A Source block of the E5 contexts is serialized by source-assembly-r01
(assemble.unit / assemble.serialize) as
    [Source [[doc_id,source_version,element_id,start,end],...]]\\n<text>
with blocks joined by a blank line. Inside one block the fragment texts are element_text[start:end] in header
order, joined by '' when the next fragment continues the same element at the previous end, otherwise by '\\n\\n'.
So every fragment's Unicode [start,end) in the context follows from the header intervals alone.

derive(context) computes these boundaries from the header only and marks a block aligned only when it checks out
strictly: the header is a JSON list of 5-tuples with valid integer intervals, the derived body length ends exactly
at the next header (or the end of the context), and every separator is literally '\\n\\n'. A block that fails
any check keeps its header but gets no fragment spans; nothing is guessed. verify() adds two independent
checks (the frozen assembly record of the context and the frozen source views); neither is used to derive.
Offsets are Python str indices, i.e. Unicode code points (not UTF-16 units, not bytes).

The single-block calibration anchors use the historical header '[Source <id> | <locator>]'; such a block is one
source, so its one fragment is the whole body (derivation 'single_source_label').
"""
from __future__ import annotations
import json
import re

VERSION='fragment-boundaries-r03'
TAG='[Source '
LABEL=re.compile(r'\[Source ([^\]\n|]+?) \| ([^\]\n]+)\]\n')


def fragment_id(block,k):return f'B{block}-F{k}'


def _tuple_ok(t):
    return (isinstance(t,list) and len(t)==5 and all(isinstance(x,str) and x for x in t[:3])
            and all(isinstance(x,int) and not isinstance(x,bool) for x in t[3:]) and 0<=t[3]<t[4])


def _headers(context):
    """Every '[Source [[...]]]\\n' at the start of the context or right after a blank line."""
    dec=json.JSONDecoder();out=[];i=0
    while True:
        i=context.find(TAG,i)
        if i<0:return out
        if i==0 or context[i-2:i]=='\n\n':
            try:
                arr,end=dec.raw_decode(context,i+len(TAG))
                if context[end:end+2]==']\n' and isinstance(arr,list) and arr and all(isinstance(t,list) for t in arr):
                    out.append((i,end+2,arr))
            except ValueError:pass
        i+=1


def derive(context):
    """Blocks with fragment boundaries derived from the header intervals; context is read, never changed."""
    m=LABEL.match(context)
    if m and not _headers(context):
        return [{'block_id':'B1','header_span':[0,m.end()],'body_span':[m.end(),len(context)],'header_text':context[:m.end()-1],
                 'alignment':'exact','derivation':'single_source_label',
                 'fragments':[{'fragment_id':fragment_id(1,1),'header_index':1,'source':f'{m.group(1)} | {m.group(2)}','span':[m.end(),len(context)]}]}]
    heads=_headers(context);blocks=[]
    if not heads or heads[0][0]!=0:
        return [{'block_id':'B0','alignment':'unaligned','problems':['context does not start with a parseable Source header'],'fragments':[]}]
    for n,(h0,b0,arr) in enumerate(heads,1):
        nxt=heads[n][0]-2 if n<len(heads) else len(context)
        problems=[];frags=[];pos=b0;prev=None
        if not all(_tuple_ok(t) for t in arr):problems.append('header is not a list of [doc_id,source_version,element_id,start,end] with 0<=start<end')
        else:
            for k,t in enumerate(arr,1):
                if prev is not None:
                    contiguous=prev[:3]==t[:3] and prev[4]==t[3]
                    if not contiguous:
                        if context[pos:pos+2]!='\n\n':problems.append(f'separator before fragment {k} is not a blank line')
                        pos+=2
                frags.append({'fragment_id':fragment_id(n,k),'header_index':k,'source':t,'span':[pos,pos+t[4]-t[3]]})
                pos+=t[4]-t[3];prev=t
            if pos!=nxt:problems.append(f'derived block end {pos} differs from the next block boundary {nxt}')
        blk={'block_id':f'B{n}','header_span':[h0,b0],'body_span':[b0,nxt],'header_text':context[h0:b0-1],
             'alignment':'exact' if not problems else 'unaligned','derivation':'header_intervals'}
        if problems:blk.update(problems=problems,fragments=[{'fragment_id':fragment_id(n,k),'header_index':k,'source':t,'span':None} for k,t in enumerate(arr,1)])
        else:blk['fragments']=frags
        blocks.append(blk)
    return blocks


def packet_field(blocks):
    """The judge-facing field: blocks with header/body spans and every fragment's span and source (no checks, no text copies)."""
    out=[]
    for b in blocks:
        row={'block_id':b['block_id'],'alignment':b['alignment'],'header_span':b.get('header_span'),'body_span':b.get('body_span'),
             'fragments':[{k:f[k] for k in ('fragment_id','header_index','source','span')} for f in b['fragments']]}
        out.append(row)
    return out


def verify(context,blocks,record=None,views=None):
    """Independent checks of aligned blocks. record: the frozen assembly 'final' snapshot of this context (units with spans and
    parts); views: {(doc_id,source_version,element_id): element text}. Returns a list of problems per block_id."""
    out={}
    units=(record or {}).get('units')
    if record is not None and (record.get('serialized_context')!=context or len(units)!=len(blocks)):
        return {'context':['assembly record does not reproduce this context or block count']}
    for i,b in enumerate(blocks):
        if b['alignment']!='exact' or b['derivation']!='header_intervals':continue
        p=[]
        if units is not None:
            u=units[i];body0=b['body_span'][0]
            if [[s[k] for k in ('doc_id','source_version','element_id','start','end')] for s in u['spans']]!=[f['source'] for f in b['fragments']]:p.append('header differs from assembly spans')
            elif [[body0+x['text_start'],body0+x['text_end']] for x in u['parts']]!=[f['span'] for f in b['fragments']]:p.append('fragment spans differ from assembly parts')
            elif context[b['body_span'][0]:b['body_span'][1]]!=u['text']:p.append('block body differs from assembly unit text')
        if views is not None:
            for f in b['fragments']:
                d,v,e,s0,s1=f['source'];text=views.get((d,v,e))
                if text is None:p.append(f'{f["fragment_id"]}: element not in source views')
                elif text[s0:s1]!=context[f['span'][0]:f['span'][1]] or s1>len(text):p.append(f'{f["fragment_id"]}: text differs from the source element')
        if p:out[b['block_id']]=p
    return out
