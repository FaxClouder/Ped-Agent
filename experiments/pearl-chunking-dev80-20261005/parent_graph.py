"""Public section parent graph, built without child strategy dependencies."""
from source_view import digest,text_for_spans
from chunkers import _units,_pack


def build_parent_graph(view,counter,max_tokens=1536):
    parents=[];lookup={e["element_id"]:e for e in view["elements"]}
    for run in view["barrier_runs"]:
        groups=[];current=[]
        for eid in run:
            e=lookup[eid]
            if current and e["heading_path"]!=current[-1]["heading_path"]:
                groups.append(current);current=[]
            current.append(e)
        if current:groups.append(current)
        for group in groups:
            for spans in _pack(view,_units(group,counter,max_tokens),counter,max_tokens):
                p={"doc_id":view["doc_id"],"source_version":view["source_version"],"spans":spans,"core_spans":spans,"source_text":text_for_spans(view,spans),"heading_path":group[0]["heading_path"],"is_table":group[0]["element_type"]=="table"}
                p["parent_id"]="parent-"+digest(p)[:24];parents.append(p)
    result={"parents":parents,"view_sha256":view["view_sha256"],"tokenizer_fingerprint":counter.fingerprint,"max_tokens":max_tokens,"version":"public-section-parent-v1"}
    result["graph_sha256"]=digest(result)
    view["public_parent_graph"]=result
    return result


def parents_for_spans(core_spans,graph):
    return [p["parent_id"] for p in graph["parents"] if any(all(s[k]==t[k] for k in ("doc_id","source_version","element_id")) and max(s["start"],t["start"])<min(s["end"],t["end"]) for s in core_spans for t in p["spans"])]
