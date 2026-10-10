"""Export semantic review packets separately from experimental identity."""
import hashlib
import json
from pathlib import Path


FORBIDDEN = {'arm', 'model', 'returned_model', 'l2_sufficient', 'rank', 'score', 'method', 'configuration', 'context', 'oracle', 'serialized_context', 'segments', 'construction_status', 'source_library_path', 'source_library_sha256', 'selected_candidate_sha256', 'selected_review_sha256', 'reference_packet_sha256', 'uncertainty_mechanism'}

SEMANTIC_REFERENCE_FIELDS = {'reference_answer', 'resolved', 'unresolved_reason', 'key_targets', 'target_definitions', 'required_conditions', 'condition_definitions', 'allowed_claim_groups', 'claim_definitions', 'integration_applicable', 'integration_rule', 'numeric_targets', 'citations', 'quality', 'disputes'}


def _clean_reference(value):
    if isinstance(value, dict):
        return {key: _clean_reference(item) for key, item in value.items()
                if key not in FORBIDDEN and key not in {'intent_id', 'stratum', 'oracle_eligible', 'provenance', 'review_provenance'}}
    if isinstance(value, list):
        return [_clean_reference(item) for item in value]
    return value


def export_blind(records, references, rubric):
    packets, mapping = [], {}
    cells = set()
    for index, record in enumerate(records):
        identity = record['cell_id']
        if identity in cells:
            raise ValueError('duplicate generation cell')
        cells.add(identity)
        intent = record['intent_id']
        if intent not in references:
            raise ValueError('missing frozen reference')
        if record.get('generation_status', 'returned') != 'returned':
            # Runtime failures are scored separately; no fabricated semantic answer.
            continue
        packet_id = f'answer-{index + 1:06d}'
        packets.append({'packet_id': packet_id, 'query': record['query'], 'answer': record['raw_answer'],
                        'reference': _clean_reference({key:value for key,value in references[intent].items() if key in SEMANTIC_REFERENCE_FIELDS}), 'rubric': _clean_reference(rubric)})
        mapping[packet_id] = {key: value for key, value in record.items() if key not in {'query', 'raw_answer', 'request'}}
    return packets, mapping


def save_blind(packets, mapping, output_dir):
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=False)
    for filename, data in [('blind-packets.json', packets), ('private-mapping.json', mapping)]:
        with (directory / filename).open('x', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, sort_keys=True, indent=2)


def import_decisions(packets, decisions, mapping, selected_version):
    """Select actual independently recorded judgments; never synthesize labels."""
    expected = {packet['packet_id'] for packet in packets}
    selected = [row for row in decisions if row.get('version') == selected_version]
    ids = [row['packet_id'] for row in selected]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('selected review version missing/duplicate packet')
    result = []
    for row in selected:
        if not row.get('reviewer_id') or not row.get('rationale') or row.get('actual_read') is not True:
            raise ValueError('actual review provenance and rationale required')
        result.append({**mapping[row['packet_id']], 'decision': row['decision'],
                       'review_provenance': {key: row[key] for key in ('version', 'reviewer_id', 'rationale', 'actual_read')}})
    return result
