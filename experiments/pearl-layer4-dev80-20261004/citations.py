"""Frozen textual scope candidates; copies already reviewed claim-source support only."""
import re,copy

def source_spans(context):
    matches=list(re.finditer(r'\[Source\s+([^\]|]+)\s*\|\s*p\.([^\]]+)\]',context))
    return [{'source_label':m.group(0),'source_id':m.group(1).strip(),'pages':m.group(2).strip(),'start':m.start(),'end':matches[i+1].start() if i+1<len(matches) else len(context)} for i,m in enumerate(matches)]

def expand_evidence(ev,context):
    spans=[s for s in source_spans(context) if s['source_label']==ev['source_label'] and s['start']<=ev['start']<ev['end']<=s['end']]
    if not spans: raise ValueError('Evidence source absent or crossed')
    source=spans[0]
    start=context.rfind('\n\n',source['start'],ev['start']);start=source['start'] if start<0 else start+2
    end=context.find('\n\n',ev['end'],source['end']);end=source['end'] if end<0 else end
    return ev|{'start':start,'end':end,'quote':context[start:end]}

def textual_pairs(answer,claims,context):
    citations=list(re.finditer(r'[\[(][^\]\)\n]*pearl-src-[^\]\)\n]*[\])]',answer))
    scrub=list(answer)
    for m in citations:scrub[m.start():m.end()]=' '*len(m.group())
    clean=''.join(scrub)
    for m in re.finditer(r'\bet al\.|\bAdj\.|\b(?:Mr|Dr|Fig|Eq|Sec)\.',clean):
        for i in range(m.start(),m.end()):
            if scrub[i]=='.':scrub[i]=' '
    clean=''.join(scrub)
    stops=[m.end() for m in re.finditer(r'(?<!\d)[.!?](?!\d)|(?<=\d)[.!?](?!\d)|\n\s*\n',clean)]
    spans=source_spans(context); pairs=[]
    for cite in citations:
        previous=[s for s in stops if s<=cite.start()]
        # A trailing period before an inline citation terminates the cited sentence.
        boundary=previous[-1] if previous else 0
        trailing=bool(previous) and not clean[boundary:cite.start()].strip()
        if trailing:boundary=previous[-2] if len(previous)>1 else 0
        end=cite.start() if trailing else next((s for s in stops if s>cite.end()),len(answer))
        line_start=answer.rfind('\n',0,cite.start())+1
        line_end=answer.find('\n',cite.end());line_end=len(answer) if line_end<0 else line_end
        if re.match(r'\s*(?:[-*+]\s|\d+[.)]\s)',answer[line_start:line_end]):
            boundary=max(boundary,line_start);end=min(end,line_end)
        if not answer[line_start:cite.start()].strip() and not answer[cite.end():line_end].strip():
            # A stand-alone paragraph-end citation covers that paragraph if it has no other citations.
            para=answer.rfind('\n\n',0,cite.start());para_start=0 if para<0 else para+2
            if not answer[para_start:cite.start()].strip():
                para=answer.rfind('\n\n',0,para);para_start=0 if para<0 else para+2
            if not any(para_start<=other.start()<cite.start() for other in citations):boundary=para_start;end=cite.start()
        applicable=[c for c in claims if any(boundary<=o['start']<end for o in c.get('occurrences',[c]))]
        refs=list(re.finditer(r'pearl-src-[a-f0-9]+',cite.group()))
        identities=[]
        for index,ref in enumerate(refs):
            sid=ref.group();block=cite.group()[ref.end():refs[index+1].start() if index+1<len(refs) else len(cite.group())]
            pages=re.findall(r'p\.\s*([0-9]+(?:[-–][0-9]+)?)',block)
            identities.extend((sid,page.replace('–','-') if page is not None else None) for page in pages or [None])
        for claim in applicable:
            for sid,page in identities:
                matching=[s for s in spans if s['source_id']==sid and (page is None or s['pages'].replace('–','-')==page)]
                actual_label=f'[Source {sid} | p.{page}]' if page else f'[Source {sid}]'
                ev=[e for e in claim['grounding'].get('evidence',[]) if any(s['source_label']==e['source_label'] for s in matching)]
                label='invalid' if not any(s['source_id']==sid for s in spans) else 'outside-context' if not matching else claim['grounding']['label'] if ev else 'unknown'
                # Source-ID-only cites have no page; a valid visible source judgment can resolve to its actual label.
                resolved=ev[0]['source_label'] if page is None and ev else actual_label
                pairs.append({'claim_id':claim['claim_id'],'citation_start':cite.start(),'citation_end':cite.end(),'citation_quote':cite.group(),'source_label':resolved,'citation_source_id':sid,'citation_page':page,'label':label,'evidence':copy.deepcopy(ev),'reason':'Frozen inline-sentence scope; support copied only from an actual semantic judgment of this claim in this cited source/page. Missing same-source semantic basis remains unknown, not support by ID existence.'})
    return pairs
