"""Independent synthetic saved-artifact counterexamples; never executes models."""
from copy import deepcopy
import itertools
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from assemble import assemble, digest
from runtime import cache_identity, sha
from score import aggregate
from verify import check_visible_unit, independent_source_support, independent_truth
import evaluate
import smoke
import verify


def span(start=0, end=4, version="v"):
    return dict(doc_id="d", source_version=version, element_id="e", start=start, end=end)


def mapping_record(intent="q0"):
    requirements=[]
    for rid, s in (("a", span()), ("b", span(4, 8))):
        requirements.append(dict(requirement_id=rid, evidence_groups=[dict(status="yes", necessary_spans=[s], reviewer_id="synthetic", rationale="fixed semantic certificate")]))
    return dict(intent_id=intent, requirements=requirements, groups=[["a", "b"]])


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf8")


def dump_rows(path, records):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records)+"\n", encoding="utf8")


class Counter:
    fingerprint="synthetic-unicode-character-counter"
    def count(self, text): return len(text)
    def offsets(self, text): return [(i, i+1) for i in range(len(text))]


@pytest.fixture
def saved_run(tmp_path, monkeypatch):
    monkeypatch.setattr(smoke, "counter", Counter)
    views=[dict(doc_id="d", source_version="v", elements=[dict(doc_id="d", source_version="v", element_id="e", text="甲😀abWXYZ", element_type="paragraph", heading_path=[], order=0)])]
    parents={"parents":[dict(parent_id="p",spans=[span()],source_text="甲😀ab")]}
    dump(tmp_path/"source-views-prepared.json",views)
    dump(tmp_path/"public-parent-graph.json",parents)
    dump(tmp_path/"table-snapshot.json",{"tables":[]})
    queries=[dict(intent_id=f"q{i}",query=f"query {i}") for i in range(8)]
    dump_rows(tmp_path/"queries.jsonl",queries)
    children=[dict(chunk_id=f"c{i:03}", core_spans=[span()], overlap_spans=[], prefix_spans=[], text="甲😀ab",source_text="甲😀ab",retrieval_text="甲😀ab") for i in range(100)]
    directory=tmp_path/"index-C1-L384-O0-M0";directory.mkdir()
    dump_rows(directory/"child_chunks.jsonl",children)
    configuration={"source":sha(tmp_path/"source-views-prepared.json"),"parent":sha(tmp_path/"public-parent-graph.json"),"table":sha(tmp_path/"table-snapshot.json"),"tokenizer":Counter.fingerprint}
    dump(directory/"manifest.json",{"configuration":configuration,"output_sha256":{"child_chunks.jsonl":sha(directory/"child_chunks.jsonl")}})
    rankings=[];contexts=[]
    for qi,q in enumerate(queries):
        sparse=[dict(c,rank=i+1,score=1/(61+i)) for i,c in enumerate(children)]
        fused=[dict(c,rank=i+1,score=2/(61+i)) for i,c in enumerate(children)]
        ranking=dict(intent_id=q["intent_id"],status="success",results={"R1":deepcopy(sparse),"R2":deepcopy(sparse),"R3":deepcopy(fused),"R4":[dict(r,score=r["score"]+qi*.001) for r in fused]},rrf_union=[{"chunk_id":c["chunk_id"],"score":2/(61+i)} for i,c in enumerate(children)],index_sha256=sha(directory/"manifest.json"),query_sha256=cache_identity(q),source_sha256=configuration["source"],parent_sha256=configuration["parent"])
        rankings.append(ranking)
        for P,B,panel in itertools.product(("P0","P1","P2"),(4096,8192),("fixed_budget_main","seed10_diagnostic")):
            record=assemble(ranking["results"]["R4"],views,parents,P,B,panel,Counter());record["intent_id"]=q["intent_id"];contexts.append(record)
    dump_rows(tmp_path/"rankings.jsonl",rankings);dump_rows(tmp_path/"contexts.jsonl",contexts)
    dump_rows(tmp_path/"retrieval-audits.jsonl",[dict(intent_id=q["intent_id"],dense={"actual_forward_inputs_verified":True},rerank=[{"actual_forward_inputs_verified":True} for _ in range(100)]) for q in queries])
    calibration=tmp_path/"calibration-r02";calibration.mkdir()
    dump(calibration/"semantic-threshold.json",{"threshold":.9,"distance_values":[0.,1.]})
    mapping={"records":[mapping_record(q["intent_id"]) for q in queries]};mapping["map_sha256"]=digest(mapping)
    map_path=tmp_path/"map.json";dump(map_path,mapping)
    scored=evaluate.run(tmp_path,map_path);score_path=tmp_path/"scores.json";dump(score_path,scored)
    return tmp_path, score_path, scored, rankings, contexts


def resummarize(scored):
    cells={r["cell"] for r in scored["details"]}
    scored["summaries"]={cell:aggregate([r for r in scored["details"] if r["cell"]==cell]) for cell in cells}


def test_saved_fixture_is_valid_before_tampering(saved_run):
    output,path,*_=saved_run
    assert verify.run(output,path)["status"]=="passed"


@pytest.mark.parametrize("tamper",["groups","omit_unknown_detail","duplicate_context","rank_query","rank_child","offset","coverage_bounds","r3_order"])
def test_saved_artifact_tampering_must_be_rejected(saved_run,tamper):
    output,path,scored,rankings,contexts=saved_run
    if tamper=="groups":
        # A present condition must not replace the frozen AND requirement.
        for result in scored["details"]:
            result["groups"]=[["a"]];result["sufficient"]="yes"
        resummarize(scored);dump(path,scored)
    elif tamper=="omit_unknown_detail":
        scored["details"].pop();resummarize(scored);dump(path,scored)
    elif tamper=="duplicate_context":
        contexts[-1]=deepcopy(contexts[-2]);dump_rows(output/"contexts.jsonl",contexts)
        scored=evaluate.run(output,Path(scored["mapping_path"]));dump(path,scored)
    elif tamper=="rank_query":
        rankings[0]["query_sha256"]="stale-query-sha";dump_rows(output/"rankings.jsonl",rankings)
        scored=evaluate.run(output,Path(scored["mapping_path"]));dump(path,scored)
    elif tamper=="rank_child":
        for method in rankings[0]["results"]:
            rankings[0]["results"][method][0]["core_spans"]=[span(4,8)]
        dump_rows(output/"rankings.jsonl",rankings)
        scored=evaluate.run(output,Path(scored["mapping_path"]));dump(path,scored)
    elif tamper=="r3_order":
        rankings[0]["results"]["R3"].reverse()
        dump_rows(output/"rankings.jsonl",rankings)
        scored=evaluate.run(output,Path(scored["mapping_path"]));dump(path,scored)
    elif tamper=="offset":
        contexts[0]["final"]["units"][0]["spans"][0]["end"]=3
        dump_rows(output/"contexts.jsonl",contexts)
    else:
        scored["details"][0]["coverage_lower"]=99
        scored["details"][0]["coverage_upper"]=-1
        dump(path,scored)
    with pytest.raises(ValueError):
        verify.run(output,path)


def test_independent_source_interval_union_cross_blocks_and_gap():
    mapping=mapping_record();mapping["requirements"]=mapping["requirements"][:1]
    assert independent_source_support([span(2,4),span(0,2)],mapping)=={"a":"yes"}
    assert independent_source_support([span(0,1),span(2,4)],mapping)=={"a":"unknown"}
    assert independent_source_support([span(version="other")],mapping)=={"a":"unknown"}
    mapping["requirements"][0]["evidence_groups"][0]["reviewer_id"]=""
    assert independent_source_support([span()],mapping)=={"a":"unknown"}


def test_independent_and_or_fixed_truth_table():
    for a,b,c in itertools.product(("yes","no","unknown"),repeat=3):
        left="no" if "no" in (a,b) else "yes" if a==b=="yes" else "unknown"
        expected="yes" if left=="yes" or c=="yes" else "no" if left==c=="no" else "unknown"
        assert independent_truth([["a","b"],["c"]],dict(a=a,b=b,c=c))==expected


def test_saved_unicode_offset_tamper_rejected():
    views=[dict(doc_id="d",source_version="v",elements=[dict(element_id="e",text="甲😀abWXYZ")])]
    unit={"spans":[span()],"text":"甲😀ab"}
    assert check_visible_unit(views,unit)
    unit["spans"][0]["start"]=1
    with pytest.raises(ValueError):check_visible_unit(views,unit)


@pytest.mark.parametrize("field", ["threshold", "RRF", "R3"])
def test_saved_nonfinite_numeric_fields_rejected(saved_run, field):
    output, path, scored, rankings, _ = saved_run
    if field == "threshold":
        dump(output/"calibration-r02/semantic-threshold.json", {"threshold":float("nan"),"distance_values":[0.,1.]})
    else:
        collection = rankings[0]["rrf_union"] if field == "RRF" else rankings[0]["results"]["R3"]
        collection[0]["score"] = float("nan")
        dump_rows(output/"rankings.jsonl", rankings)
        scored=evaluate.run(output,Path(scored["mapping_path"]));dump(path,scored)
    with pytest.raises(ValueError):
        verify.run(output,path)
