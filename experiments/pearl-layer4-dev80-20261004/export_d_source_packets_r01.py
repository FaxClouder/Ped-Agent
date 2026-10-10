"""Export explicitly selected D atoms to source-only packets; assigns no labels.

Selection: rows [{cell_id, blind_id, grounding_path}], where blind_id is the
source-review identity chosen on the evaluation side. Each batch is exclusive.
"""
import argparse
from pathlib import Path
from assemble_c100_r01 import ROOT, atom, canonical, read, sha, write


def export(selection, directory, manifest):
    directory, manifest = Path(directory), Path(manifest)
    facts = {x['intent_id']: x for x in read(ROOT / 'facts/facts-r03.json')['items']}
    inputs = {x['cell_id']: x for x in read(ROOT / 'inputs-r01.json')['cells']}
    ids, cells, prepared = set(), set(), []
    for row in selection['rows']:
        ident, cell = row['blind_id'], row['cell_id']
        if ident in ids or cell in cells or not ident.startswith('factuality-'):
            raise ValueError('duplicate or invalid identity')
        ids.add(ident); cells.add(cell)
        inp, ground = inputs[cell], read(row['grounding_path'])
        response_sha = ground.get('response_sha256', ground.get('provenance', {}).get('response_sha256'))
        context_sha = ground.get('context_sha256', ground.get('provenance', {}).get('context_sha256'))
        if response_sha != inp['response_sha256'] or context_sha != inp['context_sha256']:
            raise ValueError('selected grounding input mismatch')
        if len({c['claim_id'] for c in ground['claims']}) != len(ground['claims']):
            raise ValueError('duplicate claim identity')
        fact = facts[inp['intent_id']]
        packet = {'blind_id': ident, 'claims': [atom(c) for c in ground['claims']],
                  'response_sha256': response_sha,
                  'facts': {'sources': fact['evidence'],
                            'supplementary_facts': fact.get('supplementary_facts', [])},
                  'rubric': 'true / false / unknown; source-only review of every atom and all conditions'}
        path = directory / (ident + '.json')
        if path.exists():
            raise FileExistsError(path)
        prepared.append((path, packet, row))
    if manifest.exists():
        raise FileExistsError(manifest)
    bindings = []
    for path, packet, row in prepared:
        write(path, packet)
        bindings.append({'cell_id': row['cell_id'], 'blind_id': row['blind_id'],
                         'packet_path': str(path), 'packet_sha256': sha(path),
                         'grounding_path': row['grounding_path'],
                         'grounding_sha256': sha(row['grounding_path']),
                         'canonical_atoms': canonical(packet['claims'])})
    write(manifest, {'status': 'packets_only_not_reviewed', 'labels_generated': False,
                     'source_facts_sha256': sha(ROOT / 'facts/facts-r03.json'), 'rows': bindings})
    return {'packet_n': len(bindings), 'labels_generated': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('selection', type=Path)
    parser.add_argument('directory', type=Path)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    print(export(read(args.selection), args.directory, args.manifest))
