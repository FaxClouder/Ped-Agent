"""Fixed assembly/support counterexamples, independent of models and old results."""
import importlib.util
from pathlib import Path
import sys
import pytest
HERE=Path(__file__).parent
sys.path.insert(0,str(HERE))
from assemble import assemble, union_spans, serialize
from support import visible_support, export_source_support
from score import score_support
from review import export_visible_packets, validate_review

def span(d='d',e='e',start=0,end=4):
    return dict(doc_id=d,source_version='v',element_id=e,start=start,end=end)

def view(d='d', text='甲😀ab'):
    return dict(doc_id=d,source_version='v',elements=[dict(element_id='e',text=text,order=0,heading_path=[],element_type='paragraph')])

def child(s,id='c'):
    return dict(chunk_id=id,core_spans=[s],overlap_spans=[],prefix_spans=[])

class Counter:
    def count(self,t): return len(t)
    def offsets(self,t): return [(i,i+1) for i in range(len(t))]

def test_source_union_not_text_dedup():
    a=span(end=3); b=span(start=2,end=4); other=span(d='other')
    assert union_spans([a,b,other]) == [span(),other]
    out=assemble([child(a),child(b,'c2'),child(other,'c3')],[view(),view('other')],{},'P0',10000,'fixed_budget_main',Counter())
    assert len(out['deduplicated']['units'])==3
    assert out['deduplicated']['units'][1]['spans']==[span(start=3,end=4)]
    assert out['final']['units'][2]['text']=='甲😀ab'

def test_top100_and_top10_distinct():
    rows=[child(span(d=str(i)),str(i)) for i in range(12)]
    views=[view(str(i)) for i in range(12)]
    main=assemble(rows,views,{},'P0',10000,'fixed_budget_main',Counter())
    diag=assemble(rows,views,{},'P0',10000,'seed10_diagnostic',Counter())
    assert len(main['raw']['units'])==12 and len(diag['raw']['units'])==10
    assert main['panel_id']!=diag['panel_id']

def test_budget_maximal_nonmonotonic_and_stop():
    class Weird(Counter):
        def count(self,t):
            if t.endswith('甲😀a'): return 20
            if t.endswith('甲😀'): return 200
            return len(t)
    rows=[child(span()),child(span(d='other'),'later')]
    out=assemble(rows,[view(),view('other')],{},'P0',20,'fixed_budget_main',Weird())
    assert len(out['final']['units'])==1
    assert out['final']['units'][0]['text']=='甲😀a'
    assert out['final']['units'][0]['spans']==[span(end=3)]
    assert out['final']['token_count']==20
    assert out['truncation'][0]['retained_characters']==3

def test_header_counted_and_empty_budget():
    out=assemble([child(span())],[view()],{},'P0',1,'fixed_budget_main',Counter())
    assert not out['final']['units'] and out['final']['token_count']==0

def test_p1_same_section_neighbors_and_p2_multi_parent():
    elems=[dict(element_id=str(i),text='ab',order=i,heading_path=['s' if i<3 else 't'],element_type='paragraph') for i in range(4)]
    v=dict(doc_id='d',source_version='v',elements=elems,paragraphs=elems)
    c=child(span(e='1',end=1))
    one=assemble([c],[v],{},'P1',10000,'fixed_budget_main',Counter())
    assert {s['element_id'] for s in one['final']['units'][0]['spans']}=={'0','1','2'}
    graph=dict(parents=[dict(parent_id='p1',spans=[span(e='0',end=2),span(e='1',end=1)]),dict(parent_id='p2',spans=[span(e='1',start=1,end=2),span(e='2',end=2)])])
    c=child(span(e='1',end=2)); c['parent_ids']=['p1','p2']
    two=assemble([c],[v],graph,'P2',10000,'fixed_budget_main',Counter())
    assert {s['element_id'] for s in two['final']['units'][0]['spans']}=={'0','1','2'}

def test_reviewed_full_span_only_and_union_across_chunks():
    mapping=dict(requirements=[dict(requirement_id='a',evidence_groups=[dict(status='yes',necessary_spans=[span()],reviewer_id='r',rationale='Full scope reviewed')])])
    assert visible_support([span(end=2),span(start=2,end=4)],mapping)=={'a':'yes'}
    assert visible_support([span(end=3)],mapping)=={'a':'unknown'}
    mapping['requirements'][0]['evidence_groups'][0]['reviewer_id']=''
    assert visible_support([span()],mapping)=={'a':'unknown'}

def test_three_valued_and_or_and_false():
    assert score_support([['a','b'],['c']],{'a':'yes','b':'unknown','c':'no'})['sufficient']=='unknown'
    assert score_support([['a','b'],['c']],{'a':'no','b':'unknown','c':'yes'})['sufficient']=='yes'
    assert score_support([['a','b']],{'a':'no','b':'unknown'})['sufficient']=='no'

def test_blind_packet_and_review_binding():
    context=assemble([child(span())],[view()],{},'P0',1000,'fixed_budget_main',Counter())
    requirements=[dict(requirement_id='a',description='Explain scope',evidence_groups=[])]
    packet=export_visible_packets(context,requirements)
    assert 'ranking' not in str(packet) and 'P0' not in str(packet)
    review=dict(packet_id=packet['packet_id'],packet_sha256=packet['packet_sha256'],reviewer_id='agent',judgments={'a':dict(status='unknown',rationale='Insufficient scope',necessary_spans=[])})
    validate_review(packet,review)
    review['packet_sha256']='bad'
    with pytest.raises(ValueError): validate_review(packet,review)

def test_prefix_never_visible_support_and_version_bound():
    c=child(span(end=2)); c['prefix_spans']=[span(start=2,end=4)]
    out=assemble([c],[view()],{},'P0',1000,'fixed_budget_main',Counter())
    assert out['final']['units'][0]['text']=='甲😀'
    wrong=span(); wrong['source_version']='new'
    mapping={'requirements':[{'requirement_id':'a','evidence_groups':[{'status':'yes','necessary_spans':[wrong],'reviewer_id':'r','rationale':'scope reviewed'}]}]}
    assert visible_support([span()],mapping)=={'a':'unknown'}

def test_pending_anchors_never_inherit_legacy_true():
    gold={'intents':[{'intent_id':'q','query':'what','main_stratum':'single_source','atoms':[{'atom_id':'a','source_id':'d','anchor_text':'甲😀','supports':'fact'}],'requirements':[{'requirement_id':'r','claim':'fact','support_bundles':[['a']]}],'evidence_groups':[{'requirements':['r']}]}]}
    exported=export_source_support(gold,{},legacy_review={'a':'yes'},views=[view()])
    req=exported['records'][0]['requirements'][0]
    assert req['evidence_groups'][0]['anchor_candidates'][0]['unique']
    assert visible_support([span()],{'requirements':[req]})=={'r':'unknown'}

def test_separator_truncation_is_reversible():
    v=view(text='abc'); v['elements'].append(dict(element_id='f',text='def',heading_path=[],order=1,element_type='paragraph'))
    c=child(span(end=3)); c['core_spans'].append(span(e='f',end=3))
    baseline=assemble([c],[v],{},'P0',10000,'fixed_budget_main',Counter())
    u=baseline['final']['units'][0]
    # Fit first source only; separators cannot claim support or produce dangling text.
    from assemble import prefix_unit,views_by_id
    assert prefix_unit(u,4,views_by_id([v])) is None
    p=prefix_unit(u,6,views_by_id([v]))
    assert p['text']=='abc\n\nd' and p['spans'][-1]['end']==1

def test_failure_retains_denominator():
    from score import aggregate
    a=aggregate([{'sufficient':'yes','failure':None},{'sufficient':'unknown','failure':'api_failed'}])
    assert a['n']==2 and a['complete_group_lower']==.5 and a['failure_n']==1

def test_packet_content_drift_rejected():
    context=assemble([child(span())],[view()],{},'P0',1000,'fixed_budget_main',Counter())
    packet=export_visible_packets(context,[{'requirement_id':'a','description':'Fact'}])
    review={'packet_id':packet['packet_id'],'packet_sha256':packet['packet_sha256'],'reviewer_id':'r','judgments':{'a':{'status':'unknown','rationale':'No scope','necessary_spans':[]}}}
    packet['visible_units'][0]['text']='tampered'
    with pytest.raises(ValueError):validate_review(packet,review)
