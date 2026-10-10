"""One public row-preserving table snapshot, independent of child policy."""
from source_view import digest,make_span

DEFAULT_CONFIG={"version":"public-table-rows-v1","max_tokens":256,"repeated_header":"none","oversized_row":"token-offset-fallback","oversized_cell":"raw-offset-partition"}


def freeze_tables(views,counter,table_config=None):
    from chunkers import token_ranges
    config=DEFAULT_CONFIG | (table_config or {})
    tables=[]
    for view in views:
        for e in view["elements"]:
            if e["element_type"]!="table":continue
            rows=e.get("table_data") or []
            cells=[];row_spans=[];cursor=0;resolved=True
            for ri,row in enumerate(rows):
                expected=" | ".join(str(c) for c in row)
                # Raw Adobe serialization must match exactly; no numeric fixes.
                actual=e["text"][cursor:cursor+len(expected)]
                if actual!=expected:
                    resolved=False;break
                row_spans.append(make_span(e,cursor,cursor+len(expected)+(1 if cursor+len(expected)<len(e["text"]) and e["text"][cursor+len(expected)]=="\n" else 0)))
                col_cursor=cursor
                for ci,cell in enumerate(row):
                    cell=str(cell)
                    cells.append({"row":ri,"col":ci,"span":make_span(e,col_cursor,col_cursor+len(cell)),"text":cell})
                    col_cursor+=len(cell)+3
                cursor=row_spans[-1]["end"]
            if cursor!=len(e["text"]):resolved=False
            if not resolved:
                cells=[];row_spans=[make_span(e)]
            chunks=[];start=0;end=0
            for s in row_spans:
                if end>start and counter.count(e["text"][start:s["end"]])>config["max_tokens"]:
                    chunks.append({"core_spans":[make_span(e,start,end)]});start=end
                if counter.count(e["text"][s["start"]:s["end"]])>config["max_tokens"]:
                    for a,b in token_ranges(e["text"][s["start"]:s["end"]],counter,config["max_tokens"]):
                        chunks.append({"core_spans":[make_span(e,s["start"]+a,s["start"]+b)]})
                    start=end=s["end"]
                else:end=s["end"]
            if end>start:chunks.append({"core_spans":[make_span(e,start,end)]})
            tables.append({"doc_id":view["doc_id"],"source_version":view["source_version"],"element_id":e["element_id"],"mapping_status":"resolved" if resolved else "unresolved","cells":cells,"rows":row_spans,"chunks":chunks,"raw_text_sha256":digest(e["text"])})
    snapshot={"config":config,"tokenizer_fingerprint":counter.fingerprint,"tables":tables}
    snapshot["snapshot_sha256"]=digest(snapshot)
    for view in views:
        view["table_snapshot"]={"config":config,"tokenizer_fingerprint":counter.fingerprint,"tables":[t for t in tables if t["doc_id"]==view["doc_id"] and t["source_version"]==view["source_version"]],"snapshot_sha256":snapshot["snapshot_sha256"]}
        view["table_snapshot_sha256"]=snapshot["snapshot_sha256"]
    return snapshot
