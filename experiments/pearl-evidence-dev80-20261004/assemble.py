"""Fixed-ranking, Gold-isolated Layer 2 assembly; no retrieval entry points."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Knowledge-Base/src'))
from ped_knowledge.tokenization import HuggingFaceTokenCounter


def text_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line]


def write_json(path, data):
    with Path(path).open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def write_jsonl(path, records):
    with Path(path).open('x', encoding='utf-8', newline='\n') as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')


def load_counter(path, expected_sha256=None):
    return HuggingFaceTokenCounter.from_local_path(Path(path), expected_sha256=expected_sha256)


def validate_queries(records):
    ids = set()
    for record in records:
        if set(record) != {'intent_id', 'query'}:
            raise ValueError('expected strict query-only records')
        if record['intent_id'] in ids:
            raise ValueError('duplicate query ID')
        ids.add(record['intent_id'])
    return records


def validate_body(chunk):
    if text_sha(chunk['text']) != chunk['text_sha256']:
        raise ValueError('body hash drift: ' + chunk['chunk_id'])


def unit(chunk, rank, child_id):
    validate_body(chunk)
    fields = ('text', 'source_id', 'source_sha256', 'version_id', 'title', 'locator',
              'parser_version', 'policy_version', 'text_sha256')
    result = {k: chunk.get(k) for k in fields}
    result.update(unit_id=chunk['chunk_id'], rank=rank, child_ids=[child_id],
                  source_type=chunk.get('chunk_level', 'child'), truncated=False, discarded_text='')
    return result


def serialize(units):
    return '\n\n'.join(f"[Source {u['source_id']} | {u['locator']}]\nTitle: {u['title']}\n{u['text']}" for u in units)


def snapshot(units, counter):
    text = serialize(units)
    return dict(units=copy.deepcopy(units), serialized_context=text,
                text_sha256=text_sha(text), token_count=counter.count(text))


def assemble(intent_id, query, children, parents, counter, strategy, budget):
    start = time.perf_counter()
    if strategy not in {'C0', 'C1'} or budget <= 0:
        raise ValueError('invalid strategy/budget')
    children = children[:10]
    if len({c['chunk_id'] for c in children}) != len(children):
        raise ValueError('duplicate child ID')
    raw, expanded, trace = [], [], []
    for rank, child in enumerate(children, 1):
        if child.get('rank', rank) != rank:
            raise ValueError('ranking order drift')
        raw.append(unit(child, rank, child['chunk_id']))
        chosen, reason = child, 'no_expansion'
        parent_id = child.get('parent_chunk_id')
        if strategy == 'C1':
            parent = parents.get(parent_id)
            reason = 'missing_parent'
            if parent is not None:
                validate_body(parent)
                if parent['chunk_id'] != parent_id:
                    raise ValueError('parent ID mismatch')
                for field in ('version_id', 'source_id', 'source_sha256', 'policy_version', 'parser_version'):
                    if child.get(field) != parent.get(field):
                        raise ValueError('parent version/source mismatch: ' + field)
                if child.get('parent_text_sha256') and child['parent_text_sha256'] != parent['text_sha256']:
                    raise ValueError('parent text hash drift')
                if child['text'] in parent['text']:
                    chosen, reason = parent, 'parent_contains_child'
                else:
                    reason = 'containment_failed'
        u = unit(chosen, rank, child['chunk_id'])
        if chosen is not child:
            u['source_type'] = 'parent'
        expanded.append(u)
        trace.append(dict(child_id=child['chunk_id'], parent_id=parent_id, selected_id=u['unit_id'], reason=reason))
    dedup, seen = [], {}
    for u in expanded:
        if u['unit_id'] in seen:
            old = seen[u['unit_id']]
            if old['text_sha256'] != u['text_sha256']:
                raise ValueError('duplicate unit body drift')
            old['child_ids'].extend(x for x in u['child_ids'] if x not in old['child_ids'])
        else:
            v = copy.deepcopy(u); dedup.append(v); seen[v['unit_id']] = v
    kept, cuts, stopped = [], [], False
    for u in dedup:
        if stopped:
            cuts.append(dict(unit_id=u['unit_id'], reason='after_budget_stop', discarded_text=u['text']))
            continue
        if counter.count(serialize(kept + [u])) <= budget:
            kept.append(copy.deepcopy(u)); continue
        stopped = True
        lo, hi = 0, len(u['text'])
        while lo < hi:
            mid = (lo + hi + 1) // 2
            candidate = dict(u, text=u['text'][:mid])
            if counter.count(serialize(kept + [candidate])) <= budget:
                lo = mid
            else:
                hi = mid - 1
        if lo:
            candidate = dict(u, text=u['text'][:lo], text_sha256=text_sha(u['text'][:lo]),
                             truncated=True, discarded_text=u['text'][lo:])
            kept.append(candidate)
        cuts.append(dict(unit_id=u['unit_id'], reason='prefix_truncated' if lo else 'header_cannot_fit',
                         retained_characters=lo, discarded_text=u['text'][lo:]))
    final = snapshot(kept, counter)
    if final['token_count'] > budget:
        raise ValueError('serialized budget exceeded')
    final.update(context_id=f'{intent_id}::{strategy}-{budget}', intent_id=intent_id, query=query,
                 configuration=f'{strategy}-{budget}', strategy=strategy, budget=budget,
                 tokenizer_fingerprint=counter.fingerprint, expansion_trace=trace, truncation_trace=cuts,
                 steps={name: snapshot(units, counter) for name, units in
                        [('raw', raw), ('expanded', expanded), ('deduplicated', dedup)]},
                 assembly_seconds=time.perf_counter()-start)
    return final


def verify_saved(path, counter):
    records = read_jsonl(path)
    ids = set()
    for r in records:
        if r['context_id'] in ids:
            raise ValueError('duplicate context ID')
        ids.add(r['context_id'])
        for block in [r, *r['steps'].values()]:
            if serialize(block['units']) != block['serialized_context']:
                raise ValueError('saved serialization mismatch')
            if text_sha(block['serialized_context']) != block['text_sha256']:
                raise ValueError('saved text hash mismatch')
            if counter.count(block['serialized_context']) != block['token_count']:
                raise ValueError('saved token count mismatch')
            for u in block['units']:
                if text_sha(u['text']) != u['text_sha256']:
                    raise ValueError('saved unit hash mismatch')
        if r['token_count'] > r['budget']:
            raise ValueError('saved budget exceeded')
    return len(records)


def select_intents(records, count):
    ids = [r['intent_id'] for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate type intent ID')
    groups = {}
    for r in records:
        if set(r) != {'intent_id', 'main_stratum'}:
            raise ValueError('type-only metadata required')
        groups.setdefault(r['main_stratum'], []).append(r['intent_id'])
    if len(groups) != 4 or any(len(v) != 20 for v in groups.values()):
        raise ValueError('expected four types of twenty')
    if count == 80:
        return sorted(ids)
    if count != 20:
        raise ValueError('expected 20 or 80')
    rng = random.Random(20261004)
    return sorted(x for key in sorted(groups) for x in rng.sample(sorted(groups[key]), 5))


def repository_path(path):
    path = Path(path)
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def prepare_inputs(type_path):
    """Read declared manifests and hashes; never deserialize Gold or support labels."""
    type_path = repository_path(type_path)
    old = ROOT / 'outputs/pearl-retrieval-dev80-20261003-01'
    revised = ROOT / 'outputs/pearl-retrieval-dev80-gold-r02-20261003-01'
    run_path, revision_path = old/'run_manifest.json', revised/'revision-manifest.json'
    run, revision = read_json(run_path), read_json(revision_path)
    delivery_path = revised/'delivery-manifest.json'
    delivery = read_json(delivery_path)
    matching = [revised/name for name, sha in delivery['artifacts_sha256'].items()
                if sha == revision['revised_gold_sha256']]
    if len(matching) != 1:
        raise ValueError('ambiguous declared revised Gold binding')
    gold_path = matching[0]
    index = Path(run['input_binding']['index_dir'])
    expected = {old/'rankings.jsonl':revision['base']['rankings_sha256'],
                run_path:revision['base']['run_manifest_sha256'],
                old/'queries.jsonl':revision['original_queries_sha256'],
                gold_path:revision['revised_gold_sha256'],
                index/'build_manifest.json':run['input_binding']['index_build_manifest_sha256']}
    for name in ('child_chunks.jsonl', 'parent_chunks.jsonl'):
        expected[index/name] = run['input_binding']['index_artifact_sha256'][name]
    tokenizer = ROOT/'memPed/knowledge/models/bge-m3/tokenizer.json'
    expected[tokenizer] = run['method_config']['R2']['actual_asset_sha256']['tokenizer.json']
    expected[old/'method-R4-manifest.json'] = run['output_sha256']['method-R4-manifest.json']
    for path, sha in expected.items():
        if file_sha(path) != sha:
            raise ValueError('input hash drift: ' + str(path))
    types = read_json(type_path)
    if types['gold_sha256'] != revision['revised_gold_sha256']:
        raise ValueError('type-only Gold binding mismatch')
    type_records = types['intents']
    select_intents(type_records, 80)
    queries = validate_queries(read_jsonl(old/'queries.jsonl'))
    if {r['intent_id'] for r in queries} != {r['intent_id'] for r in type_records}:
        raise ValueError('query/type identity mismatch')
    children = read_jsonl(index/'child_chunks.jsonl')
    parents = read_jsonl(index/'parent_chunks.jsonl')
    for records in (children, parents):
        if len({x['chunk_id'] for x in records}) != len(records):
            raise ValueError('duplicate frozen chunk ID')
        for x in records:
            validate_body(x)
    by_child = {c['chunk_id']:c for c in children}
    rankings = [r for r in read_jsonl(old/'rankings.jsonl') if r['method']=='R4' and r['pass_number']==1]
    if len(rankings) != 80 or len({r['intent_id'] for r in rankings}) != 80:
        raise ValueError('R4 ranking count/identity mismatch')
    query_map = {r['intent_id']:r['query'] for r in queries}
    for r in rankings:
        if r['query'] != query_map[r['intent_id']] or r['status'] != 'success':
            raise ValueError('ranking query/status drift')
        for hit in r['results'][:10]:
            frozen = by_child.get(hit['chunk_id'])
            if frozen is None:
                raise ValueError('ranking child missing')
            for key, value in frozen.items():
                if hit.get(key) != value:
                    raise ValueError('ranking frozen child metadata/body drift: ' + key)
    # Preserve a complete byte inventory of the old development, r02 and eval200 outputs.
    old_files = [p for folder in [old,revised,ROOT/'outputs/pearl-retrieval-eval200-20261003-01']
                 for p in folder.rglob('*') if p.is_file()]
    old_hashes = {str(p.relative_to(ROOT)):file_sha(p) for p in sorted(old_files)}
    input_files = list(expected) + [revision_path, delivery_path, Path(type_path)]
    input_hashes = {str(p.relative_to(ROOT)):file_sha(p) for p in input_files}
    manifest = dict(schema_version='pearl-evidence-input-v1', fixed_method='R4', pass_number=1,
                    top_k=10, seed=20261004, input_sha256=input_hashes, old_assets_sha256=old_hashes,
                    gold_path=str(gold_path.relative_to(ROOT)), gold_sha256=revision['revised_gold_sha256'],
                    gold_read_boundary='bytes hashed only; Gold not deserialized by assembler',
                    tokenizer_path=str(tokenizer.relative_to(ROOT)), tokenizer_sha256=expected[tokenizer],
                    tokenizer_fingerprint='hf-tokenizer:'+expected[tokenizer],
                    tokenizers_version=importlib.metadata.version('tokenizers'),
                    query_count=len(queries), child_count=len(children), parent_count=len(parents),
                    protocol_sha256=file_sha(Path(__file__).with_name('protocol.md')))
    return manifest, rankings, {p['chunk_id']:p for p in parents}, type_records, tokenizer


def run_stage(output, count, type_path):
    output = Path(output)
    if output.exists():
        raise FileExistsError('stage output already exists: '+str(output))
    manifest, rankings, parents, types, tokenizer = prepare_inputs(type_path)
    selected = select_intents(types, count)
    output.mkdir(parents=True, exist_ok=False)
    write_json(output/'selection.json', dict(seed=20261004, count=count, intent_ids=selected,
               query_types_sha256=file_sha(type_path)))
    write_json(output/'input-manifest.json', manifest)
    counter = load_counter(tokenizer, manifest['tokenizer_sha256'])
    type_map = {r['intent_id']:r['main_stratum'] for r in types}
    rank_map = {r['intent_id']:r for r in rankings}
    records = []
    for intent in selected:
        r = rank_map[intent]
        for strategy in ('C0','C1'):
            for budget in (4096,8192):
                result = assemble(intent, r['query'], r['results'][:10], parents, counter, strategy, budget)
                result['question_type'] = type_map[intent]
                records.append(result)
    write_jsonl(output/'contexts.jsonl', records)
    saved_count = verify_saved(output/'contexts.jsonl', counter)
    unchanged = all(file_sha(ROOT/path)==sha for path,sha in manifest['old_assets_sha256'].items())
    if not unchanged:
        raise ValueError('old asset preservation failed')
    reasons = {}
    for r in records:
        if r['strategy']=='C1' and r['budget']==4096:
            for trace in r['expansion_trace']:
                reasons[trace['reason']] = reasons.get(trace['reason'],0)+1
    verification = dict(context_count=saved_count, intent_count=count, budgets_and_hashes_verified=True,
                        old_asset_count=len(manifest['old_assets_sha256']), old_assets_unchanged=unchanged,
                        parent_replacement_reasons_unique_intent_children=reasons,
                        truncated_contexts=sum(bool(r['truncation_trace']) for r in records))
    write_json(output/'assembly-verification.json', verification)
    write_json(output/'assembly-manifest.json', dict(status='assembly_complete', **verification,
               input_manifest_sha256=file_sha(output/'input-manifest.json'),
               protocol_sha256=manifest['protocol_sha256'], code_sha256=file_sha(__file__),
               output_sha256={p.name:file_sha(p) for p in output.iterdir() if p.is_file()}))
    return verification


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--count', type=int, choices=[20,80], required=True)
    parser.add_argument('--query-types', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_stage(args.output,args.count,args.query_types),ensure_ascii=False))
