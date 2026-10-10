from cross_layer import diagnostics

def test_strict_failure_is_not_false_claim_and_na_reference_is_excluded():
    rows=[{'cell_id':'x::a','intent_id':'x','arm':'a','answerability':'complete','behavior':'full_answer','abstain':False,'unsupported_completion':False,'extraction_unknown':False,'claims':[{'grounding':{'label':'supported'},'factuality':{'label':'unknown'}}]}, {'cell_id':'y::ref','intent_id':'y','arm':'ref','answerability':'complete','behavior':'full_answer','abstain':False,'unsupported_completion':False,'extraction_unknown':False,'claims':[{'grounding':{'label':'unsupported'},'factuality':{'label':'true'}}]}]
    old={'rows':[{'intent_id':'x','arm':'a','strict':'no'},{'intent_id':'y','arm':'ref','strict':'yes'}]}
    l2={'cells':[{'intent_id':'x','arm':'a','l2_sufficient':'no'},{'intent_id':'y','arm':'ref','l2_sufficient':'na'}]}
    d=diagnostics(rows,old,l2)
    assert d['arms']['a']['claim_truth_grounding']['unknown|supported']==1
    assert d['arms']['ref']['claim_truth_grounding']['true|unsupported']==1
    assert d['l2_actual_cell_N']==1
    assert d['arms']['a']['l2_answerability']['no|complete']==1
