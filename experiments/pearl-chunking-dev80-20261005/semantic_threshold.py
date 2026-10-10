"""Corpus-only adjacent sentence calibration; no query or Gold parameters."""
import hashlib
import numpy as np
from chunkers import sentence_spans,sentence_key,SENTENCE_SPLITTER_VERSION
from source_view import digest,make_span


def extract_sentences(views,sentence_splitter=None):
    splitter=sentence_splitter or sentence_spans
    records=[];pairs=[];excluded={"empty":0,"zero_norm":0,"nonfinite":0}
    for view in views:
        lookup={e["element_id"]:e for e in view["elements"]}
        for run in view["barrier_runs"]:
            previous=None
            for eid in run:
                e=lookup[eid]
                if e["element_type"]=="table":previous=None;continue
                for a,b in splitter(e["text"]):
                    text=e["text"][a:b]
                    if not text.strip():
                        excluded["empty"]+=1;previous=None;continue
                    index=len(records)
                    records.append({"text":text,"span":make_span(e,a,b),"sentence_id":sentence_key(e,a)})
                    if previous is not None:pairs.append((previous,index))
                    previous=index
    return records,pairs,excluded


def freeze_threshold(views,sentence_splitter,model,quantile=.9,method="linear"):
    if method!="linear":raise ValueError("quantile method frozen to linear")
    records,pairs,excluded=extract_sentences(views,sentence_splitter)
    output=model.encode([r["text"] for r in records]) if records else []
    vectors=np.asarray(output.get("dense_vecs") if isinstance(output,dict) else output,dtype=np.float64)
    if len(vectors)!=len(records):raise ValueError("sentence vector cardinality mismatch")
    distances={};values=[];pair_records=[]
    for a,b in pairs:
        left,right=vectors[a],vectors[b]
        if not np.isfinite(left).all() or not np.isfinite(right).all():excluded["nonfinite"]+=1;continue
        ln,rn=np.linalg.norm(left),np.linalg.norm(right)
        if ln==0 or rn==0:excluded["zero_norm"]+=1;continue
        d=float(1-np.clip(np.dot(left,right)/(ln*rn),-1,1))
        values.append(d);distances[records[b]["sentence_id"]]=d
        pair_records.append({"left":records[a]["sentence_id"],"right":records[b]["sentence_id"],"distance":d})
    vector_identity = hashlib.sha256(str((vectors.dtype.str,vectors.shape)).encode("ascii") + np.ascontiguousarray(vectors).tobytes()).hexdigest()
    manifest={"version":"adjacent-semantic-threshold-v1","threshold":float(np.quantile(values,quantile,method=method)) if values else None,"quantile":quantile,"quantile_method":method,"sentences":records,"sentence_sha256":digest(records),"pairs":pair_records,"distances":distances,"distance_values":values,"excluded":excluded,"splitter_version":SENTENCE_SPLITTER_VERSION,"view_sha256s":[v["view_sha256"] for v in views],"vectors_sha256":vector_identity,"vectors_hash_format":"numpy-dtype-shape-ascii-plus-contiguous-bytes-v1","model_identity":getattr(model,"identity",type(model).__name__)}
    manifest["manifest_sha256"]=digest(manifest)
    return manifest
