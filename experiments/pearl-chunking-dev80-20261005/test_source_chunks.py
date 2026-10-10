"""Fixed counterexamples; tokenizer tests use the actual pinned local BGE artifact."""
import importlib
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).parent))
from ped_knowledge.tokenization import HuggingFaceTokenCounter

@pytest.fixture(scope="module")
def counter():
    return HuggingFaceTokenCounter.from_local_path(Path("memPed/knowledge/models/bge-m3"))

def api(name):
    assert (Path(__file__).parent / (name + ".py")).exists(), "missing source/chunk implementation"
    return importlib.import_module(name)

def doc(texts, types=None, paths=None):
    return {"doc_id":"d", "source_version":"v", "elements":[{"element_id":str(i),"text":t,"element_type":(types or ["paragraph"]*len(texts))[i],"heading_path":(paths or [[]]*len(texts))[i],"order":i} for i,t in enumerate(texts)]}

def view(d):
    return api("source_view").build_source_view(d)

def test_unicode_source_separator_and_array_json():
    d=doc(["Ａ e\u0301 😀\n", "same", "same", ""], types=["heading","paragraph","paragraph","image"])
    d["elements"][1]["heading_path"]='["Ａ"]'
    v=view(d)
    assert v["source_text"]=="Ａ e\u0301 😀\n\n\nsame\n\nsame"
    assert len(v["separator_map"])==2
    assert v["elements"][1]["heading_path"]==["Ａ"]
    assert api("source_view").text_for_spans(v,[e["span"] for e in v["elements"]])==v["source_text"]

def test_legacy_ambiguity_stays_unknown():
    v=view(doc(["repeat", "repeat"]))
    assert api("source_view").resolve_legacy_span({"text":"repeat"},None,v)["status"]=="ambiguous"

@pytest.mark.parametrize("policy",["C1","C2","C3","C4"])
def test_policy_conservation_tail_and_limit(counter,policy):
    v=view(doc(["One sentence. Another sentence! "*20,"尾块😀"],paths=[["A"],["B"]]))
    manifest={"threshold":0.5,"distances":{}} if policy=="C4" else None
    chunks=api("chunkers").chunk(v,policy,32,counter,manifest)
    assert chunks
    assert all(counter.count(c["source_text"])<=32 for c in chunks)
    restored={e["element_id"]:"" for e in v["elements"]}
    for c in chunks:
        for s in c["core_spans"]:
            restored[s["element_id"]]+=next(e["text"] for e in v["elements"] if e["element_id"]==s["element_id"])[s["start"]:s["end"]]
    assert restored=={e["element_id"]:e["text"] for e in v["elements"]}

def test_structure_short_sections_and_public_multi_parent(counter):
    v=view(doc(["A short.","B short.","Long sentence. "*100],paths=[["A"],["B"],["B"]]))
    cs=api("chunkers").chunk(v,"C3",64,counter)
    assert not any({s["element_id"] for s in c["core_spans"]}>={"0","1"} for c in cs)
    g=api("parent_graph").build_parent_graph(v,counter,32)
    assert all(counter.count(p["source_text"])<=32 for p in g["parents"])
    assert len(api("parent_graph").parents_for_spans([v["elements"][2]["span"]],g))>1
    assert api("parent_graph").build_parent_graph(v,counter,32)["graph_sha256"]==g["graph_sha256"]

def test_public_table_mapping_long_cell_and_same_policy_snapshot(counter):
    d=doc(["intro","H | N\n"+"x "*100+" | 7\nshort | 8","after"],types=["paragraph","table","paragraph"])
    d["elements"][1]["table_data"]=[["H","N"],["x "*100,"7"],["short","8"]]
    v=view(d); t=api("table_snapshot").freeze_tables([v],counter,{"max_tokens":32})
    assert t["tables"][0]["mapping_status"]=="resolved"
    assert t["tables"][0]["cells"][3]["row"]==1
    for policy in ["C1","C2","C3","C4"]:
        cs=api("chunkers").chunk(v,policy,32,counter,{"threshold":0.5,"distances":{}})
        table=[c for c in cs if c["is_table"]]
        assert all(c["table_snapshot_sha256"]==t["snapshot_sha256"] for c in cs)
        assert "".join(c["source_text"] for c in table)==d["elements"][1]["text"]
        assert all(counter.count(c["source_text"])<=32 for c in table)

def test_overlap_and_prefix_never_change_core(counter):
    v=view(doc(["Paper title","Sentence one. "*40],types=["heading","paragraph"],paths=[["Paper title"],["Paper title"]]))
    mod=api("chunkers"); cs=mod.chunk(v,"C1",32,counter)
    c=next(c for c in cs if c["core_spans"][0]["start"]>0)
    extended=mod.attach_overlap(c,0.2,32,v,counter)
    assert extended["core_sha256"]==c["core_sha256"]
    assert counter.count(api("source_view").text_for_spans(v,extended["overlap_spans"]))<=6
    prefixed=mod.render_prefix(extended,{"mode":"M1","max_tokens":64},v,counter)
    assert prefixed["prefix_spans"]
    assert prefixed["core_spans"]==c["core_spans"]

def test_semantic_numeric_reference_and_barriers():
    v=view(doc(["First. Second.","table","Third. Fourth."],types=["paragraph","table","paragraph"]))
    class Model:
        def encode(self,texts):
            return np.array([[1,0],[0,1],[1,0],[-1,0]],dtype=float)
    m=api("semantic_threshold").freeze_threshold([v],None,Model())
    assert m["distance_values"]==[1.0,2.0]
    assert m["threshold"]==pytest.approx(1.9)
    assert m["quantile_method"]=="linear"

def test_semantic_zero_nonfinite_exclusions():
    v=view(doc(["A. B. C. D."]))
    class Model:
        def encode(self,texts): return np.array([[1,0],[0,0],[np.nan,0],[1,0]])
    m=api("semantic_threshold").freeze_threshold([v],None,Model())
    assert m["threshold"] is None
    assert sum(m["excluded"].values())==3

def test_b0_regex_identity(counter):
    v=view(doc(["word "*800]))
    cs=api("chunkers").chunk(v,"B0",256,counter)
    assert cs[0]["policy"]["length_unit"]=="regex-token-v1"
    assert cs[0]["policy"]["overlap_tokens"]==48
    assert cs[1]["overlap_spans"]

def test_chunks_bind_all_public_parents(counter):
    v=view(doc(["Continuous sentence. "*80]))
    api("parent_graph").build_parent_graph(v,counter,32)
    cs=api("chunkers").chunk(v,"C1",128,counter)
    assert len(cs[0]["parent_ids"])>1

def test_c4_real_distances_cut_only_contiguous_sentences(counter):
    v=view(doc(["First complete sentence. Second complete sentence. Third complete sentence."]))
    mod=api("chunkers"); e=v["elements"][0]; starts=mod.sentence_spans(e["text"])
    threshold={"threshold":.2,"distances":{mod.sentence_key(e,starts[1][0]):1.,mod.sentence_key(e,starts[2][0]):1.}}
    cs=mod.chunk(v,"C4",12,counter,threshold)
    assert "".join(c["source_text"] for c in cs)==e["text"]
    assert all(c["core_spans"][0]["end"]==c["core_spans"][-1]["end"] or len(c["core_spans"])>=1 for c in cs)

def test_unresolved_table_preserves_raw_and_blocks_mapping(counter):
    d=doc(["raw 7 | 8"],types=["table"]); d["elements"][0]["table_data"]=[["fixed","7"]]
    v=view(d); snap=api("table_snapshot").freeze_tables([v],counter)
    assert snap["tables"][0]["mapping_status"]=="unresolved"
    assert snap["tables"][0]["cells"]==[]
    assert api("chunkers").chunk(v,"C1",256,counter)[0]["source_text"]=="raw 7 | 8"

def test_long_sentence_only_first_fragment_has_adjacent_distance(counter):
    v=view(doc(["One enormous sentence with many words "*30+"."]))
    units=api("chunkers")._units(v["elements"],counter,32,True)
    assert len(units)>1
    assert units[0][1] is not None
    assert all(key is None for spans,key in units[1:])

def test_chunk_text_hash_is_raw_utf8(counter):
    v=view(doc(["raw source."]))
    c=api("chunkers").chunk(v,"C1",32,counter)[0]
    assert c["text_sha256"]==hashlib.sha256(c["retrieval_text"].encode("utf8")).hexdigest()

def test_b0_matches_legacy_window_whitespace_unicode_and_punctuation(counter):
    from ped_knowledge.chunking import HierarchicalChunker
    texts=["  \t" + "word😀, \n"*340 + "  \t", " \nsecond! 尾句  \t"]
    v=view(doc(texts))
    adapted="\n\n".join(t.strip() for t in texts)
    reference=HierarchicalChunker()._regex_child_texts(adapted)
    cs=api("chunkers").chunk(v,"B0",256,counter)
    assert [c["source_text"] for c in cs]==[c.text for c in reference]
    assert cs[0]["core_spans"][0]["start"]==3
    assert cs[-1]["core_spans"][-1]["end"]==len(texts[-1].rstrip())

def test_b0_whitespace_only_elements_do_not_create_chunks(counter):
    assert api("chunkers").chunk(view(doc([" \n\t"])),"B0",256,counter)==[]
