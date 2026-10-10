"""Query-only PEARL dev80 runner; first of three passes is the scoring input."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import sqlite3
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / 'experiments/pearl-index-106-adobe-20260929'
sys.path.insert(0, str(PILOT))
import build


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compare = load_module('pearl_compare_algorithm', PILOT / 'compare_pilot.py')
rerank = load_module('pearl_rerank_algorithm', PILOT / 'rerank_pilot.py')
sha = build.sha
text_sha = build.text_sha
DEPTH = 100
METHODS = ('R1', 'R2', 'R3', 'R4')


def json_hash(value):
    return text_sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


def load_queries(path, expected_count=80):
    rows = compare.read_jsonl(path)
    if len(rows) != expected_count or len({r.get('intent_id') for r in rows}) != expected_count:
        raise ValueError('query-only input count or intent uniqueness mismatch')
    for row in rows:
        if set(row) != {'intent_id', 'query'}:
            raise ValueError('query-only input must contain exactly intent_id and query')
        if not all(isinstance(row[k], str) and row[k].strip() for k in row):
            raise ValueError('query-only input has blank/nonstring values')
    return rows


def assert_candidate_identity(original, ranked):
    def identities(rows):
        result = {}
        for row in rows:
            if row['chunk_id'] in result or text_sha(row['text']) != row['text_sha256']:
                raise ValueError('candidate identity or text hash mismatch')
            result[row['chunk_id']] = (row['text'], row['text_sha256'])
        return result
    if identities(original) != identities(ranked):
        raise ValueError('R3/R4 candidate identity mismatch')


def ranking_determinism(first, later):
    ids_equal = [r['chunk_id'] for r in first] == [r['chunk_id'] for r in later]
    scores_exact = ids_equal and [r['score'] for r in first] == [r['score'] for r in later]
    a, b = {r['chunk_id']:r['score'] for r in first}, {r['chunk_id']:r['score'] for r in later}
    delta = max((abs(a[c] - b[c]) for c in a.keys() & b.keys()), default=0.)
    return dict(ids_equal=ids_equal, scores_exact=scores_exact, max_score_abs_delta=delta)


def result_row(query, method, pass_number, results):
    row = dict(**query, method=method, pass_number=pass_number, status='success',
               returned=len(results), results=results)
    if not results:
        row['empty_result_reason'] = ('no_matching_sparse_body_terms' if method == 'R1'
                                     else 'legal_empty_candidate_set')
    elif len(results) < DEPTH:
        row['short_result_reason'] = ('fewer_than_100_matching_sparse_children' if method == 'R1'
                                     else 'fewer_than_100_fused_candidate_children')
    return row


def assert_actual_inputs(expected, actual):
    # FlagEmbedding first performs a batch-size probe, then the scoring pass.
    need, seen = Counter(map(tuple, expected)), Counter(map(tuple, actual))
    if set(need) != set(seen) or any(seen[key] < value for key, value in need.items()):
        raise ValueError('actual model input differs from complete untruncated audited tokens')


def check_output(output, allowed):
    if output.exists():
        unexpected = {p.name for p in output.iterdir()} - set(allowed)
        if unexpected:
            raise FileExistsError(f'refusing to overwrite research output: {sorted(unexpected)}')
    else:
        output.mkdir(parents=True, exist_ok=False)


class Journal:
    """Exclusive creation, query-level flush and fsync; no resume/overwrite semantics."""
    def __init__(self, output):
        self.output, self.streams = output, {}

    def append(self, name, row):
        if name not in self.streams:
            self.streams[name] = (self.output / name).open('x', encoding='utf-8', newline='\n')
        self.streams[name].write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')

    def flush(self):
        for stream in self.streams.values():
            if not stream.closed:
                stream.flush()
                os.fsync(stream.fileno())

    def close(self):
        self.flush()
        for stream in self.streams.values():
            if not stream.closed:
                stream.close()


def save_json(path, value):
    # Manifest/checkpoint belongs to this run; replace only our own live state.
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def reject_competing_dense_weights(model_dir):
    if list(model_dir.glob('*.safetensors')):
        raise ValueError('unverified safetensors weights present; HF weight selection would change')


def preflight_inputs(preflight_path, queries_path):
    import numpy as np
    frozen = json.loads(preflight_path.read_text(encoding='utf-8'))
    if frozen['status'] != 'passed' or frozen['queries_sha256'] != sha(queries_path):
        raise ValueError('preflight/query-only hash mismatch')
    queries = load_queries(queries_path)
    index = Path(frozen['index_dir']).resolve()
    if sha(index / 'build_manifest.json') != frozen['index_build_manifest_sha256']:
        raise ValueError('index manifest differs from preflight')
    manifest = json.loads((index / 'build_manifest.json').read_text(encoding='utf-8'))
    verification = json.loads((index / 'verification.json').read_text(encoding='utf-8'))
    if verification['status'] != 'passed' or verification['build_manifest_sha256'] != sha(index / 'build_manifest.json'):
        raise ValueError('index verification stale')
    for name in ('child_chunks.jsonl', 'dense_ids.json', 'dense_vectors.npy', 'fts.sqlite3'):
        if sha(index / name) != manifest['output_sha256'][name]:
            raise ValueError(f'frozen index changed: {name}')
    if sha(index / 'child_chunks.jsonl') != frozen['frozen_child_sha256']:
        raise ValueError('child library changed')
    corpus = ROOT / 'paper/pearl-framework/datasets/retrieval-corpus/corpus-manifest-v02.jsonl'
    if sha(corpus) != frozen['corpus_manifest_sha256']:
        raise ValueError('corpus manifest changed')
    corpus_expected = manifest['input_sha256']['paper\\pearl-framework\\datasets\\retrieval-corpus\\corpus-manifest-v02.jsonl']
    if sha(corpus) != corpus_expected:
        raise ValueError('corpus/index binding mismatch')
    child_rows = compare.read_jsonl(index / 'child_chunks.jsonl')
    children = {r['chunk_id']: r for r in child_rows}
    ids = json.loads((index / 'dense_ids.json').read_text(encoding='utf-8'))
    if len(children) != 6433 or len(ids) != len(set(ids)) or set(ids) != set(children) or len(child_rows) != len(children):
        raise ValueError('frozen child/dense membership mismatch')
    for child in children.values():
        if text_sha(child['text']) != child['text_sha256']:
            raise ValueError('frozen child text hash mismatch')
    vectors = np.load(index / 'dense_vectors.npy', allow_pickle=False)
    build.validate_vectors(vectors, len(ids))
    config_path = PILOT / 'reranker-config.json'
    if sha(config_path) != frozen['reranker_config_sha256']:
        raise ValueError('reranker config changed')
    config = json.loads(config_path.read_text(encoding='utf-8'))
    dense_dir = ROOT / 'memPed/knowledge/models/bge-m3'
    reject_competing_dense_weights(dense_dir)
    for name, expected in manifest['dense']['actual_asset_sha256'].items():
        if sha(dense_dir / name) != expected:
            raise ValueError(f'dense model file changed: {name}')
    for name, expected in config['verified_files_sha256'].items():
        if sha(ROOT / config['local_model_dir'] / name) != expected:
            raise ValueError(f'reranker model file changed: {name}')
    return frozen, queries, index, manifest, children, ids, vectors, config


@contextmanager
def capture_forward_inputs(model):
    class CapturedInputs(list):
        hook_seconds = 0.
    actual = CapturedInputs()
    def hook(_model, args, kwargs):
        start = time.perf_counter()
        inputs = args[0] if args and hasattr(args[0], 'keys') else kwargs
        tokens = inputs['input_ids'].detach().cpu().tolist()
        masks = inputs['attention_mask'].detach().cpu().tolist()
        actual.extend([token for token, keep in zip(row, mask) if keep] for row, mask in zip(tokens, masks))
        actual.hook_seconds += time.perf_counter() - start
    handle = model.register_forward_pre_hook(hook, with_kwargs=True)
    try:
        yield actual
    finally:
        handle.remove()


class Models:
    def __init__(self, manifest, config):
        import numpy as np
        import torch
        from FlagEmbedding import BGEM3FlagModel, FlagReranker
        self.np, self.torch, self.config = np, torch, config
        self.max_length = manifest['dense']['max_length']
        self.dense = BGEM3FlagModel(str(ROOT / 'memPed/knowledge/models/bge-m3'),
            devices='cuda:0', use_fp16=True, normalize_embeddings=True,
            query_instruction_for_retrieval=None)
        self.reranker = FlagReranker(str(ROOT / config['local_model_dir']),
            devices=config['device'], use_fp16=config['use_fp16'], batch_size=config['batch_size'],
            query_max_length=config['query_max_length'], max_length=config['max_length'], normalize=config['normalize'])

    def sync(self):
        self.torch.cuda.synchronize()

    def encode(self, query):
        raw = self.dense.tokenizer(query, add_special_tokens=True, truncation=False)['input_ids']
        if len(raw) > self.max_length:
            raise ValueError('dense query input would be truncated')
        self.sync()
        start = time.perf_counter()
        with capture_forward_inputs(self.dense.model) as actual:
            value = self.dense.encode([query], batch_size=8, max_length=self.max_length,
                return_dense=True, return_sparse=False, return_colbert_vecs=False)
        self.sync()
        gross_seconds = time.perf_counter() - start
        seconds = max(0., gross_seconds - actual.hook_seconds)
        assert_actual_inputs([raw], actual)
        vector = self.np.asarray(value['dense_vecs'][0], dtype=self.np.float32)
        norm = self.np.linalg.norm(vector)
        if not self.np.isfinite(vector).all() or not math.isfinite(float(norm)) or norm <= 0:
            raise ValueError('nonfinite/zero dense query vector')
        vector /= norm
        audit = dict(query=query, query_sha256=text_sha(query), token_ids=raw,
            token_count=len(raw), truncated=False, actual_forward_calls_tokens_sha256=json_hash(actual),
            actual_forward_inputs_verified=True, encode_seconds=seconds)
        audit.update(encode_gross_seconds=gross_seconds, input_capture_seconds=actual.hook_seconds)
        return vector, audit, seconds

    def rerank(self, query, original):
        start = time.perf_counter()
        audits = rerank.audit_inputs(self.reranker.tokenizer, query, original, self.config)
        if any(a['query_truncated'] or a['child_truncated_initial'] or a['child_truncated_pair'] for a in audits):
            raise ValueError('R4 input would be truncated')
        audit_seconds = time.perf_counter() - start
        self.sync()
        start = time.perf_counter()
        with capture_forward_inputs(self.reranker.model) as actual:
            scores = self.reranker.compute_score([[query, r['text']] for r in original],
                batch_size=self.config['batch_size'], query_max_length=self.config['query_max_length'],
                max_length=self.config['max_length'], normalize=self.config['normalize'])
        self.sync()
        inference_gross_seconds = time.perf_counter() - start
        inference_seconds = max(0., inference_gross_seconds-actual.hook_seconds)
        validation_start = time.perf_counter()
        assert_actual_inputs([a['model_input_ids'] for a in audits], actual)
        validation_seconds = time.perf_counter()-validation_start
        sort_start = time.perf_counter()
        ranked = rerank.rerank_results(original, list(scores))
        sort_seconds = time.perf_counter()-sort_start
        validation_start = time.perf_counter()
        assert_candidate_identity(original, ranked)
        for audit in audits:
            audit['actual_forward_inputs_verified'] = True
            audit['model_input_ids_sha256'] = json_hash(audit['model_input_ids'])
        validation_seconds += time.perf_counter()-validation_start
        return ranked, audits, dict(r4_input_audit_seconds=audit_seconds,
            r4_reranker_seconds=inference_seconds, r4_reranker_gross_seconds=inference_gross_seconds,
            r4_input_capture_seconds=actual.hook_seconds, r4_sort_seconds=sort_seconds,
            r4_validation_seconds=validation_seconds,
            r4_forward_inputs_sha256=json_hash(actual))


def retrieve(models, index, vectors, ids, children, query):
    total_start = time.perf_counter()
    vector, dense_audit, encode_seconds = models.encode(query)
    start = time.perf_counter()
    sparse = build.sparse_query(index / 'fts.sqlite3', query, limit=DEPTH)
    r1_seconds = time.perf_counter() - start
    start = time.perf_counter()
    dense = build.exact_dense(vectors, vector, ids, limit=DEPTH)
    r2_seconds = time.perf_counter() - start
    start = time.perf_counter()
    union = compare.rrf_union(sparse, dense, 60)
    r3_seconds = time.perf_counter() - start
    results = {method: compare.attach_children(ranking, children) for method, ranking in
        (('R1', sparse), ('R2', dense), ('R3', union[:DEPTH]))}
    results['R4'], r4_audits, r4_times = models.rerank(query, results['R3'])
    times = dict(query_encode_seconds=encode_seconds, r1_search_seconds=r1_seconds,
        query_encode_gross_seconds=dense_audit['encode_gross_seconds'],
        dense_input_capture_seconds=dense_audit['input_capture_seconds'],
        r2_exact_search_seconds=r2_seconds, r3_fusion_seconds=r3_seconds,
        r1_total_seconds=r1_seconds, r2_total_seconds=encode_seconds+r2_seconds,
        r3_total_seconds=r1_seconds+encode_seconds+r2_seconds+r3_seconds,
        total_pipeline_seconds=time.perf_counter()-total_start, **r4_times)
    times['r4_total_seconds'] = times['r3_total_seconds'] + r4_times['r4_reranker_seconds'] + r4_times['r4_sort_seconds']
    return results, union, vector, dense_audit, r4_audits, times


def run(output, preflight_path, queries_path):
    import numpy as np
    allowed = {'preflight.json', 'queries.jsonl', 'verification-preflight.json'}
    check_output(output, allowed)
    journal = Journal(output)
    state = dict(status='starting', run_id=output.name, created_at_utc=datetime.now(timezone.utc).isoformat(),
        protocol='retrieval-v0.2', split='development_80', scoring_pass=1,
        support_review='pending; no quality scores computed', execution_failures=[], completed_queries_by_pass={})
    save_json(output / 'run_manifest.json', state)
    current = dict(pass_number=None, intent_id=None)
    try:
        frozen, queries, index, manifest, children, ids, vectors, config = preflight_inputs(preflight_path, queries_path)
        for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_DATASETS_OFFLINE'):
            os.environ[key] = '1'
        os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA unavailable; no CPU/model fallback permitted')
        seed = manifest['seed']
        if config['seed'] != seed:
            raise ValueError('frozen dense/reranker seeds differ')
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        ordered = list(queries)
        random.Random(seed).shuffle(ordered)
        code_paths = [Path(__file__), Path(build.__file__), PILOT / 'compare_pilot.py', PILOT / 'rerank_pilot.py']
        code_paths += list((ROOT / 'Knowledge-Base/src/ped_knowledge').rglob('*.py'))
        code_paths += list((ROOT / 'Contracts/src/ped_contracts').rglob('*.py'))
        state.update(status='loading_models', seed=seed, passes=3, warmup_queries=5, depth=DEPTH, rrf_k=60,
            query_order=[q['intent_id'] for q in ordered], preflight_sha256=sha(preflight_path),
            warmup_protocol='first 5 distinct dev queries in fixed shuffled order, one full pipeline call each',
            latency_protocol='gross synchronized inference/pipeline are real instrumented measurements; method totals are adjusted estimates excluding explicit input audit/validation and measured forward-hook CPU time, not clean uninstrumented latency; one sequential query, cached frozen indexes/models, FlagEmbedding adaptive batch probe retained',
            queries_sha256=sha(queries_path), input_binding=frozen,
            code_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in code_paths},
            dependencies={n:importlib.metadata.version(n) for n in ('numpy','torch','FlagEmbedding','transformers','tokenizers')},
            cuda=dict(torch_cuda=torch.version.cuda, device=torch.cuda.get_device_name(0),
                properties=str(torch.cuda.get_device_properties(0))), deterministic_algorithms=True,
            tf32=False, tie_break='chunk_id ascending', r3_r4_candidate_identity='exact ID/text/hash equality',
            method_config={'R1':dict(manifest['sparse'], sqlite_version=sqlite3.sqlite_version,
                idf='SQLite FTS5 log((N-n+0.5)/(n+0.5)); nonpositive values floor 1e-6; k1=1.2, b=0.75',
                query='sorted unique EnglishLexicalAnalyzer tokens OR; body only; negated SQLite bm25'),
                'R2':manifest['dense'], 'R3':dict(depth=100, rrf_k=60, equal_weights=True), 'R4':config})
        save_json(output / 'run_manifest.json', state)
        start = time.perf_counter()
        models = Models(manifest, config)
        models.sync()
        state['model_load_seconds'] = time.perf_counter() - start
        state['status'] = 'warming_up'
        save_json(output / 'run_manifest.json', state)
        for n, q in enumerate(ordered[:5], 1):
            current = dict(pass_number=0, intent_id=q['intent_id'])
            warm_results, warm_union, _, warm_dense, warm_r4, times = retrieve(models, index, vectors, ids, children, q['query'])
            journal.append('warmup_timings.jsonl', dict(warmup=n, intent_id=q['intent_id'], **times))
            journal.append('warmup_records.jsonl', dict(warmup=n, **q, excluded_from_scoring=True,
                results=warm_results, rrf_union=warm_union, dense_input=warm_dense, r4_inputs=warm_r4))
            journal.flush()
            print(f'warmup {n}/5 {q["intent_id"]}', flush=True)
        state['status'] = 'running'
        save_json(output / 'run_manifest.json', state)
        baseline, first_vector_hashes = {}, {}
        for pass_number in (1, 2, 3):
            pass_dir = output / f'pass-{pass_number}'
            pass_dir.mkdir(exist_ok=False)
            pass_vectors, vector_ids = [], []
            for position, q in enumerate(ordered, 1):
                current = dict(pass_number=pass_number, intent_id=q['intent_id'])
                results, union, vector, dense_audit, audits, times = retrieve(models, index, vectors, ids, children, q['query'])
                vector_sha = hashlib.sha256(np.asarray(vector, dtype='<f4').tobytes()).hexdigest()
                dense_audit.update(intent_id=q['intent_id'], pass_number=pass_number, vector_sha256=vector_sha)
                journal.append(f'pass-{pass_number}/query_inputs.jsonl', dense_audit)
                with (pass_dir / f'query-vector-{q["intent_id"]}.npy').open('xb') as stream:
                    np.save(stream, vector, allow_pickle=False)
                pass_vectors.append(vector)
                vector_ids.append(q['intent_id'])
                if pass_number == 1:
                    first_vector_hashes[q['intent_id']] = vector_sha
                else:
                    journal.append('determinism.jsonl', dict(**current, method='dense_query_vector',
                        bytes_exact=vector_sha==first_vector_hashes[q['intent_id']]))
                for method in METHODS:
                    row = result_row(q, method, pass_number, results[method])
                    journal.append('rankings.jsonl' if pass_number==1 else f'pass-{pass_number}/rankings.jsonl', row)
                    key = (q['intent_id'], method)
                    if pass_number == 1:
                        baseline[key] = results[method]
                    else:
                        journal.append('determinism.jsonl', dict(**current, method=method,
                            **ranking_determinism(baseline[key], results[method])))
                journal.append('rrf_union.jsonl' if pass_number==1 else f'pass-{pass_number}/rrf_union.jsonl',
                    dict(**current, query=q['query'], rrf_k=60,
                        union=[dict(rank=i, in_top100=i<=100, **r) for i,r in enumerate(union,1)]))
                for audit in audits:
                    if pass_number > 1:
                        audit = {k:v for k,v in audit.items() if k not in ('query_text','child_text','model_input_ids')}
                    journal.append('model-inputs-r4.jsonl' if pass_number==1 else f'pass-{pass_number}/model-input-identities-r4.jsonl',
                        dict(**current, **audit))
                journal.append('query_timings.jsonl', dict(**current, order_position=position, **times))
                journal.flush()
                state['completed_queries_by_pass'][str(pass_number)] = position
                save_json(output / 'progress.json', dict(**current, order_position=position, status='running'))
                print(f'pass {pass_number}/3 query {position}/80 {q["intent_id"]} R4={times["r4_reranker_seconds"]:.3f}s', flush=True)
            with (pass_dir / 'query_vectors.npy').open('xb') as stream:
                np.save(stream, np.stack(pass_vectors), allow_pickle=False)
            save_json(pass_dir / 'query_vector_ids.json', vector_ids)
        journal.close()
        checks = compare.read_jsonl(output / 'determinism.jsonl')
        state.update(status='retrieval_complete_support_review_pending', methods_executed=list(METHODS),
            intent_count=80, scoring_rankings_count=320, truncated_input_count=0,
            actual_forward_input_verification='all dense/R4 warmup and timed inputs verified',
            determinism=dict(ranking_ids_equal=all(r.get('ids_equal',True) for r in checks),
                ranking_scores_exact=all(r.get('scores_exact',True) for r in checks),
                query_vectors_bytes_exact=all(r.get('bytes_exact',True) for r in checks),
                max_score_abs_delta=max(r.get('max_score_abs_delta',0) for r in checks)),
            finished_at_utc=datetime.now(timezone.utc).isoformat())
        for method in METHODS:
            save_json(output / f'method-{method}-manifest.json', dict(method=method, status='success',
                configuration=state['method_config'][method], seed=seed, passes=3, scoring_pass=1,
                queries_sha256=state['queries_sha256'], frozen_child_sha256=frozen['frozen_child_sha256'],
                code_sha256=state['code_sha256'], timings_file='query_timings.jsonl'))
        save_json(output / 'progress.json', dict(status=state['status'], completed_queries_by_pass=state['completed_queries_by_pass']))
        # Review/scoring may begin after pass 1. Only the runner's explicit outputs
        # participate in its manifest, irrespective of concurrent review files.
        artifact_names = set(journal.streams) | {'preflight.json', 'queries.jsonl', 'progress.json'}
        artifact_names |= {f'method-{m}-manifest.json' for m in METHODS}
        for pass_number in (1, 2, 3):
            artifact_names |= {f'pass-{pass_number}/query_vectors.npy', f'pass-{pass_number}/query_vector_ids.json'}
            artifact_names |= {f'pass-{pass_number}/query-vector-{q["intent_id"]}.npy' for q in queries}
        state['output_sha256'] = {name:sha(output / name) for name in sorted(artifact_names)}
        save_json(output / 'run_manifest.json', state)
    except BaseException as error:
        journal.close()
        state.update(status='partial_execution_failure', finished_at_utc=datetime.now(timezone.utc).isoformat())
        state['execution_failures'].append(dict(**current, error_type=type(error).__name__, message=str(error),
            traceback=traceback.format_exc(), quality_score=None))
        save_json(output / 'run_manifest.json', state)
        save_json(output / 'progress.json', dict(**current, status=state['status'], error=str(error)))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--preflight', type=Path, required=True)
    parser.add_argument('--queries', type=Path, required=True)
    args = parser.parse_args()
    run(args.output_dir.resolve(), args.preflight.resolve(), args.queries.resolve())
