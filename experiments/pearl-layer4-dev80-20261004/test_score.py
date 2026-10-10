import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('l4score', Path(__file__).with_name('score.py'))
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

def test_grounding_bounds_and_refusal_na():
    result = score.claim_metrics(['supported','supported','partial','unsupported','unknown'], ['true']*5)
    assert result['faithfulness'] == [0.4, 0.6]
    assert result['unsupported_rate'] == [0.4, 0.6]
    assert score.claim_metrics([], [])['faithfulness'] == [None,None]
    assert score.claim_metrics(['supported'], ['true'], extraction_unknown=True)['faithfulness'] == [None,None]
    assert score.claim_metrics(['supported'], ['true'], extraction_unknown=True)['factuality_coverage'] is None

def test_actual_citation_pairs_include_invalid():
    pairs = [{'claim_id':'c1','label':'supported'}, {'claim_id':'c2','label':'supported'}, {'claim_id':'c3','label':'invalid'}]
    result = score.citation_metrics(['c1','c2','c3'], pairs)
    assert result['precision'] == [2/3,2/3]
    assert result['recall'] == [2/3,2/3]
    assert score.citation_metrics(['c1'],[])['recall'] == [0,0]
    assert score.citation_metrics([],[])['precision'] == [None,None]

def test_confusion_and_unknown_not_tn():
    rows = [{'answerability':a, 'abstain':b} for a,b in [('partial',True),('none',True),('complete',True),('partial',False),('complete',False),('complete',False),('unknown',False)]]
    result=score.reliability_metrics(rows)
    assert [result[k] for k in ('TP','FP','FN','TN')] == [2,1,1,2]
    assert result['precision'] == result['recall'] == result['f1'] == 2/3
    assert result['false_answer_rate'] == result['false_refusal_rate'] == 1/3
    assert result['resolved_cells'] == 6 and result['unknown_cells'] == 1
    assert score.reliability_metrics([{'answerability':'complete','abstain':False}])['recall'] is None

def test_invalid_claim_label_fails():
    with pytest.raises(ValueError): score.claim_metrics(['wrong'],['true'])
    with pytest.raises(ValueError): score.reliability_metrics([{'answerability':'unknown','abstain':'yes'}])

def test_unknown_bounds_respect_known_answerability():
    result=score.reliability_metrics([{'answerability':'partial','abstain':None},{'answerability':'complete','abstain':False}])
    assert result['TN']==1 and result['unknown_cells']==1
    assert result['recall_bounds']==[0,1]
    assert result['false_refusal_rate_bounds']==[0,0]
