"""Public source-preserving boundary policies with separate overlap and prefix."""
import math
from copy import deepcopy
from ped_knowledge.chunking import _sentence_spans
from ped_knowledge.tokenization import TOKEN_PATTERN
from source_view import digest, make_span, text_for_spans, text_hash

SENTENCE_SPLITTER_VERSION = "ped-knowledge-bilingual-sentence-spans-session2-v1"


def sentence_spans(text):
    # Existing sentence boundaries omit inter-sentence spaces; assign them to the
    # previous sentence so the source partition is exhaustive and reversible.
    ends = sorted({b for a, b in _sentence_spans(text) if b > a})
    starts = [a for a, b in _sentence_spans(text) if b > a]
    boundaries = starts[1:] + [len(text)] if starts else [len(text)]
    previous = 0
    result = []
    for end in boundaries:
        if end > previous:
            result.append((previous, end))
            previous = end
    return result


def token_ranges(text, counter, limit):
    if limit <= counter.count(""):
        raise ValueError("token limit cannot contain content and tokenizer special tokens")
    ranges, start = [], 0
    while start < len(text):
        tail = text[start:]
        if counter.count(tail) <= limit:
            end = len(text)
        else:
            _, offsets = counter.encode_with_offsets(tail)
            # XLM-R may emit several offsets for one Unicode code point. Unique
            # character boundaries avoid splitting Unicode or losing whitespace.
            content_offsets = [(a,b) for a,b in offsets if b > a]
            width = max(1, limit-counter.count(""))
            selected = content_offsets[:width]
            candidates = sorted({b for a,b in selected}, reverse=True)
            end_offset = next((b for b in candidates if counter.count(tail[:b]) <= limit), None)
            if end_offset is None:
                raise ValueError("one Unicode character exceeds token limit")
            # Preserve the source gap until the next token if it fits. No
            # maximal-prefix claim: fixed windows need a legal exhaustive split.
            next_start = next((a for a,b in content_offsets if a >= end_offset), end_offset)
            if counter.count(tail[:next_start]) <= limit:
                end_offset=next_start
            end = start + end_offset
        ranges.append((start, end))
        start = end
    return ranges


def interval_spans(elements, start, end):
    result, cursor = [], 0
    for e in elements:
        stop = cursor + len(e["text"])
        a, b = max(start, cursor), min(end, stop)
        if b > a:
            source_offset=e.get("_source_offset",0)
            result.append(make_span(e, a - cursor + source_offset, b - cursor + source_offset))
        cursor = stop + 2
    return result


def _pack(view, units, counter, limit, semantic=None):
    packed, current = [], []
    for spans, sentence_key in units:
        text = text_for_spans(view, current)
        distance = (semantic or {}).get("distances", {}).get(sentence_key)
        semantic_cut = current and counter.count(text) >= math.floor(0.5 * limit) and distance is not None and distance > semantic["threshold"]
        if current and (semantic_cut or counter.count(text_for_spans(view, current + spans)) > limit):
            packed.append(current)
            current = []
        current += spans
    if current:
        packed.append(current)
    return packed


def _units(elements, counter, limit, always_sentences=False):
    units = []
    for e in elements:
        boundaries = sentence_spans(e["text"]) if always_sentences or counter.count(e["text"]) > limit else [(0, len(e["text"]))]
        for a, b in boundaries:
            for x, y in token_ranges(e["text"][a:b], counter, limit):
                s = make_span(e, a + x, a + y)
                units.append(([s], sentence_key(e, a) if x == 0 else None))
    return units


def sentence_key(e, start):
    return f'{e["doc_id"]}:{e["source_version"]}:{e["element_id"]}:{start}'


def _record(view, spans, policy, counter, ordinal, overlap=None, table=False):
    overlap = overlap or []
    core = text_for_spans(view, spans)
    source = text_for_spans(view, overlap + spans)
    identity = {"spans": spans, "policy": policy, "view_sha256": view["view_sha256"]}
    record = dict(chunk_id="chunk-" + digest(identity)[:24],doc_id=view["doc_id"],source_version=view["source_version"],
                  core_spans=spans,overlap_spans=overlap,prefix_spans=[],core_text=core,source_text=source,retrieval_text=source,
                  core_sha256=digest({"spans":spans,"text":core}),text_sha256=text_hash(source),
                  tokenizer_sha256=counter.fingerprint,table_snapshot_sha256=view.get("table_snapshot_sha256"),
                  parent_ids=[],policy=policy,config_id=digest(policy),ordinal=ordinal,is_table=table)
    return record


def chunk(view, C, L, counter, semantic_manifest=None):
    if C not in {"C1","C2","C3","C4","B0"}:
        raise ValueError("unknown boundary policy")
    if C == "C4" and (not semantic_manifest or semantic_manifest.get("threshold") is None):
        raise ValueError("C4 requires frozen measured threshold")
    from table_snapshot import freeze_tables
    if "table_snapshot" not in view:
        freeze_tables([view],counter)
    lookup = {e["element_id"]:e for e in view["elements"]}
    policy = {"C":C,"L":L,"length_unit":"regex-token-v1" if C=="B0" else "BGE-tokens", "overlap_tokens":48 if C=="B0" else 0,"splitter":SENTENCE_SPLITTER_VERSION}
    result=[]
    for run in view["barrier_runs"]:
        elements=[lookup[eid] for eid in run]
        if elements[0]["element_type"]=="table":
            table=next(t for t in view["table_snapshot"]["tables"] if t["element_id"]==run[0] and t["doc_id"]==view["doc_id"])
            for unit in table["chunks"]:
                result.append(_record(view,unit["core_spans"],policy,counter,len(result),table=True))
            continue
        groups=[]; current=[]; tokens=0
        for e in elements:
            if C=="B0" and not e["text"].strip():
                continue
            changed=current and e["heading_path"]!=current[-1]["heading_path"]
            regex_count=len(TOKEN_PATTERN.findall(e["text"]))
            if current and ((C=="C3" and changed) or (C=="B0" and (changed or tokens+regex_count>1800))):
                groups.append(current); current=[]; tokens=0
            current.append(e); tokens+=regex_count
            if C=="B0" and tokens>=1200:
                groups.append(current); current=[];tokens=0
        if current: groups.append(current)
        for group in groups:
            if C=="B0":
                # Preserve legacy _render_elements whitespace trimming while
                # mapping each retained character to its original raw offset.
                group=[dict(e,text=e["text"].strip(),_source_offset=len(e["text"])-len(e["text"].lstrip())) for e in group]
            text="\n\n".join(e["text"] for e in group)
            if C=="B0":
                matches=list(TOKEN_PATTERN.finditer(text));step=272
                for i in range(0,len(matches),step):
                    a=matches[i].start(); stop=min(i+320,len(matches)); b=matches[stop-1].end()
                    core_start=a if i==0 else matches[min(i+48,len(matches)-1)].start()
                    result.append(_record(view,interval_spans(group,core_start,b),policy,counter,len(result),interval_spans(group,a,core_start)))
                    if stop==len(matches): break
            else:
                ranges=[interval_spans(group,a,b) for a,b in token_ranges(text,counter,L)] if C=="C1" else _pack(view,_units(group,counter,L,C=="C4"),counter,L,semantic_manifest if C=="C4" else None)
                for spans in ranges:
                    if spans:
                        result.append(_record(view,spans,policy,counter,len(result)))
    if "public_parent_graph" in view:
        from parent_graph import parents_for_spans
        for record in result:
            record["parent_ids"]=parents_for_spans(record["core_spans"],view["public_parent_graph"])
    return result


def attach_overlap(core, r, L, view=None, counter=None):
    if view is None or counter is None:
        raise ValueError("overlap requires public source view and tokenizer")
    result=deepcopy(core); limit=math.floor(r*L)
    if not 0<=r<1: raise ValueError("invalid overlap ratio")
    if limit<=counter.count("") or core["is_table"]:
        return result
    first=core["core_spans"][0]; lookup={e["element_id"]:e for e in view["elements"]}
    run=next(run for run in view["barrier_runs"] if first["element_id"] in run)
    elements=[]
    for eid in run:
        e=lookup[eid]
        if core["policy"]["C"]=="C3" and e["heading_path"]!=lookup[first["element_id"]]["heading_path"]:
            elements=[];continue
        if eid==first["element_id"]:
            e=dict(e,text=e["text"][:first["start"]]);elements.append(e);break
        elements.append(e)
    text="\n\n".join(e["text"] for e in elements)
    sentence_starts=[a for a,b in sentence_spans(text)]
    valid=[a for a in sentence_starts if counter.count(text[a:])<=limit]
    if valid: start=min(valid)
    else:
        _,offsets=counter.encode_with_offsets(text)
        valid=[a for a,b in offsets if b>a and counter.count(text[a:])<=limit]
        if not valid:return result
        start=min(valid)
    result["overlap_spans"]=interval_spans(elements,start,len(text))
    result["source_text"]=text_for_spans(view,result["overlap_spans"]+result["core_spans"])
    result["retrieval_text"]=result["source_text"];result["text_sha256"]=text_hash(result["source_text"])
    result["config_id"]=digest({"base":core["config_id"],"O":r})
    result["chunk_id"]="chunk-"+digest({"base":core["chunk_id"],"O":r})[:24]
    return result


def render_prefix(core, prefix_config, view=None, counter=None):
    result=deepcopy(core)
    if prefix_config.get("mode","M0")=="M0":return result
    if view is None or counter is None:raise ValueError("prefix requires raw source view and tokenizer")
    maximum=min(64,prefix_config.get("max_tokens",64))
    first=core["core_spans"][0]; e=next(e for e in view["elements"] if e["element_id"]==first["element_id"])
    headings=[h for h in view["elements"] if h["element_type"] in {"heading","title"}]
    ordered=[]
    if headings:ordered.append(headings[0])
    for name in reversed(e["heading_path"]):
        match=next((h for h in headings if h["text"]==name),None)
        if match and match not in ordered:ordered.append(match)
    spans=[]
    for h in ordered:
        whole=spans+[h["span"]]
        if counter.count(text_for_spans(view,whole))<=maximum:spans=whole;continue
        # A prefix is allowed to end mid-heading, but always at a raw offset.
        _, offsets=counter.encode_with_offsets(h["text"])
        valid=[b for a,b in offsets if b>a and counter.count(text_for_spans(view,spans+[make_span(h,0,b)]))<=maximum]
        if valid:spans.append(make_span(h,0,max(valid)))
        break
    prefix=text_for_spans(view,spans)
    result.update(prefix_spans=spans,prefix_text=prefix,retrieval_text=prefix+"\n\n"+result["source_text"] if prefix else result["source_text"])
    result["text_sha256"]=text_hash(result["retrieval_text"])
    result["config_id"]=digest({"base":core["config_id"],"M":prefix_config})
    result["chunk_id"]="chunk-"+digest({"base":core["chunk_id"],"M":prefix_config})[:24]
    return result
