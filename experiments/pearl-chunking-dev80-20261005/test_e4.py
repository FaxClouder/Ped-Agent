"""Session 5B fixed examples: M0/M1 rule, independent prefix derivation, prefix isolation."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent))
from ped_knowledge.tokenization import HuggingFaceTokenCounter

@pytest.fixture(scope="module")
def counter():
    return HuggingFaceTokenCounter.from_local_path(Path("memPed/knowledge/models/bge-m3"))

def doc(texts, types, paths):
    return {"doc_id":"d","source_version":"v","elements":[{"element_id":str(i),"text":t,"element_type":types[i],"heading_path":paths[i],"order":i} for i,t in enumerate(texts)]}

def view(d):
    import source_view
    return source_view.build_source_view(d)

def row(c,yes,unknown,cegr):
    return dict(configuration_id=c,yes=yes,no=80-yes-unknown,unknown=unknown,cegr10_yes=cegr)

def test_rule_ties_prefer_m0_and_threats_keep_pending():
    from e4_score import choose,M0,M1
    d=choose([row(M0,57,1,63),row(M1,57,0,63)])
    assert d['order'][0]==M0 and d['status']=='pending_review' and d['threats']==[M1]
    d=choose([row(M0,50,0,60),row(M1,57,2,61)])
    assert d['selected']==M1 and d['status']=='frozen' and d['threats']==[]
    d=choose([row(M0,55,3,60),row(M1,57,0,61)])
    assert d['selected'] is None and d['threats']==[M0]
    d=choose([row(M0,57,0,62),row(M1,57,0,63)])
    assert d['order'][0]==M1 and d['threats']==[M0]

def test_independent_prefix_equals_frozen_render_prefix(counter):
    import chunkers
    from verify_e4 import expected_prefix
    long_leaf="Section "+"word "*80
    v=view(doc(["Paper title","1. Intro","1.1 Setup",long_leaf,"Body sentence one. "*30],
               ["title","heading","heading","heading","paragraph"],
               [[],["Paper title"],["Paper title","1. Intro"],["Paper title","1. Intro","1.1 Setup"],["Paper title","1. Intro","1.1 Setup",long_leaf]]))
    for c in chunkers.chunk(v,"C2",64,counter):
        if c["is_table"]:continue
        got=chunkers.render_prefix(c,{"mode":"M1","max_tokens":64},v,counter)
        assert got["prefix_spans"]==expected_prefix(c,v,counter)
        if got["prefix_spans"]:
            assert counter.count(got["prefix_text"])<=64
            assert got["retrieval_text"]==got["prefix_text"]+"\n\n"+got["source_text"]
        assert got["core_spans"]==c["core_spans"] and got["source_text"]==c["source_text"]

def test_prefix_never_enters_p0_context(counter):
    import chunkers
    from assemble import assemble
    v=view(doc(["Unique Title Words","Body sentence one. "*20],["title","paragraph"],[[],["Unique Title Words"]]))
    c=[x for x in chunkers.chunk(v,"C2",64,counter) if x["core_spans"][0]["element_id"]=="1"][0]
    m1=chunkers.render_prefix(c,{"mode":"M1","max_tokens":64},v,counter)
    assert "Unique Title Words" in m1["retrieval_text"]
    ctx=assemble([m1],[v],{"parents":[]},"P0",4096,"fixed_budget_main",counter)
    ctx0=assemble([c],[v],{"parents":[]},"P0",4096,"fixed_budget_main",counter)
    assert "Unique Title Words" not in ctx["final"]["serialized_context"]
    assert ctx["final"]["units"][0]["spans"]==ctx0["final"]["units"][0]["spans"]
