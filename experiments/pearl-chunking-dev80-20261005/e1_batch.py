"""Equivalent descending exhaustive Unicode budget search, batched tokenization."""
from contextlib import contextmanager
import assemble as original

def truncate_batch(u,kept,views,budget,counter):
    offsets=counter.encode_with_offsets(u['text'])[1] if hasattr(counter,'encode_with_offsets') else list(counter.offsets(u['text'])) if hasattr(counter,'offsets') else []
    boundaries={b for a,b in offsets};max_n=len(u['text'])-1
    fixed=original.serialize(kept)
    import json
    def render(n):
        spans=[]
        for part in u['parts']:
            available=max(0,min(n,part['text_end'])-part['text_start'])
            if available:
                s=part['span'];spans.append(dict(s,end=s['start']+available))
        # A prefix ending in a separator is not a source-backed candidate.
        if not spans or not any(p['text_start']<n<=p['text_end'] for p in u['parts']):return None
        header='[Source '+json.dumps([list(original.key(s))+[s['start'],s['end']] for s in spans],ensure_ascii=False,separators=(',',':'))+']\n'
        return (fixed+'\n\n' if fixed else '')+header+u['text'][:n]
    for top in range(max_n,0,-64):
        candidates=[]
        for n in range(top,max(0,top-64),-1):
            rendered=render(n)
            if rendered is not None:candidates.append((n,rendered))
        if hasattr(counter,'_tokenizer'):
            counts=[len(e.ids) for e in counter._tokenizer.encode_batch([r[1] for r in candidates])]
        else:counts=[counter.count(r[1]) for r in candidates]
        for (n,rendered),count in zip(candidates,counts,strict=True):
            if count<=budget:
                # Recheck through the public counter and exact original serializer.
                value=original.prefix_unit(u,n,views)
                if value is None or original.serialize(kept+[value])!=rendered or counter.count(rendered)!=count:raise ValueError('batch/single source serializer or tokenizer count drift')
                return value,dict(retained_characters=n,token_offset_boundary=n in boundaries,search='descending_exhaustive_unicode_source_prefix_batched_equivalent')
    return None,dict(retained_characters=0,token_offset_boundary=False,search='descending_exhaustive_unicode_source_prefix_batched_equivalent')

@contextmanager
def batched_search():
    previous=original.truncate_with_offsets
    original.truncate_with_offsets=truncate_batch
    try:yield
    finally:original.truncate_with_offsets=previous
