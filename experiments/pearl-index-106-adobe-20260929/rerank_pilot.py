"""Rerank frozen Adobe-106 R3 Top-100 with a verified local BGE reranker."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
R3_RUN = ROOT / 'outputs/pearl-retrieval-dev-pilot-8-adobe106-20260929-01'
GOLD = ROOT / 'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json'
CONFIG = HERE / 'reranker-config.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def write_json(path: Path, item: dict) -> None:
    path.write_text(json.dumps(item, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')


def write_jsonl(path: Path, items: list[dict]) -> None:
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        for item in items:
            stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + '\n')


def rerank_results(original: list[dict], scores: list[float]) -> list[dict]:
    if len(scores) != len(original) or any(not math.isfinite(float(score)) for score in scores):
        raise ValueError('scores must be finite and correspond one-to-one with R3 candidates')
    if len({row['chunk_id'] for row in original}) != len(original):
        raise ValueError('duplicate R3 candidate IDs')
    ranked = [dict(row, score=float(score), r3_rank=row['rank']) for row, score in zip(original, scores)]
    ranked.sort(key=lambda row: (-row['score'], row['chunk_id']))
    for index, row in enumerate(ranked, 1):
        row['rank'] = index
    return ranked


def audit_inputs(tokenizer, query: str, rows: list[dict], config: dict) -> list[dict]:
    from FlagEmbedding.utils.tokenizer_compat import prepare_for_model_compat

    query_raw = tokenizer(query, add_special_tokens=False)['input_ids']
    query_used = query_raw[:config['query_max_length']]
    special_count = tokenizer.num_special_tokens_to_add(pair=True)
    audited = []
    for row in rows:
        passage_raw = tokenizer(row['text'], add_special_tokens=False)['input_ids']
        passage_used = passage_raw[:config['max_length']]
        pair = prepare_for_model_compat(tokenizer, query_used, passage_used,
                                        truncation='only_second', max_length=config['max_length'],
                                        padding=False)
        audited.append({
            'chunk_id': row['chunk_id'], 'r3_rank': row['rank'],
            'query_text': query, 'query_sha256': hashlib.sha256(query.encode('utf-8')).hexdigest(),
            'child_text': row['text'], 'child_text_sha256': row['text_sha256'],
            'query_raw_tokens': len(query_raw), 'child_raw_tokens': len(passage_raw),
            'query_truncated': len(query_raw) > len(query_used),
            'child_truncated_initial': len(passage_raw) > len(passage_used),
            'child_truncated_pair': len(query_used) + len(passage_used) + special_count > config['max_length'],
            'model_input_ids': pair['input_ids'], 'model_input_length': len(pair['input_ids']),
        })
    return audited


def preflight(config: dict) -> tuple[dict, list[dict]]:
    manifest = json.loads((R3_RUN / 'run_manifest.json').read_text(encoding='utf-8'))
    if manifest['gold_sha256'] != sha(GOLD):
        raise ValueError('Gold changed')
    for name, expected in manifest['output_sha256'].items():
        if sha(R3_RUN / name) != expected:
            raise ValueError(f'frozen R1-R3 output changed: {name}')
    model_dir = ROOT / config['local_model_dir']
    for name, expected in config['verified_files_sha256'].items():
        if sha(model_dir / name) != expected:
            raise ValueError(f'model file changed: {name}')
    gold = json.loads(GOLD.read_text(encoding='utf-8'))
    queries = {row['intent_id']: row['query'] for row in gold['intents']}
    rows = [row for row in read_jsonl(R3_RUN / 'rankings.jsonl') if row['method'] == 'R3']
    if len(rows) != len(queries) or len({row['intent_id'] for row in rows}) != len(rows):
        raise ValueError('R3 intent count mismatch')
    for row in rows:
        if row['query'] != queries.get(row['intent_id']) or len(row['results']) != 100:
            raise ValueError('R3 query or candidate count mismatch')
        if [candidate['rank'] for candidate in row['results']] != list(range(1, 101)):
            raise ValueError('R3 ranks invalid')
        for candidate in row['results']:
            if hashlib.sha256(candidate['text'].encode('utf-8')).hexdigest() != candidate['text_sha256']:
                raise ValueError('R3 child text hash mismatch')
    return manifest, rows


def run(output: Path) -> None:
    if output.exists():
        raise FileExistsError(f'refusing to overwrite: {output}')
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    source_manifest, r3_rows = preflight(config)
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_HUB_OFFLINE'] = '1'
    import torch
    from FlagEmbedding import FlagReranker
    import FlagEmbedding

    if not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable; configured R4 run requires CUDA')
    random.seed(config['seed'])
    torch.manual_seed(config['seed'])
    torch.cuda.manual_seed_all(config['seed'])
    model_dir = ROOT / config['local_model_dir']
    load_start = time.perf_counter()
    model = FlagReranker(str(model_dir), devices=config['device'], use_fp16=config['use_fp16'],
                         batch_size=config['batch_size'], query_max_length=config['query_max_length'],
                         max_length=config['max_length'], normalize=config['normalize'])
    load_seconds = time.perf_counter() - load_start
    rankings, audits, timings = [], [], []
    started = datetime.now(timezone.utc).isoformat()
    for index, row in enumerate(r3_rows, 1):
        start = time.perf_counter()
        checked = audit_inputs(model.tokenizer, row['query'], row['results'], config)
        tokenization_seconds = time.perf_counter() - start
        pairs = [[row['query'], item['text']] for item in row['results']]
        start = time.perf_counter()
        scores = model.compute_score(pairs, batch_size=config['batch_size'],
                                     query_max_length=config['query_max_length'],
                                     max_length=config['max_length'], normalize=config['normalize'])
        torch.cuda.synchronize()
        inference_seconds = time.perf_counter() - start
        ranked = rerank_results(row['results'], scores)
        if {item['chunk_id']: (item['text'], item['text_sha256']) for item in ranked} != {
                item['chunk_id']: (item['text'], item['text_sha256']) for item in row['results']}:
            raise ValueError('R4 candidate or text identity mismatch')
        rankings.append({'intent_id': row['intent_id'], 'method': 'R4', 'query': row['query'],
                         'returned': len(ranked), 'results': ranked})
        audits.extend(dict(item, intent_id=row['intent_id']) for item in checked)
        timings.append({'intent_id': row['intent_id'], 'candidate_count': len(ranked),
                        'input_audit_seconds': tokenization_seconds,
                        'reranker_seconds': inference_seconds,
                        'total_seconds': tokenization_seconds + inference_seconds})
        print(f'{index}/{len(r3_rows)} {row["intent_id"]}: rerank={inference_seconds:.2f}s', flush=True)
    output.mkdir(parents=True, exist_ok=False)
    write_jsonl(output / 'rankings-r4.jsonl', rankings)
    write_jsonl(output / 'model-inputs-r4.jsonl', audits)
    write_jsonl(output / 'query-timings-r4.jsonl', timings)
    files = ('rankings-r4.jsonl', 'model-inputs-r4.jsonl', 'query-timings-r4.jsonl')
    write_json(output / 'run_manifest.json', {
        'run_id': output.name, 'status': 'retrieval_complete_support_review_pending',
        'created_at_utc': started, 'finished_at_utc': datetime.now(timezone.utc).isoformat(),
        'split': 'eight_intent_development_pilot', 'method': 'R4', 'protocol': source_manifest['protocol'],
        'source_run_id': source_manifest['run_id'],
        'source_run_manifest_sha256': sha(R3_RUN / 'run_manifest.json'),
        'r3_rankings_sha256': sha(R3_RUN / 'rankings.jsonl'),
        'gold_sha256': sha(GOLD), 'corpus_manifest_sha256': source_manifest['corpus_manifest_sha256'],
        'frozen_child_sha256': source_manifest['frozen_child_sha256'],
        'config_sha256': sha(CONFIG), 'code_sha256': sha(Path(__file__)), 'config': config,
        'model_load_seconds': load_seconds, 'torch_version': torch.__version__,
        'flagembedding_version': __import__('importlib.metadata', fromlist=['version']).version('FlagEmbedding'),
        'cuda_device': torch.cuda.get_device_name(0),
        'input_count': len(audits), 'intent_count': len(rankings),
        'truncated_input_count': sum(item['query_truncated'] or item['child_truncated_initial'] or item['child_truncated_pair'] for item in audits),
        'output_sha256': {name: sha(output / name) for name in files},
        'tie_break': 'chunk_id ascending',
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    run(parser.parse_args().output_dir.resolve())
