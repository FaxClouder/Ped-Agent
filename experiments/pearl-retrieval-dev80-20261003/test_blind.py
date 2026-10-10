import importlib.util
from pathlib import Path
import pytest

def module():
    spec=importlib.util.spec_from_file_location('blind',Path(__file__).with_name('blind.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_blind_fields_and_semantic_gold_only():
    m=module()
    c={'chunk_id':'c','text':'raw child','text_sha256':'h','source_id':'s','rank':1,'score':2,
       'r3_rank':9,'parent_chunk_id':'p','source_sha256':'sh','title':'t','page_start':1,'page_end':1}
    q={'intent_id':'q','query':'why','atoms':[],'requirements':[],'evidence_groups':[],
       'reference_answer':'answer','annotation_provenance':{'rank':1},'authoring_note':'private'}
    p=m.packet(q,[c],[c])
    m.assert_blind(p)
    assert 'rank' not in str(p) and 'parent_chunk_id' not in str(p)
    assert 'annotation_provenance' not in p['intent']
    assert p['candidates'][0]['text']=='raw child'

def test_rank_context_rejected_recursively():
    m=module()
    with pytest.raises(ValueError):m.assert_blind({'a':[{'method':'R1'}]})
