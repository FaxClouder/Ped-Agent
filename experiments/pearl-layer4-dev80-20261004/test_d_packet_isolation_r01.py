import json
import pytest
import export_d_source_packets_r01 as source
import export_d_context_adjudication_r01 as third


def test_third_rejects_review_from_another_response():
    packet = {'response_sha256': 'actual', 'context_sha256': 'actual_context'}
    with pytest.raises(ValueError, match='review input mismatch'):
        third.validate_review_input({'response_sha256': 'other', 'context_sha256': 'actual_context'}, packet)
    third.validate_review_input({'response_sha256': 'actual', 'context_sha256': 'actual_context'}, packet)


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def test_source_packet_isolates_context_labels_and_identity(tmp_path, monkeypatch):
    root = tmp_path / 'root'
    monkeypatch.setattr(source, 'ROOT', root)
    put(root / 'facts/facts-r03.json', {'items': [{'intent_id': 'i', 'evidence': []}]})
    put(root / 'inputs-r01.json', {'cells': [{'cell_id': 'i::arm', 'intent_id': 'i', 'response_sha256': 'r', 'context_sha256': 'c'}]})
    g = root / 'ground.json'
    put(g, {'claims': [{'claim_id': 'a', 'start': 0, 'end': 1, 'quote': 'A',
                        'normalized_claim': 'A', 'conditions': [], 'occurrences': [],
                        'grounding': {'label': 'unsupported'}}],
            'provenance': {'response_sha256': 'r', 'context_sha256': 'c'},
            'arm': 'secret_arm', 'context': 'secret_context'})
    selection = {'rows': [{'cell_id': 'i::arm', 'blind_id': 'factuality-0001', 'grounding_path': str(g)}]}
    out, manifest = tmp_path / 'packets', tmp_path / 'manifest.json'
    assert source.export(selection, out, manifest)['labels_generated'] is False
    packet = json.loads((out / 'factuality-0001.json').read_text())
    assert set(packet) == {'blind_id', 'claims', 'response_sha256', 'facts', 'rubric'}
    assert 'grounding' not in packet['claims'][0]
    assert 'secret_context' not in json.dumps(packet) and 'secret_arm' not in json.dumps(packet)
    with pytest.raises(FileExistsError):
        source.export(selection, out, tmp_path / 'manifest2.json')
    assert not (tmp_path / 'manifest2.json').exists()


def test_source_rejects_wrong_original_context_sha(tmp_path, monkeypatch):
    root = tmp_path / 'root'
    monkeypatch.setattr(source, 'ROOT', root)
    put(root / 'facts/facts-r03.json', {'items': [{'intent_id': 'i', 'evidence': []}]})
    put(root / 'inputs-r01.json', {'cells': [{'cell_id': 'i::arm', 'intent_id': 'i', 'response_sha256': 'r', 'context_sha256': 'c'}]})
    g = root / 'ground.json'
    put(g, {'claims': [], 'response_sha256': 'r', 'context_sha256': 'tampered'})
    selection = {'rows': [{'cell_id': 'i::arm', 'blind_id': 'factuality-0001', 'grounding_path': str(g)}]}
    with pytest.raises(ValueError, match='input mismatch'):
        source.export(selection, tmp_path / 'out', tmp_path / 'manifest')
    assert not (tmp_path / 'out').exists()


def test_behavior_third_packet_cannot_import_frozen_answerability_or_facts(tmp_path, monkeypatch):
    root = tmp_path / 'root'
    monkeypatch.setattr(third, 'ROOT', root)
    put(root / 'packets/behavior-D60-r02-identity-map.json', [{'cell_id': 'i::arm', 'blind_id': 'behavior-0001'}])
    put(root / 'packets/behavior-D60-r02/behavior-0001.json', {'blind_id': 'behavior-0001', 'query': 'q', 'raw_answer': 'a', 'context': 'c', 'requirements': []})
    decision = {'behavior': 'full_answer', 'abstain': False, 'reason': {'label': 'na'},
                'answerability': 'complete', 'facts': 'secret_gold', 'provenance': {'arm': 'secret_arm'}}
    p, s = root / 'p.json', root / 's.json'
    put(p, decision); put(s, decision)
    selection = {'rows': [{'cell_id': 'i::arm', 'primary_path': str(p), 'secondary_path': str(s)}]}
    out = tmp_path / 'packets'
    third.export(selection, 'behavior', out, tmp_path / 'manifest.json')
    packet = json.loads((out / 'behavior-0001.json').read_text())
    assert set(packet['review_A']) == {'behavior', 'abstain', 'reason'}
    assert 'secret_gold' not in json.dumps(packet) and 'secret_arm' not in json.dumps(packet)
