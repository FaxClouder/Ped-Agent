"""Run the eight-intent PEARL development comparison on the frozen Adobe child library."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import time

import build


ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / 'outputs/pearl-index-106-adobe-20260929-01'
GOLD = ROOT / 'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json'
CORPUS = ROOT / 'paper/pearl-framework/datasets/retrieval-corpus/corpus-manifest-v02.jsonl'
RERANKER = ROOT / 'memPed/knowledge/models/bge-reranker-v2-m3'
DEPTH = 100
RRF_K = 60


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def rrf_union(sparse: list[dict], dense: list[dict], k: int = RRF_K) -> list[dict]:
    scores: dict[str, dict] = {}
    for label, ranking in (('r1', sparse), ('r2', dense)):
        for rank, row in enumerate(ranking, 1):
            ident = row['chunk_id']
            item = scores.setdefault(ident, {'chunk_id': ident, 'score': 0.0,
                                             'r1_rank': None, 'r2_rank': None})
            item['score'] += 1 / (k + rank)
            item[f'{label}_rank'] = rank
    return sorted(scores.values(), key=lambda row: (-row['score'], row['chunk_id']))


def attach_children(ranking: list[dict], children: dict[str, dict]) -> list[dict]:
    result = []
    for rank, row in enumerate(ranking, 1):
        child = children[row['chunk_id']]
        if text_sha(child['text']) != child['text_sha256']:
            raise ValueError(f"child text hash mismatch: {row['chunk_id']}")
        result.append({'rank': rank, 'score': row['score'], **child})
    return result


def preflight(index: Path, gold_path: Path) -> tuple[dict, dict, dict[str, dict], list[str]]:
    manifest = json.loads((index / 'build_manifest.json').read_text(encoding='utf-8'))
    verified = json.loads((index / 'verification.json').read_text(encoding='utf-8'))
    if verified['status'] != 'passed' or verified['build_manifest_sha256'] != sha(index / 'build_manifest.json'):
        raise ValueError('index verification is absent or stale')
    for name in ('child_chunks.jsonl', 'dense_ids.json', 'dense_vectors.npy', 'fts.sqlite3'):
        if sha(index / name) != manifest['output_sha256'][name]:
            raise ValueError(f'frozen index artifact changed: {name}')
    if sha(CORPUS) != manifest['input_sha256']['paper\\pearl-framework\\datasets\\retrieval-corpus\\corpus-manifest-v02.jsonl']:
        raise ValueError('corpus manifest differs from the frozen index')
    gold = json.loads(gold_path.read_text(encoding='utf-8'))
    if gold['corpus_version'] != manifest['corpus_version'] or gold['corpus_manifest_sha256'] != sha(CORPUS):
        raise ValueError('Gold corpus binding differs from index')
    if gold['revision']['frozen_child_library_sha256'] != sha(index / 'child_chunks.jsonl'):
        raise ValueError('Gold child library binding differs from index')
    sources = {row['source_id']: row for row in read_jsonl(CORPUS)}
    for row in gold['source_bindings']:
        if row['source_sha256'] != sources[row['source_id']]['sha256']:
            raise ValueError('Gold source hash differs from corpus')
    if len(gold['intents']) != 8:
        raise ValueError('pilot must contain exactly eight intents')
    child_rows = read_jsonl(index / 'child_chunks.jsonl')
    children = {row['chunk_id']: row for row in child_rows}
    ids = json.loads((index / 'dense_ids.json').read_text(encoding='utf-8'))
    if len(child_rows) != len(children) or set(ids) != set(children) or len(ids) != manifest['child_count']:
        raise ValueError('frozen child membership differs from dense IDs')
    return manifest, gold, children, ids


def encode_queries(queries: list[str], manifest: dict):
    import numpy as np
    import torch
    from FlagEmbedding import BGEM3FlagModel

    model_path = ROOT / 'memPed/knowledge/models/bge-m3'
    for relative, record in manifest['dense']['model_manifest']['weights'].items():
        path = model_path / relative
        if not path.is_file() or sha(path) != record['sha256']:
            raise ValueError(f'BGE-M3 weight missing or changed: {relative}')
    for relative in ('tokenizer.json', 'tokenizer_config.json', 'sentencepiece.bpe.model'):
        if sha(model_path / relative) != manifest['dense']['actual_asset_sha256'][relative]:
            raise ValueError(f'BGE-M3 tokenizer changed: {relative}')
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable for the pinned BGE-M3 query encoder')
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    torch.manual_seed(manifest['seed'])
    torch.cuda.manual_seed_all(manifest['seed'])
    model = BGEM3FlagModel(str(model_path), devices='cuda:0', use_fp16=True,
                           normalize_embeddings=True, query_instruction_for_retrieval=None)
    tokenizer = model.tokenizer
    records = []
    vectors = []
    for query in queries:
        tokens = tokenizer(query, add_special_tokens=True, truncation=False)['input_ids']
        if len(tokens) > manifest['dense']['max_length']:
            raise ValueError('query would be truncated')
        started = time.perf_counter()
        encoded = model.encode([query], batch_size=8, max_length=1024,
                               return_dense=True, return_sparse=False, return_colbert_vecs=False)
        vector = np.asarray(encoded['dense_vecs'][0], dtype=np.float32)
        vector /= np.linalg.norm(vector)
        vectors.append(vector)
        records.append({'query': query, 'token_ids': tokens, 'token_count': len(tokens),
                        'truncated': False, 'encode_seconds': time.perf_counter() - started})
    return np.stack(vectors), records


def main() -> None:
    import numpy as np

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--index-dir', type=Path, default=INDEX)
    parser.add_argument('--gold', type=Path, default=GOLD)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists():
        raise SystemExit(f'refusing to overwrite existing research output: {output}')
    index = args.index_dir.resolve()
    gold_path = args.gold.resolve()
    manifest, gold, children, ids = preflight(index, gold_path)
    vectors = np.load(index / 'dense_vectors.npy', allow_pickle=False)
    build.validate_vectors(vectors, len(ids))
    queries = [row['query'] for row in gold['intents']]
    query_vectors, query_records = encode_queries(queries, manifest)
    reranker_status = ('asset_present_unverified' if RERANKER.is_dir()
                       else 'not_executed_local_model_asset_absent')
    output.mkdir(parents=True, exist_ok=False)
    np.save(output / 'query_vectors.npy', query_vectors, allow_pickle=False)
    write_jsonl(output / 'query_inputs.jsonl', query_records)
    rankings: list[dict] = []
    unions: list[dict] = []
    per_query: list[dict] = []
    pool: list[dict] = []
    required: list[dict] = []
    rng = random.Random(manifest['seed'])
    for intent, query_vector in zip(gold['intents'], query_vectors, strict=True):
        query = intent['query']
        ident = intent['intent_id']
        t0 = time.perf_counter()
        sparse = build.sparse_query(index / 'fts.sqlite3', query, limit=DEPTH)
        sparse_seconds = time.perf_counter() - t0
        t0 = time.perf_counter()
        dense = build.exact_dense(vectors, query_vector, ids, limit=DEPTH)
        dense_seconds = time.perf_counter() - t0
        t0 = time.perf_counter()
        union = rrf_union(sparse, dense, RRF_K)
        fusion_seconds = time.perf_counter() - t0
        final = {'R1': sparse, 'R2': dense, 'R3': union[:DEPTH]}
        for method, rows in final.items():
            rankings.append({'intent_id': ident, 'query': query, 'method': method,
                             'returned': len(rows), 'results': attach_children(rows, children)})
        unions.append({'intent_id': ident, 'query': query, 'rrf_k': RRF_K,
                       'union': [dict(rank=i, **row, in_top100=i <= DEPTH)
                                 for i, row in enumerate(union, 1)]})
        per_query.append({'intent_id': ident, 'query_encode_seconds': query_records[len(per_query)]['encode_seconds'],
                          'r1_search_seconds': sparse_seconds, 'r2_exact_search_seconds': dense_seconds,
                          'r3_fusion_seconds': fusion_seconds})
        all_ids = {row['chunk_id'] for method in final.values() for row in method}
        # Source anchored children widen the pool beyond retrieved candidates.
        source_ids = {atom['source_id'] for atom in intent['atoms']}
        all_ids |= {cid for cid, child in children.items() if child['source_id'] in source_ids}
        pool_rows = [children[cid] for cid in sorted(all_ids)]
        rng.shuffle(pool_rows)
        pool.extend({'intent_id': ident, **child} for child in pool_rows)
        first20 = {row['chunk_id'] for method in final.values() for row in method[:20]}
        required_rows = [children[cid] for cid in sorted(first20)]
        rng.shuffle(required_rows)
        required.extend({'intent_id': ident, **child} for child in required_rows)
    write_jsonl(output / 'rankings.jsonl', rankings)
    write_jsonl(output / 'rrf_union.jsonl', unions)
    write_jsonl(output / 'review_pool_blind.jsonl', pool)
    write_jsonl(output / 'review_required_top20_blind.jsonl', required)
    write_jsonl(output / 'query_timings.jsonl', per_query)
    write_json(output / 'reranker_status.json', {'method': 'R4', 'model_id': 'BAAI/bge-reranker-v2-m3',
        'status': reranker_status, 'local_path': str(RERANKER),
        'reason': 'No verified local model manifest and weights available' if not RERANKER.is_dir()
                  else 'Asset requires revision, weight hash, tokenizer and input validation before execution'})
    files = ('query_vectors.npy', 'query_inputs.jsonl', 'rankings.jsonl', 'rrf_union.jsonl',
             'review_pool_blind.jsonl', 'review_required_top20_blind.jsonl',
             'query_timings.jsonl', 'reranker_status.json')
    write_json(output / 'run_manifest.json', {
        'status': 'retrieval_complete_support_review_pending', 'run_id': output.name,
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'protocol': 'retrieval-v0.2',
        'split': 'eight_intent_development_pilot', 'gold_sha256': sha(gold_path),
        'corpus_manifest_sha256': sha(CORPUS), 'index_build_manifest_sha256': sha(index / 'build_manifest.json'),
        'frozen_child_sha256': sha(index / 'child_chunks.jsonl'), 'dense_ids_sha256': sha(index / 'dense_ids.json'),
        'dense_vectors_sha256': sha(index / 'dense_vectors.npy'), 'fts_sha256': sha(index / 'fts.sqlite3'),
        'index_content_sha256': manifest['content_sha256'], 'source_count': manifest['source_count'],
        'child_count': manifest['child_count'], 'methods_executed': ['R1', 'R2', 'R3'],
        'r4_status': reranker_status, 'depth': DEPTH, 'rrf_k': RRF_K,
        'r1': manifest['sparse'], 'r2': {'model': manifest['dense']['model_manifest'],
             'metric': 'float32 exact cosine via dot product of stored unit vectors',
             'query_encoding': 'CUDA FP16 BGE-M3 dense only; unit normalized; no instruction'},
        'tie_break': 'chunk_id ascending', 'seed': manifest['seed'],
        'code_sha256': {'compare_pilot.py': sha(Path(__file__)), 'build.py': sha(Path(build.__file__))},
        'output_sha256': {name: sha(output / name) for name in files},
        'support_review': 'pending; no CEGR or related scores computed'})
    print(json.dumps({'run': str(output), 'intents': len(gold['intents']),
                      'rankings': len(rankings), 'r4_status': reranker_status}))


if __name__ == '__main__':
    main()
