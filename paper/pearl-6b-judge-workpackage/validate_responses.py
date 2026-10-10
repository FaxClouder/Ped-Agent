"""Structural check of judge responses (standard library only).

Usage: python validate_responses.py calibration-r02
       python validate_responses.py research-primary-1/grounding   (one task directory of a research period)
       python validate_responses.py research-primary-1             (every task directory of the period)

Checks that every packet in <dir>/manifest.json has responses/<job_id>.json containing exactly one JSON
object with the required keys and the packet's identity value. For grounding it also checks mechanically
that every text / other_occurrence_texts / citation_text is a verbatim substring of raw_answer and every
context_evidence quote a verbatim substring of context. For factuality it checks that every packet claim_id is
labelled exactly once with true / false / unknown. It does NOT check whether labels are right.
"""
import json
import sys
from pathlib import Path

NEED = {'layer3': ['packet_id', 'decision', 'unknown_reasons', 'rationale'],
        'answerability': ['anchor_id', 'answerability', 'reason'],
        'grounding': ['anchor_id', 'claims', 'citation_pairs', 'extraction_unknown', 'citation_extraction_unknown', 'reason'],
        'factuality': ['anchor_id', 'claims'],
        'behavior': ['anchor_id', 'behavior', 'abstains_from_unsupported_completion', 'unsupported_completion', 'refusal_reason', 'reason']}
ENUM = {'answerability': {'complete', 'partial', 'none', 'unknown'},
        'behavior': {'full_answer', 'bounded_partial', 'pure_abstain', 'ambiguous'}}
FACT_LABELS = {'true', 'false', 'unknown'}


def verbatim(obj, packet):
    p = json.loads(packet['user_message'].split('\n', 1)[1])
    for c in obj['claims'] or []:
        for t in [c.get('text')] + list(c.get('other_occurrence_texts') or []):
            if not t or t not in p['raw_answer']:
                return f"claim {c.get('claim_id')}: text not verbatim in raw_answer: {str(t)[:60]!r}"
        for e in c.get('context_evidence') or []:
            if e.get('quote') and e['quote'] not in p['context']:
                return f"claim {c.get('claim_id')}: quote not verbatim in context: {e['quote'][:60]!r}"
    for q in obj['citation_pairs'] or []:
        if not q.get('citation_text') or q['citation_text'] not in p['raw_answer']:
            return f"citation of {q.get('claim_id')}: citation_text not verbatim in raw_answer"
    return None


def factuality_claims(obj, packet):
    p = json.loads(packet['user_message'].split('\n', 1)[1])
    if not isinstance(obj['claims'], list) or not all(isinstance(c, dict) for c in obj['claims']):
        return 'claims must be a list of objects'
    got = [c.get('claim_id') for c in obj['claims']]
    want = [c['claim_id'] for c in p['claims']]
    if sorted(map(str, got)) != sorted(want):
        return f'claim_id set {got} differs from the packet claims {want} (label every claim exactly once)'
    bad = [c.get('claim_id') for c in obj['claims'] if c.get('label') not in FACT_LABELS]
    if bad:
        return f'label of {bad} must be one of {sorted(FACT_LABELS)}'
    return None


def main(phase):
    root = Path(__file__).resolve().parent / phase
    man = json.loads((root / 'manifest.json').read_text(encoding='utf8'))
    if 'index' not in man:  # research period root: validate each task directory
        return max(main(f"{phase}/{v['dir']}") for v in man['tasks'].values())
    problems, ok = [], 0
    for i in man['index']:
        job = i['job_id']; task = i['task']
        packet = json.loads((root / i['packet_file']).read_text(encoding='utf8'))
        r = root / 'responses' / f'{job}.json'
        if not r.exists():
            problems.append((job, 'missing response file')); continue
        try:
            obj = json.loads(r.read_text(encoding='utf8'))
        except Exception as e:
            problems.append((job, f'invalid JSON: {e}')); continue
        if not isinstance(obj, dict):
            problems.append((job, 'response is not a JSON object')); continue
        miss = [k for k in NEED[task] if k not in obj]
        if miss:
            problems.append((job, f'missing keys {miss}')); continue
        if obj.get(packet['identity_field']) != packet['identity_value']:
            problems.append((job, f"{packet['identity_field']} must be {packet['identity_value']!r}")); continue
        if task == 'layer3' and not all(isinstance(obj['decision'].get(k), dict) for k in ('targets', 'conditions', 'claims')):
            problems.append((job, 'decision.targets / conditions / claims must be objects')); continue
        if task in ENUM and obj[NEED[task][1]] not in ENUM[task]:
            problems.append((job, f'{NEED[task][1]} must be one of {sorted(ENUM[task])}')); continue
        if task == 'factuality':
            v = factuality_claims(obj, packet)
            if v:
                problems.append((job, v)); continue
        if task == 'grounding':
            v = verbatim(obj, packet)
            if v:
                problems.append((job, v)); continue
        ok += 1
    print(json.dumps({'phase': phase, 'packets': len(man['index']), 'valid': ok, 'problems': len(problems), 'first_problems': problems[:20]}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'calibration'))
