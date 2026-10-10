import copy
from e3_cached import project_p0, memoized_assembly
import assemble as a

class Counter:
    def count(self,text):return len(text)

def test_project_top10_preserves_exact_full_assembly():
    c=Counter();v=dict(doc_id='d',source_version='v',elements=[dict(element_id='e',text='abcdefghij'*30)])
    ranked=[dict(chunk_id=str(i),core_spans=[dict(doc_id='d',source_version='v',element_id='e',start=i*10,end=(i+1)*10)]) for i in range(20)]
    for B in (200,2000):
        full=a.assemble(ranked,[v],[],'P0',B,'fixed_budget_main',c)
        expected=a.assemble(ranked,[v],[],'P0',B,'seed10_diagnostic',c)
        actual=project_p0(full,ranked,[v],[],B,c)
        assert all(actual[k]==expected[k] for k in actual if k!='assembly_seconds')

def test_memo_preserves_budget_and_source_dedup():
    c=Counter();v=dict(doc_id='d',source_version='v',elements=[dict(element_id='e',text='abcdefghij'*30)])
    ranked=[dict(chunk_id=str(i),core_spans=[dict(doc_id='d',source_version='v',element_id='e',start=i*10,end=(i+2)*10)]) for i in range(12)]
    original=[a.assemble(ranked,[v],[],'P0',B,panel,c) for B in (200,2000) for panel in ('fixed_budget_main','seed10_diagnostic')]
    with memoized_assembly(c):
        cached=[a.assemble(ranked,[v],[],'P0',B,panel,c) for B in (200,2000) for panel in ('fixed_budget_main','seed10_diagnostic')]
    assert all(all(x[k]==y[k] for k in x if k!='assembly_seconds') for x,y in zip(original,cached))

def test_full_p1_p2_cell_order_with_different_expansions():
    c=Counter();v=dict(doc_id='d',source_version='v',elements=[dict(element_id=str(i),text=('paragraph'+str(i))*15,heading_path=['s']) for i in range(4)])
    spans=[dict(doc_id='d',source_version='v',element_id=str(i),start=0,end=len(e['text'])) for i,e in enumerate(v['elements'])]
    ranked=[dict(chunk_id='a',core_spans=[dict(spans[1],start=10,end=30)]),dict(chunk_id='b',core_spans=[dict(spans[2],start=10,end=30)])]
    parents=[dict(spans=spans)]
    cells=[(P,B,panel) for P in ('P1','P2') for B in (300,700) for panel in ('fixed_budget_main','seed10_diagnostic')]
    original=[a.assemble(ranked,[v],parents,P,B,panel,c) for P,B,panel in cells]
    with memoized_assembly(c):cached=[a.assemble(ranked,[v],parents,P,B,panel,c) for P,B,panel in cells]
    assert all(all(x[k]==y[k] for k in x if k!='assembly_seconds') for x,y in zip(original,cached))
