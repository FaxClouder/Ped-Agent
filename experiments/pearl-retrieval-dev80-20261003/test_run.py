import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


def runner():
    path = Path(__file__).with_name('run.py')
    assert path.exists(), 'query-only dev80 runner must exist'
    spec = importlib.util.spec_from_file_location('dev80_runner', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_query_only_rejects_gold_fields(tmp_path):
    module = runner()
    path = tmp_path / 'queries.jsonl'
    path.write_text(json.dumps({'intent_id': 'dev001', 'query': 'flow?', 'answer': 'secret'}))
    with pytest.raises(ValueError, match='query-only'):
        module.load_queries(path, expected_count=1)
    path.write_text(json.dumps({'intent_id': 'dev001', 'query': 'flow?'}))
    assert module.load_queries(path, expected_count=1)[0]['query'] == 'flow?'


def test_fixed_numerical_ties_and_rrf():
    module = runner()
    vectors = np.array([[1., 0.], [1., 0.], [0., 1.]], dtype=np.float32)
    dense = module.build.exact_dense(vectors, np.array([1., 0.]), ['b', 'a', 'c'], 3)
    assert [row['chunk_id'] for row in dense] == ['a', 'b', 'c']
    union = module.compare.rrf_union([{'chunk_id': 'b'}], [{'chunk_id': 'a'}])
    assert [row['chunk_id'] for row in union] == ['a', 'b']
    assert union[0]['score'] == pytest.approx(1 / 61)


def test_r4_preserves_candidate_identity_and_ties():
    module = runner()
    original = [dict(rank=1, chunk_id='b', text='B', text_sha256=module.text_sha('B')),
                dict(rank=2, chunk_id='a', text='A', text_sha256=module.text_sha('A'))]
    ranked = module.rerank.rerank_results(original, [2., 2.])
    assert [row['chunk_id'] for row in ranked] == ['a', 'b']
    module.assert_candidate_identity(original, ranked)
    ranked[0]['text'] = 'changed'
    with pytest.raises(ValueError, match='identity'):
        module.assert_candidate_identity(original, ranked)


def test_determinism_checks_scores_not_only_ids():
    module = runner()
    first = [dict(chunk_id='a', score=1.)]
    assert module.ranking_determinism(first, first)['scores_exact']
    result = module.ranking_determinism(first, [dict(chunk_id='a', score=1.0001)])
    assert result['ids_equal'] and not result['scores_exact']
    assert result['max_score_abs_delta'] == pytest.approx(.0001)


def test_actual_input_audit_rejects_truncation():
    module = runner()
    module.assert_actual_inputs([[1, 2], [3, 4]], [[3, 4], [1, 2], [1, 2]])
    with pytest.raises(ValueError, match='actual model input'):
        module.assert_actual_inputs([[1, 2]], [[1]])
    with pytest.raises(ValueError, match='actual model input'):
        module.assert_actual_inputs([[1, 2], [3, 4]], [[1, 2]])


def test_output_overwrite_rejected(tmp_path):
    module = runner()
    (tmp_path / 'rankings.jsonl').write_text('frozen')
    with pytest.raises(FileExistsError):
        module.check_output(tmp_path, {'preflight.json', 'queries.jsonl'})


def test_result_row_distinguishes_legal_short_return():
    module = runner()
    empty = module.result_row({'intent_id': 'dev001', 'query': '!'}, 'R1', 1, [])
    assert empty['status'] == 'success'
    assert empty['empty_result_reason'] == 'no_matching_sparse_body_terms'
    short = module.result_row({'intent_id': 'dev001', 'query': 'flow'}, 'R1', 1, [{'rank': 1}])
    assert short['returned'] == 1
    assert short['short_result_reason'] == 'fewer_than_100_matching_sparse_children'


def test_retriever_never_invokes_pilot_gold_loaders():
    import ast
    module = runner()
    tree = ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
    calls = [node.func for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert not any(isinstance(call, ast.Attribute) and isinstance(call.value, ast.Name)
                   and call.value.id in ('compare', 'rerank') and call.attr in ('preflight', 'main', 'run')
                   for call in calls)
    assert '--gold' not in Path(module.__file__).read_text(encoding='utf-8')


def test_actual_forward_hook_captures_positional_and_keyword_inputs():
    import torch
    module = runner()
    class Dummy(torch.nn.Module):
        def forward(self, inputs=None, **kwargs):
            return 1
    model = Dummy()
    batch = dict(input_ids=torch.tensor([[1, 2, 0], [3, 0, 0]]),
                 attention_mask=torch.tensor([[1, 1, 0], [1, 0, 0]]))
    with module.capture_forward_inputs(model) as captured:
        model(batch)
        model(**batch)
    assert captured == [[1, 2], [3], [1, 2], [3]]
    assert len(model._forward_pre_hooks) == 0


def test_preflight_failure_persisted_without_quality_zero(tmp_path, monkeypatch):
    module = runner()
    def broken(*args):
        raise ValueError('frozen input mismatch')
    monkeypatch.setattr(module, 'preflight_inputs', broken)
    with pytest.raises(ValueError, match='frozen input mismatch'):
        module.run(tmp_path, tmp_path / 'preflight.json', tmp_path / 'queries.jsonl')
    manifest = json.loads((tmp_path / 'run_manifest.json').read_text())
    assert manifest['status'] == 'partial_execution_failure'
    assert manifest['execution_failures'][0]['quality_score'] is None
    assert not (tmp_path / 'rankings.jsonl').exists()


def test_journal_close_is_idempotent_after_late_failure(tmp_path):
    module = runner()
    journal = module.Journal(tmp_path)
    journal.append('a.jsonl', {'status': 'success'})
    journal.close()
    journal.close()
    assert len((tmp_path / 'a.jsonl').read_text().splitlines()) == 1


def test_dense_competing_weights_rejected(tmp_path):
    module = runner()
    (tmp_path / 'pytorch_model.bin').write_bytes(b'allowed')
    module.reject_competing_dense_weights(tmp_path)
    (tmp_path / 'model.safetensors').write_bytes(b'competing')
    with pytest.raises(ValueError, match='unverified safetensors'):
        module.reject_competing_dense_weights(tmp_path)
