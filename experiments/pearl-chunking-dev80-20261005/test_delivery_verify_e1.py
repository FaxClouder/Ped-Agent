import hashlib
import pytest
from delivery_verify_e1 import (
    check_delivery_fields,
    check_document,
    check_external_envelopes,
    check_manifest,
)


def test_sealed_manifest_rejects_tampering_and_escape(tmp_path):
    path = tmp_path / 'evidence.json'
    path.write_bytes(b'actual evidence')
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = dict(artifact_count=1, artifacts_sha256={'evidence.json': expected})
    assert check_manifest(tmp_path, manifest) == 1
    path.write_bytes(b'replaced evidence')
    with pytest.raises(ValueError, match='hash drift'):
        check_manifest(tmp_path, manifest)
    with pytest.raises(ValueError, match='escaping'):
        check_manifest(tmp_path, dict(artifacts_sha256={'../outside': expected}))


def test_delivery_links_must_reopen(tmp_path):
    path = tmp_path / 'handoff.md'
    path.write_text('# E1\n\n*status: current*\n\n[table](missing.csv)\n', encoding='utf8')
    with pytest.raises(ValueError, match='broken'):
        check_document(path)
    (tmp_path / 'missing.csv').write_text('actual table', encoding='utf8')
    assert check_document(path) == 1

    outside = tmp_path.parent / 'outside.csv'
    outside.write_text('outside', encoding='utf8')
    path.write_text('# E1\n\n*status: current*\n\n[outside](../outside.csv)\n', encoding='utf8')
    with pytest.raises(ValueError, match='escaping'):
        check_document(path)


def test_repo_relative_retained_attempt_manifest_format_is_supported(tmp_path):
    artifact = tmp_path / 'outputs' / 'attempt' / 'rankings.jsonl'
    artifact.parent.mkdir(parents=True)
    artifact.write_text('retained bytes', encoding='utf8')
    manifest = {
        'status': 'aborted_performance_restart',
        'accepted_run': 'outputs/accepted',
        'artifact_count': 1,
        'artifacts_sha256': {
            'outputs/attempt/rankings.jsonl': hashlib.sha256(artifact.read_bytes()).hexdigest(),
        },
    }
    assert check_manifest(tmp_path, manifest) == 1


def test_receipt_must_be_declared_excluded_external_envelope(tmp_path):
    output = tmp_path / 'outputs' / 'run'
    output.mkdir(parents=True)
    manifest = {
        'artifacts_sha256': {'outputs/run/handoff.md': 'hash'},
        'external_post_freeze_envelopes': [
            'command-package-r02.json',
            'command-package-r02.stdout.log',
            'command-package-r02.stderr.log',
            'delivery-verification-e1-r01.json',
        ],
    }
    receipt = output / 'delivery-verification-e1-r01.json'
    assert check_external_envelopes(tmp_path, output, receipt, manifest)

    manifest['artifacts_sha256']['outputs/run/delivery-verification-e1-r01.json'] = 'hash'
    with pytest.raises(ValueError, match='excluded'):
        check_external_envelopes(tmp_path, output, receipt, manifest)


def test_delivery_fields_cover_counts_candidate_and_generation_scope():
    manifest = {
        'status': 'E1_matrix_complete_selection_pending',
        'counts': {
            'configurations': 13,
            'retrieved': 1040,
            'method_cells': 4160,
            'contexts': 2080,
            'score_details': 22880,
            'summary_cells': 286,
            'independent_intents': 80,
            'failed': 0,
        },
        'decisions': {
            'status': 'pending_unknown',
            'selected': [],
            'baseline_retained': 'B0-regex320-overlap48-M0',
            'generation_calls': 0,
        },
        'budget': {
            'generation_calls': 0,
            'external_model_api_calls': 0,
            'external_judge_api_calls': 0,
        },
    }
    assert check_delivery_fields(manifest)

    manifest['budget']['external_model_api_calls'] = 1
    with pytest.raises(ValueError, match='generation/API'):
        check_delivery_fields(manifest)


def test_frozen_candidate_count_uses_nonduplicate_representatives():
    manifest = {
        'status': 'E1_complete_candidates_frozen',
        'counts': {
            'configurations': 13,
            'retrieved': 1040,
            'method_cells': 4160,
            'contexts': 2080,
            'score_details': 22880,
            'summary_cells': 286,
            'independent_intents': 80,
            'failed': 0,
        },
        'decisions': {
            'status': 'frozen',
            'selected': ['C1-L256-O0-M0'],
            'nonduplicate_metrics': [{'configuration_id': 'C1-L256-O0-M0'}],
            'baseline_retained': 'B0-regex320-overlap48-M0',
            'generation_calls': 0,
        },
        'budget': {
            'generation_calls': 0,
            'external_model_api_calls': 0,
            'external_judge_api_calls': 0,
        },
    }

    assert check_delivery_fields(manifest)

    manifest['decisions']['selected'] = []
    with pytest.raises(ValueError, match='frozen candidate count'):
        check_delivery_fields(manifest)
