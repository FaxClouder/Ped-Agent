"""Protect historical outputs and reproduce the fixed v3 numerical reference."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = ROOT / 'memPed/knowledge/pearl-retrieval-pilot-r1-2026-09-29-01'


def test_explicit_rescore_preserves_original_and_matches_reference(tmp_path):
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in RUN.iterdir() if p.is_file()}
    output = tmp_path / 'scores.json'
    command = [sys.executable, str(HERE / 'score_bm25_pilot.py'), str(RUN),
               '--gold', str(HERE / 'pilot-intents-agent-reviewed-v3.json'),
               '--mapping', str(RUN / 'support-mapping-agent-reviewed.json'),
               '--output', str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    actual = json.loads(output.read_text(encoding='utf-8'))
    reference = json.loads((RUN / 'preliminary-scores.json').read_text(encoding='utf-8'))
    assert actual['details'] == reference['details']
    assert actual['by_k'] == reference['by_k']
    assert actual['by_k']['10']['CEGR'] == 3 / 8
    assert actual['by_k']['20']['CEGR'] == 5 / 8
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in RUN.iterdir() if p.is_file()}
    output.write_text('{"existing": true}', encoding='utf-8')
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert json.loads(output.read_text()) == {'existing': True}


def test_revision_requires_identical_queries_and_records_provenance(tmp_path):
    gold = json.loads((HERE / 'pilot-intents-agent-reviewed-v3.json').read_text(encoding='utf-8'))
    gold['dataset_id'] = 'test-revision'
    path = tmp_path / 'gold.json'
    path.write_text(json.dumps(gold), encoding='utf-8')
    mapping = json.loads((RUN / 'support-mapping-agent-reviewed.json').read_text(encoding='utf-8'))
    mapping['gold_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    mapping_path = tmp_path / 'mapping.json'
    mapping_path.write_text(json.dumps(mapping), encoding='utf-8')
    output = tmp_path / 'scores.json'
    command = [sys.executable, str(HERE / 'score_bm25_pilot.py'), str(RUN),
               '--gold', str(path), '--mapping', str(mapping_path), '--output', str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    scores = json.loads(output.read_text())
    assert scores['gold_dataset_id'] == 'test-revision'
    assert scores['original_gold_sha256'] != scores['gold_sha256']
    assert scores['children_sha256'] == json.loads((RUN / 'run-manifest.json').read_text())['children_sha256']
    gold['intents'][0]['query'] += ' changed'
    path.write_text(json.dumps(gold), encoding='utf-8')
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'cannot change query' in result.stderr


def test_v4_fixed_reference_requires_li_running_condition(tmp_path):
    output = tmp_path / 'v4.json'
    revised = ROOT / 'memPed/knowledge/pearl-retrieval-pilot-r1-v4-2026-09-29-01'
    result = subprocess.run([
        sys.executable, str(HERE / 'score_bm25_pilot.py'), str(RUN),
        '--gold', str(HERE / 'pilot-intents-agent-reviewed-v4.json'),
        '--mapping', str(revised / 'support-mapping-agent-reviewed-v4.json'),
        '--output', str(output)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    scores = json.loads(output.read_text())
    rows = {r['intent_id']: r for r in scores['details']}
    assert scores['by_k']['1']['CEGR'] == 1 / 8
    assert scores['by_k']['10']['CEGR'] == 3 / 8
    assert scores['by_k']['20']['CEGR'] == 5 / 8
    assert rows['pearl-dev-pilot-004']['scores']['1']['first_complete_rank'] == 1
    li = rows['pearl-dev-pilot-005']['scores']
    assert li['10']['requirements_hit']['r2'] is False
    assert li['20']['first_complete_rank'] == 18
