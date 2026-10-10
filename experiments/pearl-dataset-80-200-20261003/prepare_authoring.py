"""Verify the frozen Adobe corpus and prepare source-disjoint annotation packets."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCES = ROOT / 'outputs/pearl-index-106-adobe-20260929-01/sources.jsonl'
CORPUS = ROOT / 'paper/pearl-framework/datasets/retrieval-corpus/corpus-manifest-v02.jsonl'
PILOT = ROOT / 'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json'
PILOT_SOURCE_INDICES = (17, 34, 41, 48, 57, 71, 83)
DEV_ADDITIONAL_INDICES = (0, 3, 8, 11, 18, 23, 25, 27, 28, 30, 31, 33, 36, 38, 44, 45, 49, 50, 53, 54, 60, 68, 70, 76, 105)
SEED = 20260929

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path: Path, value: dict) -> None:
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')

def assign_sources(rows: list[dict], pilot_sources: set[str]) -> dict[str, list[dict]]:
    if len(rows) != 106:
        raise ValueError('expected frozen 106-source inventory')
    dev_indices = set(PILOT_SOURCE_INDICES) | set(DEV_ADDITIONAL_INDICES)
    dev = [row for i, row in enumerate(rows) if i in dev_indices]
    if not pilot_sources <= {row['source_id'] for row in dev}:
        raise ValueError('pilot source identity/order changed')
    rest = [row for i, row in enumerate(rows) if i not in dev_indices]
    random.Random(SEED).shuffle(rest)
    return {'dev': dev, 'eval_a': rest[:37], 'eval_b': rest[37:]}

def run(output: Path) -> None:
    if output.exists():
        raise FileExistsError(f'refusing to overwrite {output}')
    rows = [json.loads(line) for line in SOURCES.read_text(encoding='utf-8').splitlines()]
    pilot = json.loads(PILOT.read_text(encoding='utf-8'))
    if pilot['corpus_manifest_sha256'] != sha(CORPUS):
        raise ValueError('frozen corpus binding changed')
    for row in rows:
        if sha(ROOT / row['source_path']) != row['sha256'] or sha(ROOT / row['document_path']) != row['document_sha256']:
            raise ValueError(f'source or Adobe document changed: {row["source_id"]}')
        document = json.loads((ROOT / row['document_path']).read_text(encoding='utf-8'))
        if document['parser_version'] != 'adobe-pdf-extract-v1' or document['source_hash'] != row['sha256']:
            raise ValueError('Adobe parser/source identity changed')
    assignment = assign_sources(rows, {atom['source_id'] for q in pilot['intents'] for atom in q['atoms']})
    output.mkdir(parents=True, exist_ok=False)
    for name, members in assignment.items():
        directory = output / name
        directory.mkdir()
        write(directory / 'sources.json', {'role': name, 'sources': members})
        for row in members:
            document = json.loads((ROOT / row['document_path']).read_text(encoding='utf-8'))
            page_text = defaultdict(list)
            for element in sorted(document['elements'], key=lambda item: item['order']):
                if element['text']:
                    page_text[element['page_number']].append(element['text'])
            with (directory / f'{row["source_id"]}.txt').open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(f'SOURCE_ID: {row["source_id"]}\nTITLE: {row["title_metadata"]}\nPDF: {row["source_path"]}\nSHA256: {row["sha256"]}\nADOBE_DOCUMENT: {row["document_path"]}\n')
                for page in range(1, row['page_count'] + 1):
                    stream.write(f'\n=== PDF PAGE {page} ===\n' + '\n'.join(page_text[page]) + '\n')
    write(output / 'source-allocation.json', {
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'seed': SEED,
        'source_count': 106, 'corpus_manifest_sha256': sha(CORPUS),
        'sources_snapshot_sha256': sha(SOURCES), 'pilot_gold_sha256': sha(PILOT),
        'preparation_code_sha256': sha(Path(__file__)), 'authoring_spec_sha256': sha(HERE / 'authoring-spec.md'),
        'all_source_pdf_and_adobe_hashes_verified': True,
        'groups': {name: [row['source_id'] for row in members] for name, members in assignment.items()},
        'packet_sha256': {path.relative_to(output).as_posix(): sha(path) for path in sorted(output.rglob('*')) if path.is_file()},
        'stratum_quotas': {'dev': {key: 18 for key in ('single_source', 'numeric_table', 'within_paper_multi', 'cross_paper')},
                          'eval_a': {key: 25 for key in ('single_source', 'numeric_table', 'within_paper_multi', 'cross_paper')},
                          'eval_b': {key: 25 for key in ('single_source', 'numeric_table', 'within_paper_multi', 'cross_paper')}},
        'source_partition_interpretation': 'All 106 documents remain in the retrieval corpus; question authoring source groups are disjoint to reduce study-fact family leakage.',
    })
    print(json.dumps({'output': str(output), 'groups': {key: len(value) for key, value in assignment.items()}, 'source_hashes_verified': 106}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    run(parser.parse_args().output_dir.resolve())
