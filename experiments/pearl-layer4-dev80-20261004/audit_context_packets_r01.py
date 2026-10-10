"""Mechanical-only audit of an explicit grounding selection, never assigns semantics."""
import argparse
import copy
from pathlib import Path
from assemble_c100_r01 import ROOT, read, sha, write
from verify import validate_review


def audit(selection, output):
    cells = {x['cell_id']: x for x in read(ROOT / 'inputs-r01.json')['cells']}
    results, errors = [], []
    for row in selection['rows']:
        path = row['grounding_path']
        d = read(path)
        try:
            inp = cells[row['cell_id']]
            provenance = d['provenance']
            packet_path = provenance['packet_path']
            if sha(packet_path) != provenance['packet_sha256']:
                raise ValueError('original packet SHA mismatch')
            packet = read(packet_path)
            for key in ('query', 'raw_answer', 'context', 'response_sha256', 'context_sha256'):
                if packet[key] != inp[key]:
                    raise ValueError('packet and original input mismatch: ' + key)
            shadow = copy.deepcopy(d)
            # Source-only truth is unavailable in this check. The independent
            # verifier requires a factuality field; ephemeral unknown avoids
            # checking a task not yet performed and is never saved as a decision.
            for claim in shadow['claims']:
                claim['factuality'] = {'label': 'unknown', 'source_evidence': []}
            validate_review(shadow, inp)
            results.append({'path': path, 'sha256': sha(path),
                            'claim_n': len(d['claims']), 'pair_n': len(d['citation_pairs'])})
        except Exception as exc:
            errors.append({'path': path, 'error': str(exc)})
    result = {'status': 'mechanical_context_audit_only', 'semantic_review_performed': False,
              'source_factuality_checked': False, 'selected_n': len(selection['rows']),
              'mechanically_valid_n': len(results), 'errors': errors, 'records': results}
    write(output, result)
    return {'selected_n': len(selection['rows']), 'mechanically_valid_n': len(results), 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('selection', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(audit(read(args.selection), args.output))
