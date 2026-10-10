import importlib.util
from pathlib import Path

import pytest


def load():
    spec = importlib.util.spec_from_file_location('dataset_audit', Path(__file__).with_name('dataset_audit.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def question():
    return {'intent_id': 'q1', 'family_id': 'family1', 'main_stratum': 'cross_paper', 'query': 'What differs between these two studies?',
            'reference_answer': 'A differs from B.', 'atoms': [
                {'atom_id': 'a1', 'source_id': 's1', 'page': 1, 'locator_type': 'text_anchor', 'anchor_text': 'one source anchor', 'supports': 'First fact.'},
                {'atom_id': 'a2', 'source_id': 's2', 'page': 2, 'locator_type': 'text_anchor', 'anchor_text': 'second source anchor', 'supports': 'Second fact.'}],
            'requirements': [
                {'requirement_id': 'r1', 'claim': 'First fact.', 'scope': 'A', 'support_bundles': [['a1']]},
                {'requirement_id': 'r2', 'claim': 'Second fact.', 'scope': 'B', 'support_bundles': [['a2']]}],
            'evidence_groups': [{'group_id': 'g1', 'requirements': ['r1', 'r2']}]}


def test_each_cross_paper_complete_path_requires_two_sources():
    module = load()
    q = question()
    module.validate_structure(q, {'s1', 's2'})
    q['requirements'][1]['support_bundles'].append(['a1'])
    with pytest.raises(ValueError, match='cross-paper'):
        module.validate_structure(q, {'s1', 's2'})


def test_redundant_groups_and_unknown_sources_are_rejected():
    module = load()
    q = question()
    with pytest.raises(ValueError, match='source'):
        module.validate_structure(q, {'s1'})
    q['evidence_groups'].append({'group_id': 'g2', 'requirements': ['r1']})
    with pytest.raises(ValueError, match='redundant'):
        module.validate_structure(q, {'s1', 's2'})


def test_numeric_template_variants_are_flagged_before_sealing():
    module = load()
    a = dict(question(), query='How does 1.5 m width affect flow?', family_id='f-a')
    b = dict(question(), query='How does 2.0 m width affect flow?', family_id='f-b', intent_id='q2')
    flags = module.leakage_candidates([a], [b])
    assert any(flag['type'] == 'numeric_template' for flag in flags)


def test_only_replacing_cited_study_names_is_flagged_for_semantic_review():
    m = load()
    a = dict(question(), query='How did Li et al. obtain the participant trajectories in the evacuation experiment?', family_id='f-a')
    b = dict(question(), query='How did Wang et al. obtain the participant trajectories in the evacuation experiment?', family_id='f-b', intent_id='q2')
    assert any(flag['type'] == 'study_masked_template' for flag in m.leakage_candidates([a], [b]))


def test_table_spacing_normalization_preserves_decimal_punctuation():
    m = load()
    assert m.table_field_present('2.41', 'Flow rate J 2 .41 s −1')
    assert m.table_field_present('Flow rate J (s−1)', 'Flow rate J ( s −1 )')
    assert not m.table_field_present('2.41', 'Flow rate J 241 s −1')
