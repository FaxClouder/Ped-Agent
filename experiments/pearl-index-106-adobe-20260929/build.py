"""Build fresh PEARL Adobe-only indexes; no Gold, scoring, or Catalog mutation.

Run from the repository root with --output-dir outputs/<new-unique-name>.
The child library is copied verbatim from a read-only SQLite snapshot.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
for directory in ('Contracts', 'Knowledge-Base'):
    sys.path.insert(0, str(ROOT / directory / 'src'))
from ped_knowledge.indexing import FTSIndex
from ped_knowledge.tokenization import EnglishLexicalAnalyzer

PARSER = 'adobe-pdf-extract-v1'
POLICY = 'parent-child-v1'
TOKENIZER = 'regex-token-v1'
SEED = 20260929
CORPUS = ROOT / 'paper/pearl-framework/datasets/retrieval-corpus'
CATALOG = ROOT / 'memPed/knowledge/knowledge.sqlite3'
MODEL = ROOT / 'memPed/knowledge/models/bge-m3'
SMOKE_QUERY = 'pedestrian bottleneck flow'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def jsonl(path, rows):
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def unique(rows, key):
    values = [r[key] for r in rows]
    if len(values) != len(set(values)):
        raise ValueError(f'duplicate {key}')
    return set(values)


def validate_members(sources, verified, expected_count=106):
    for key in ('source_id', 'sha256'):
        unique(sources, key)
    for key in ('source_id', 'source_sha256'):
        unique(verified['sources'], key)
    if len(sources) != expected_count or verified['source_count'] != expected_count:
        raise ValueError('unexpected source count')
    actual = {(s['source_id'], s['sha256']) for s in sources}
    expected = {(s['source_id'], s['source_sha256']) for s in verified['sources']}
    if actual != expected:
        raise ValueError('manifest and verification membership differ')
    if any(s['parser_version'] != PARSER for s in verified['sources']):
        raise ValueError('non-Adobe member')
    return {s['sha256']: s for s in sources}


def create_output(path):
    path.mkdir(parents=True, exist_ok=False)


def read_snapshot(catalog, sources, verified, root=ROOT):
    members = validate_members(sources, verified)
    checks = {s['source_sha256']: s for s in verified['sources']}
    placeholders = ','.join('?' for _ in members)
    source_rows, children, parents = [], [], []
    with closing(sqlite3.connect(catalog.resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA query_only=ON')
        conn.execute('BEGIN')
        versions = [dict(r) for r in conn.execute(f'''SELECT v.*, r.title,
            r.active_version_id FROM resource_versions v JOIN resources r
            ON r.resource_id=v.resource_id WHERE v.sha256 IN ({placeholders})
            AND r.active_version_id=v.version_id''', tuple(members))]
        if len(versions) != len(members) or {v['sha256'] for v in versions} != set(members):
            raise ValueError('missing or duplicate active source membership')
        for version in versions:
            member, check = members[version['sha256']], checks[version['sha256']]
            if version['parser_version'] != PARSER or version['status'] != 'active':
                raise ValueError('non-Adobe or inactive source')
            for key in ('resource_id', 'active_version_id'):
                if version[key] != check[key]:
                    raise ValueError(f'source identity mismatch: {key}')
            source_path = root / member['source_path']
            if sha(source_path) != member['sha256']:
                raise ValueError(f'source SHA mismatch: {source_path}')
            relative = Path(version['derived_path']) / 'document.json'
            candidates = {(base / relative).resolve() for base in (root / 'memPed/knowledge', root / 'memPed') if (base / relative).is_file()}
            if len(candidates) != 1:
                raise ValueError(f'ambiguous/missing derived path: {relative}')
            document = candidates.pop()
            if document != (root / check['document_path']).resolve() or sha(document) != check['document_sha256']:
                raise ValueError(f'canonical document mismatch: {document}')
            rows = [dict(r) for r in conn.execute('''SELECT * FROM chunks
                WHERE resource_id=? AND version_id=? AND policy_version=?
                AND tokenizer_fingerprint=? ORDER BY chunk_id''',
                (version['resource_id'], version['version_id'], POLICY, TOKENIZER))]
            if not rows or any(r['parser_version'] != PARSER for r in rows):
                raise ValueError('missing or non-Adobe chunks')
            if not any(r['chunk_level'] == 'child' for r in rows):
                raise ValueError('source has no children')
            source_rows.append(dict(member, catalog_version=version, document_path=check['document_path'],
                                    document_sha256=check['document_sha256'], child_count=sum(r['chunk_level']=='child' for r in rows)))
            for row in rows:
                row.update(source_id=member['source_id'], source_sha256=member['sha256'], title=version['title'], text_sha256=text_sha(row['text']))
                if row['chunk_level'] == 'child':
                    children.append(row)
                elif row['chunk_level'] == 'parent':
                    parents.append(row)
                else:
                    raise ValueError('unexpected chunk level')
        conn.rollback()
    unique(children + parents, 'chunk_id')
    parent_by_id = {r['chunk_id']: r for r in parents}
    for child in children:
        parent = parent_by_id.get(child['parent_chunk_id'])
        if parent is None or parent['source_id'] != child['source_id']:
            raise ValueError('missing or foreign parent')
        child['parent_text_sha256'] = parent['text_sha256']
    counts = verified['catalog_chunk_inventory']
    if len(children) != counts['child'] or len(parents) != counts['parent']:
        raise ValueError('chunk inventory changed since membership verification')
    return (sorted(source_rows, key=lambda r:r['source_id']),
            sorted(children, key=lambda r:r['chunk_id']), sorted(parents, key=lambda r:r['chunk_id']))


def build_fts(path, children, digest, revision):
    unique(children, 'chunk_id')
    if path.exists():
        raise FileExistsError(path)
    # All metadata remains in the frozen library, but contributes neither tokens nor length.
    rows = [dict(row, title='', heading_path=[]) for row in children]
    FTSIndex(path, analyzer=EnglishLexicalAnalyzer()).rebuild(rows,
        source_fingerprint=digest, policy_version=POLICY,
        tokenizer_fingerprint=TOKENIZER, code_revision=revision)


def sparse_query(path, query, limit=10):
    analyzer = EnglishLexicalAnalyzer()
    tokens = sorted(set(analyzer.analyze(query)))
    if not tokens:
        return []
    match = ' OR '.join('"' + token + '"' for token in tokens)
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        fingerprint = conn.execute("SELECT value FROM index_metadata WHERE key='lexical_analyzer_fingerprint'").fetchone()
        if fingerprint is None or fingerprint[0] != analyzer.fingerprint:
            raise ValueError('lexical analyzer fingerprint mismatch')
        rows = conn.execute('''SELECT chunk_id,
            bm25(documents, 0, 0, 0, 0, 0, 1, 0) AS rank FROM documents
            WHERE body MATCH ? ORDER BY rank ASC, chunk_id ASC LIMIT ?''', (match, limit))
        return [dict(chunk_id=r[0], sqlite_rank=r[1], score=-r[1]) for r in rows]


def verify_fts(path, children):
    expected = {row['chunk_id']:row for row in children}
    analyzer = EnglishLexicalAnalyzer()
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM documents').fetchall()
    if len(rows) != len(expected) or {r['chunk_id'] for r in rows} != set(expected):
        raise ValueError('FTS membership mismatch')
    for row in rows:
        original = expected[row['chunk_id']]
        if (row['body'] != ' '.join(analyzer.analyze(original['text']))
                or row['title'] != '' or row['heading'] != ''
                or any(row[k] != original[k] for k in ('resource_id','version_id','locator'))):
            raise ValueError('FTS content mismatch')


def content_digest(rows, vectors):
    """Canonical JSON row + newline + 1024 little-endian float32 bytes, sorted by ID."""
    import numpy as np
    digest = hashlib.sha256()
    for i in sorted(range(len(rows)), key=lambda i:rows[i]['chunk_id']):
        digest.update(json.dumps(rows[i], sort_keys=True, ensure_ascii=False,
                                 separators=(',', ':')).encode('utf-8') + b'\n')
        digest.update(np.asarray(vectors[i], dtype='<f4').tobytes())
    return digest.hexdigest()


def validate_vectors(vectors, count):
    import numpy as np
    if vectors.shape != (count, 1024) or not np.isfinite(vectors).all():
        raise ValueError('vectors must have finite shape N x 1024')
    if not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5):
        raise ValueError('vectors must have unit norm')


def exact_dense(vectors, query, ids, limit=10):
    import numpy as np
    scores = vectors @ np.asarray(query, dtype=np.float32)
    ordered = sorted(range(len(ids)), key=lambda i: (-float(scores[i]), ids[i]))[:limit]
    return [dict(chunk_id=ids[i], score=float(scores[i])) for i in ordered]


def code_provenance():
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    # Hash every consumed Python module, including dirty and untracked source files.
    paths = list((ROOT / 'Knowledge-Base/src/ped_knowledge').rglob('*.py'))
    paths += list((ROOT / 'Contracts/src/ped_contracts').rglob('*.py'))
    paths += list(Path(__file__).parent.glob('*.py'))
    return dict(git_revision=revision,
                git_status=subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True),
                consumed_code_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)})


def build_dense(output, children, digest):
    for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_DATASETS_OFFLINE'):
        os.environ[key] = '1'
    os.environ['ANONYMIZED_TELEMETRY'] = 'False'
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    import numpy as np
    import torch
    import chromadb
    from chromadb.config import Settings
    from FlagEmbedding import BGEM3FlagModel
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required; CPU fallback is disabled')
    model_manifest = json.loads((MODEL / 'model_manifest.json').read_text(encoding='utf-8'))
    assets = {}
    for name, expected in model_manifest['weights'].items():
        path = MODEL / name
        actual = sha(path)
        if actual != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError(f'model weight mismatch: {name}')
        assets[name] = actual
    # A newly added safetensors file would change HF weight selection.
    if list(MODEL.glob('*.safetensors')):
        raise ValueError('unverified safetensors weights present')
    for path in MODEL.rglob('*'):
        if path.is_file() and '.cache' not in path.parts and 'onnx' not in path.parts and path.suffix in ('.json', '.model', '.pt'):
            assets[path.relative_to(MODEL).as_posix()] = sha(path)
    model = BGEM3FlagModel(str(MODEL), devices='cuda:0', use_fp16=True,
                           normalize_embeddings=True, query_instruction_for_retrieval=None)
    lengths = []
    model_inputs = []
    texts = [row['text'] for row in children]
    for start in range(0, len(texts), 64):
        tokenized = model.tokenizer(texts[start:start+64], truncation=False,
                                    add_special_tokens=True, padding=False)
        lengths.extend(len(ids) for ids in tokenized['input_ids'])
        truncated = model.tokenizer(texts[start:start+64], truncation=True,
                                    max_length=1024, add_special_tokens=True, padding=False)
        for i in range(len(truncated['input_ids'])):
            model_inputs.append(dict(chunk_id=children[start+i]['chunk_id'],
                **{key:values[i] for key,values in truncated.items()}))
    jsonl(output / 'model_inputs.jsonl', model_inputs)
    length_rows = [dict(chunk_id=r['chunk_id'], raw_tokens=n, max_length=1024,
                        truncated=n > 1024) for r, n in zip(children, lengths, strict=True)]
    jsonl(output / 'token_lengths.jsonl', length_rows)
    dump(output / 'truncated_child_ids.json', [r['chunk_id'] for r in length_rows if r['truncated']])
    batches = []
    for start in range(0, len(texts), 8):
        encoded = model.encode(texts[start:start+8], batch_size=8, max_length=1024,
            return_dense=True, return_sparse=False, return_colbert_vecs=False)
        values = np.asarray(encoded['dense_vecs'], dtype=np.float32)
        # Persist these same float32 unit vectors in both Chroma and NPY.
        values /= np.linalg.norm(values, axis=1, keepdims=True)
        batches.append(values)
        if start % 256 == 0:
            print(f'dense {min(start+8,len(texts))}/{len(texts)}', flush=True)
    vectors = np.concatenate(batches)
    validate_vectors(vectors, len(children))
    np.save(output / 'dense_vectors.npy', vectors, allow_pickle=False)
    ids = [r['chunk_id'] for r in children]
    dump(output / 'dense_ids.json', ids)
    client = chromadb.PersistentClient(path=str(output / 'chroma'), settings=Settings(anonymized_telemetry=False))
    collection = client.create_collection('pearl_106_adobe_bge_m3', embedding_function=None,
        metadata={'corpus_content_sha256':digest, 'hnsw:space':'cosine', 'hnsw:num_threads':1})
    for start in range(0, len(ids), 128):
        batch = children[start:start+128]
        collection.add(ids=ids[start:start+128], documents=texts[start:start+128],
            embeddings=vectors[start:start+128].tolist(), metadatas=[dict(
                source_id=r['source_id'], source_sha256=r['source_sha256'],
                text_sha256=r['text_sha256'], resource_id=r['resource_id'],
                version_id=r['version_id'], parent_chunk_id=r['parent_chunk_id'],
                policy_version=POLICY, tokenizer_fingerprint=TOKENIZER) for r in batch])
    stored = collection.get(include=['documents', 'metadatas', 'embeddings'])
    unique([{'id':i} for i in stored['ids']], 'id')
    if set(stored['ids']) != set(ids) or collection.count() != len(ids):
        raise ValueError('Chroma membership mismatch')
    positions = {value:i for i,value in enumerate(ids)}
    for i, stored_id in enumerate(stored['ids']):
        index = positions[stored_id]
        row = children[index]
        if text_sha(stored['documents'][i]) != row['text_sha256'] or stored['metadatas'][i]['source_id'] != row['source_id']:
            raise ValueError('Chroma text/source mismatch')
        if not np.allclose(stored['embeddings'][i], vectors[index], atol=1e-7):
            raise ValueError('Chroma vector mismatch')
    validate_vectors(np.asarray(stored['embeddings']), len(ids))
    stored_rows = [dict(chunk_id=stored_id, text=stored['documents'][i],
                        metadata=stored['metadatas'][i]) for i,stored_id in enumerate(stored['ids'])]
    dense_digest = content_digest(stored_rows, stored['embeddings'])
    encoded = model.encode([SMOKE_QUERY], batch_size=8, max_length=1024,
                            return_dense=True, return_sparse=False, return_colbert_vecs=False)
    query = np.asarray(encoded['dense_vecs'][0], dtype=np.float32)
    query /= np.linalg.norm(query)
    np.save(output / 'smoke_query_vector.npy', query, allow_pickle=False)
    approximate = collection.query(query_embeddings=[query.tolist()], n_results=10,
                                   include=['distances'])
    ann_smoke = [dict(chunk_id=i, cosine_distance=d) for i,d in
                 zip(approximate['ids'][0], approximate['distances'][0], strict=True)]
    dense_smoke = exact_dense(vectors, query, ids)
    info = dict(model_manifest=model_manifest, actual_asset_sha256=assets,
        device=torch.cuda.get_device_name(0), torch_cuda=torch.version.cuda,
        dense_dimensions=1024, batch_size=8, max_length=1024, use_fp16=True,
        normalize_embeddings=True, storage_dtype='float32', query_instruction=None,
        raw_lengths_include_special_tokens=True, truncation_side=model.tokenizer.truncation_side,
        input_view='model_inputs.jsonl: unpadded input IDs and attention masks; batches dynamically padded',
        truncation_count=sum(n > 1024 for n in lengths), deterministic_algorithms=True,
        ann=dict(engine='Chroma HNSW', metric='cosine', num_threads=1,
                 seed='not exposed by installed Chroma configuration; no ANN bitwise guarantee',
                 collection_configuration=collection.configuration['hnsw']),
        exact_scoring='float32 dot product of stored unit vectors; ties by chunk_id ascending')
    info.update(content_sha256=dense_digest,
        content_digest_spec='sort by chunk_id; UTF-8 compact sorted JSON {chunk_id,text,metadata} + newline + little-endian float32 vector bytes')
    return info, dict(exact_cosine=dense_smoke, approximate_hnsw=ann_smoke,
                      top10_overlap=len({r['chunk_id'] for r in dense_smoke} & {r['chunk_id'] for r in ann_smoke}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    create_output(output)
    started = time.perf_counter()
    manifest = dict(status='building', started_at=datetime.now(timezone.utc).isoformat(),
                    seed=SEED, output_dir=str(output), purpose='isolated index build; no scored pilot',
                    timings_seconds={})
    try:
        manifest.update(code_provenance())
        source_path = CORPUS / 'corpus-manifest-v02.jsonl'
        verified_path = CORPUS / 'adobe-membership-verification-v02.json'
        sources = [json.loads(line) for line in source_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        verified = json.loads(verified_path.read_text(encoding='utf-8'))
        if sha(source_path) != verified['corpus_manifest_sha256']:
            raise ValueError('corpus manifest hash changed')
        manifest['input_sha256'] = {str(p.relative_to(ROOT)):sha(p) for p in (source_path, verified_path, CATALOG)}
        source_rows, children, parents = read_snapshot(CATALOG, sources, verified)
        jsonl(output / 'sources.jsonl', source_rows)
        jsonl(output / 'child_chunks.jsonl', children)
        jsonl(output / 'parent_chunks.jsonl', parents)
        digest = sha(output / 'child_chunks.jsonl')
        manifest.update(corpus_version=verified['corpus_version'], content_sha256=digest,
            source_count=len(source_rows), child_count=len(children), parent_count=len(parents),
            parser_version=PARSER, policy_version=POLICY, tokenizer_fingerprint=TOKENIZER)
        manifest['timings_seconds']['snapshot'] = time.perf_counter() - started
        tick = time.perf_counter()
        fts_path = output / 'fts.sqlite3'
        build_fts(fts_path, children, digest, manifest['git_revision'])
        verify_fts(fts_path, children)
        manifest['sparse'] = dict(analyzer_fingerprint=EnglishLexicalAnalyzer().fingerprint,
            fields='body only; title and heading empty', query='OR of unique English tokens',
            bm25=dict(k1=1.2,b=0.75,idf='max(ln((N-df+0.5)/(df+0.5)),1e-6)',
                      score='negative SQLite rank', log1p=False),
            ordering='SQLite rank ASC, chunk_id ASC', old_scores_comparable=False)
        manifest['timings_seconds']['sparse'] = time.perf_counter() - tick
        dump(output / 'build_manifest.json', manifest)
        tick = time.perf_counter()
        dense_info, dense_smoke = build_dense(output, children, digest)
        manifest['dense'] = dense_info
        manifest['timings_seconds']['dense'] = time.perf_counter() - tick
        dump(output / 'smoke.json', dict(query=SMOKE_QUERY, purpose='unscored generic smoke',
            sparse=sparse_query(fts_path, SMOKE_QUERY), dense=dense_smoke,
            source_count=len(source_rows), child_count=len(children), ids_equal=True))
        manifest['dependencies'] = {name:importlib.metadata.version(name) for name in
            ('numpy','torch','transformers','tokenizers','FlagEmbedding','chromadb')}
        manifest['sqlite_version'] = sqlite3.sqlite_version
        manifest['python'] = sys.version
        manifest['output_sha256'] = {p.relative_to(output).as_posix():sha(p)
            for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'build_manifest.json'
            and 'chroma' not in p.relative_to(output).parts}
        manifest['chroma_file_hash_note'] = 'Physical files excluded: may change during shutdown; canonical content digest verified instead.'
        manifest['status'] = 'complete'
    except BaseException as exc:
        manifest.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        manifest['timings_seconds']['total'] = time.perf_counter() - started
        manifest['finished_at'] = datetime.now(timezone.utc).isoformat()
        dump(output / 'build_manifest.json', manifest)


if __name__ == '__main__':
    main()
