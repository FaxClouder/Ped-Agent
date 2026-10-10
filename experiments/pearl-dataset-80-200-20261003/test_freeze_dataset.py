import importlib.util
from pathlib import Path

import pytest


def module():
    spec = importlib.util.spec_from_file_location('freeze_dataset', Path(__file__).with_name('freeze_dataset.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_sealing_requires_independent_complete_review_of_exact_candidate_bytes():
    m = module()
    rows = [{'intent_id': 'q1', 'atoms': [{'atom_id': 'a1'}]}]
    review = {'candidate_sha256': 'abc', 'reviewer_id': 'other-agent', 'unresolved': [], 'intents': [
        {'intent_id': 'q1', 'decision': 'accept', 'checked_atom_ids': ['a1'], 'stratum_confirmed': True,
         'all_complete_paths_sufficient': True, 'family_distinct_within_batch': True, 'findings': [], 'reason': 'Original source establishes fact and condition.'}]}
    m.require_review(rows, review, 'abc', 'author-agent')
    with pytest.raises(ValueError, match='hash'):
        m.require_review(rows, review, 'changed', 'author-agent')
    with pytest.raises(ValueError, match='independent'):
        m.require_review(rows, review, 'abc', 'other-agent')
    with pytest.raises(ValueError, match='atom'):
        m.require_review(rows, {**review, 'intents': [{**review['intents'][0], 'checked_atom_ids': []}]}, 'abc', 'author-agent')


def test_family_overlap_cannot_be_waived_by_a_leakage_review():
    m = module()
    flags = [{'type': 'shared_family_id', 'left': 'd1', 'right': 'e1'}]
    review = {'all_intents_semantically_scanned': True, 'unresolved': [], 'adjudications': [
        {'type': 'shared_family_id', 'left': 'd1', 'right': 'e1', 'decision': 'distinct', 'reason': 'Different papers.'}]}
    with pytest.raises(ValueError, match='family'):
        m.require_leakage_review(flags, review)


def test_global_semantic_scan_must_cover_exact_question_ids():
    m = module()
    review = {'all_intents_semantically_scanned': True, 'unresolved': [],
              'adjudications': [], 'reviewed_intent_ids': ['d1', 'e1']}
    m.require_leakage_review([], review, {'d1', 'e1'})
    with pytest.raises(ValueError, match='coverage'):
        m.require_leakage_review([], review, {'d1', 'e1', 'e2'})


def test_source_partition_is_checked_instead_of_assumed():
    m = module()
    ids = [f's{i}' for i in range(106)]
    groups = {'dev': ids[:32], 'eval_a': ids[32:69], 'eval_b': ids[69:]}
    actual = m.validate_source_partition(groups, set(ids), {'s0'})
    assert actual['intersection'] == [] and actual['evaluation_authoring_sources'] == 74
    bad = {**groups, 'eval_b': [*ids[70:], 's33']}
    with pytest.raises(ValueError, match='disjoint'):
        m.validate_source_partition(bad, set(ids), {'s0'})
    with pytest.raises(ValueError, match='pilot'):
        m.validate_source_partition(groups, set(ids), {'s99'})


def test_seal_provenance_paths_are_preflighted(tmp_path):
    m = module()
    directory = tmp_path / 'authoring'
    directory.mkdir()
    outside = tmp_path / 'outside.json'
    outside.write_text('{}')
    with pytest.raises(ValueError, match='outside'):
        m.validate_eval_provenance({outside}, directory)
    with pytest.raises(ValueError, match='missing'):
        m.validate_eval_provenance({directory / 'missing.json'}, directory)
