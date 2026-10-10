"""E2 overlap counterexamples with the pinned local BGE tokenizer."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
from ped_knowledge.tokenization import HuggingFaceTokenCounter
import chunkers
from source_view import build_source_view,text_for_spans

@pytest.fixture(scope='module')
def counter():
    return HuggingFaceTokenCounter.from_local_path(Path('memPed/knowledge/models/bge-m3'))

def doc(texts,paths):
    return build_source_view({'doc_id':'d','source_version':'v','elements':[{'element_id':str(i),'text':t,'element_type':'paragraph','heading_path':p,'order':i} for i,(t,p) in enumerate(zip(texts,paths))]})

def test_zero_overlap_is_byte_identical_alias(counter):
    v=doc(['Alpha beta gamma. '*30],[['A']])
    for c in chunkers.chunk(v,'C2',32,counter):
        assert chunkers.attach_overlap(c,0.0,32,v,counter)==c

@pytest.mark.parametrize('r',[0.1,0.2])
def test_overlap_limit_core_and_c3_barrier(counter,r):
    v=doc(['First section sentence. '*20,'Second section sentence. '*20],[['S1'],['S2']])
    cs=chunkers.chunk(v,'C3',64,counter)
    for c in cs:
        o=chunkers.attach_overlap(c,r,64,v,counter)
        assert o['core_spans']==c['core_spans'] and o['core_sha256']==c['core_sha256']
        if o['overlap_spans']:
            assert counter.count(text_for_spans(v,o['overlap_spans']))<=int(r*64)
            # C3 overlap never crosses the section boundary.
            assert {s['element_id'] for s in o['overlap_spans']}=={c['core_spans'][0]['element_id']}
    first_s2=next(c for c in cs if c['core_spans'][0]['element_id']=='1')
    assert chunkers.attach_overlap(first_s2,r,64,v,counter)['overlap_spans']==[]

def test_e2_grid_is_limited_to_frozen_core_candidates():
    import e2
    assert set(e2.CONFIGS)=={'C2-L384-O10-M0','C2-L384-O20-M0','C3-L256-O10-M0','C3-L256-O20-M0'}
    assert e2.configurations()['C2-L384-O20-M0']==('C2',384) and e2.STRATEGY=='P0'

def test_dedup_removes_overlap_repeated_by_neighbor(counter):
    from assemble import assemble
    v=doc(['One two three four five six. '*12],[['A']])
    cs=[chunkers.attach_overlap(c,0.2,48,v,counter) for c in chunkers.chunk(v,'C2',48,counter)]
    ranked=[dict(c,score=1.0) for c in cs[:3]]
    ctx=assemble(ranked,[v],{'parents':[]},'P0',4096,'fixed_budget_main',counter)
    seen=[]
    for u in ctx['deduplicated']['units']:
        for s in u['spans']:
            assert all(not(s['element_id']==t['element_id'] and s['start']<t['end'] and t['start']<s['end']) for t in seen)
            seen.append(s)

@pytest.mark.parametrize('C',['C2','C3'])
@pytest.mark.parametrize('r',[0.1,0.2,0.5])
def test_batched_overlap_equals_original(counter,C,r):
    import e2
    v=doc(['Short one. A much longer second sentence follows here, with clauses. '*6,'Tail para. Another! Ünïcode — dash. '*5,'Final.'],[['A'],['A'],['B']])
    for c in chunkers.chunk(v,C,40,counter):
        assert e2.attach_overlap_batched(c,r,40,v,counter)==chunkers.attach_overlap(c,r,40,v,counter)

TRICKY=['Alpha beta. ','—— !! ','​​zero​width ','中文句子。','x\x1cy ','\xa0nbsp　ideo ','ﬁne café ','12.5% ','\n\n','\t',' a',"don't. ",'Ü','!?']

def test_word_lower_bound_is_sound(counter):
    import random,bisect,e2
    rng=random.Random(20261006);base=counter.count('')
    for _ in range(300):
        text=''.join(rng.choice(TRICKY) for _ in range(rng.randint(1,25)))
        words=e2._word_starts(text)
        for a in range(len(text)+1):
            assert counter.count(text[a:])>=base+len(words)-bisect.bisect_left(words,a),(text,a)

@pytest.mark.parametrize('limit',[2,3,5,8,25,38,76])
def test_fitting_equals_exhaustive_filter(counter,limit):
    import random,e2
    rng=random.Random(limit)
    for _ in range(80):
        text=''.join(rng.choice(TRICKY) for _ in range(rng.randint(1,40)))
        starts=sorted(rng.sample(range(len(text)+1),min(len(text)+1,15)))
        expected=[a for a in starts if counter.count(text[a:])<=limit]
        assert sorted(e2._fitting(counter,text,starts,limit))==expected,(text,limit)

@pytest.mark.parametrize('C',['C2','C3'])
@pytest.mark.parametrize('r',[0.1,0.2])
def test_pruned_batched_equals_original_on_long_runs(counter,C,r):
    import e2
    v=doc(['Long sentence without stop but many words '*40+'. Short. '*3,'Ünïcode — dash! '*30+'​end.','A. B. C. '*20],[['A'],['A'],['A']])
    for c in chunkers.chunk(v,C,64,counter):
        assert e2.attach_overlap_batched(c,r,64,v,counter)==chunkers.attach_overlap(c,r,64,v,counter)
