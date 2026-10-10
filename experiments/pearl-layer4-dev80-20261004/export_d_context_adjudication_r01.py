"""Construct task-isolated third-review packets from explicit review selections.

No semantic reconciliation is performed. Cell identities and origin paths stay
in the evaluation-side manifest, outside the reviewer packet directory.
"""
import argparse
import copy
from pathlib import Path
from assemble_c100_r01 import ROOT, read, sha, write

GROUND_KEYS = ('claims', 'citation_pairs', 'extraction_unknown',
               'citation_extraction_unknown', 'excluded_candidates', 'completeness_review')
BEHAVIOR_KEYS = ('behavior', 'abstain', 'abstains_from_unsupported_completion',
                 'unsupported_completion', 'reason', 'behavior_explanation')


def validate_review_input(review, packet):
    provenance = review.get('provenance', {})
    origin = None
    for field in ('response_sha256', 'context_sha256'):
        digest = review.get(field, provenance.get(field))
        if digest is None and provenance.get('packet_path'):
            if origin is None:
                path = provenance['packet_path']
                if sha(path) != provenance.get('packet_sha256'):
                    raise ValueError('review packet SHA mismatch')
                origin = read(path)
            digest = origin.get(field)
        if field in packet and digest != packet[field]:
            raise ValueError('review input mismatch')


def export(selection, task, directory, manifest):
    if task not in ('grounding', 'behavior'):
        raise ValueError('task whitelist')
    directory, manifest = Path(directory), Path(manifest)
    if manifest.exists():
        raise FileExistsError(manifest)
    maps = {x['cell_id']: x['blind_id'] for x in read(ROOT / 'packets' / f'{task}-D60-r02-identity-map.json')}
    keys = GROUND_KEYS if task == 'grounding' else BEHAVIOR_KEYS
    prepared, seen = [], set()
    for row in selection['rows']:
        cell = row['cell_id']
        if cell in seen:
            raise ValueError('duplicate cell')
        seen.add(cell)
        ident = maps[cell]
        original = ROOT / 'packets' / f'{task}-D60-r02' / (ident + '.json')
        packet = copy.deepcopy(read(original))
        primary, secondary = read(row['primary_path']), read(row['secondary_path'])
        validate_review_input(primary, packet)
        validate_review_input(secondary, packet)
        packet['review_A'] = {k: primary[k] for k in keys if k in primary}
        packet['review_B'] = {k: secondary[k] for k in keys if k in secondary}
        packet['adjudication_instruction'] = 'Actually inspect all raw answer assertions, conditions, occurrences and relevant actual Source/page windows. Reconcile extraction, labels and citation pairs independently; preserve real unknown. No sourcefacts, arm identity, previous scores or frozen answerability labels are supplied.'
        path = directory / (ident + '.json')
        if path.exists():
            raise FileExistsError(path)
        prepared.append((path, packet, row, original))
    records = []
    for path, packet, row, original in prepared:
        write(path, packet)
        records.append({'cell_id': row['cell_id'], 'blind_id': packet['blind_id'],
                        'packet_path': str(path), 'packet_sha256': sha(path),
                        'original_white_packet_path': str(original),
                        'original_white_packet_sha256': sha(original),
                        'primary_path': row['primary_path'], 'primary_sha256': sha(row['primary_path']),
                        'secondary_path': row['secondary_path'], 'secondary_sha256': sha(row['secondary_path'])})
    write(manifest, {'task': task, 'status': 'packets_only_not_adjudicated',
                     'semantic_labels_generated': False, 'rows': records})
    return {'packet_n': len(records), 'task': task, 'semantic_labels_generated': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('selection', type=Path)
    parser.add_argument('task', choices=['grounding', 'behavior'])
    parser.add_argument('directory', type=Path)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    print(export(read(args.selection), args.task, args.directory, args.manifest))
