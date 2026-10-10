import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pytest
from verify import check_visible_unit, independent_truth

def test_saved_visible_text_must_match_offset():
    views=[{'doc_id':'d','source_version':'v','elements':[{'doc_id':'d','source_version':'v','element_id':'e','text':'条件😀 conclusion'}]}]
    u={'spans':[{'doc_id':'d','source_version':'v','element_id':'e','start':0,'end':3}],'text':'条件😀'}
    assert check_visible_unit(views,u)
    u['spans'][0]['end']=2
    with pytest.raises(ValueError):check_visible_unit(views,u)

def test_independent_unknown_and_or():
    assert independent_truth([['a','b'],['c']],{'a':'yes','b':'unknown','c':'no'})=='unknown'
    assert independent_truth([['a','b'],['c']],{'a':'yes','b':'no','c':'yes'})=='yes'
    assert independent_truth([['a','b']],{'a':'yes','b':'no'})=='no'
