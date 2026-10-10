import pytest
from assemble_d400_r01 import validate_behavior_decision
from verify_d400_r01 import validate_decision_vocabulary


def test_reject_unreviewed_behavior_and_reason_vocabulary():
    with pytest.raises(ValueError, match='behavior vocabulary'):
        validate_behavior_decision({'behavior': 'bounded_answer', 'abstain': True,
                                    'unsupported_completion': False,
                                    'reason': {'label': 'context_insufficiency'}})
    with pytest.raises(ValueError, match='reason vocabulary'):
        validate_behavior_decision({'behavior': 'bounded_partial', 'abstain': True,
                                    'unsupported_completion': False,
                                    'reason': {'label': 'context_insufficiency'}})


def test_reject_inconsistent_refusal_without_assigning_semantic_labels():
    with pytest.raises(ValueError, match='behavior action'):
        validate_behavior_decision({'behavior': 'full_answer', 'abstain': True,
                                    'unsupported_completion': False,
                                    'reason': {'label': 'na'}})
    validate_behavior_decision({'behavior': 'bounded_partial', 'abstain': True,
                               'unsupported_completion': False,
                               'reason': {'label': 'unknown'}})


def test_independent_verifier_rejects_saved_unscored_reason_category():
    with pytest.raises(ValueError, match='saved decision vocabulary'):
        validate_decision_vocabulary([{'behavior': 'bounded_partial', 'abstain': True,
                                       'unsupported_completion': False,
                                       'reason': 'context_insufficiency'}])
    validate_behavior_decision({'behavior': 'ambiguous', 'abstain': None,
                               'unsupported_completion': None,
                               'reason': {'label': 'unknown'}})
