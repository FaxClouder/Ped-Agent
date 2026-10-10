"""Structural check of citation redo r03 responses (standard library only).

Usage: python validate_citation_responses.py calibration-citation-r03
       python validate_citation_responses.py research-citation-r03

Checks that every packet in <dir>/manifest.json has responses/<job_id>.json containing exactly one JSON object with
anchor_id (the packet's identity value), citation_pairs (a list), citation_extraction_unknown (true/false) and reason,
and no claims. For every pair: claim_id is one of the packet's fixed claims; citation_text is a verbatim substring of
raw_answer and citation_occurrence (1-based) does not exceed its number of occurrences; source_id is a non-empty
string and, when written as a fragment_id (B<n>-F<k>), exists in source_fragments; label is one of the seven labels;
reason is present. It does NOT check whether labels are right.
"""
import json
import re
import sys
from pathlib import Path

NEED = ['anchor_id', 'citation_pairs', 'citation_extraction_unknown', 'reason']
PAIR = ['claim_id', 'citation_text', 'citation_occurrence', 'source_id', 'label', 'reason']
LABELS = {'supported', 'partial', 'unsupported', 'contradicted', 'unknown', 'invalid', 'outside-context'}
FRAGMENT = re.compile(r'B\d+-F\d+')


def count(haystack, needle):
    n, i = 0, haystack.find(needle)
    while i >= 0:
        n += 1
        i = haystack.find(needle, i + len(needle))
    return n


def check(obj, packet):
    p = json.loads(packet['user_message'].split('\n', 1)[1])
    if not isinstance(obj, dict):
        return 'response is not a JSON object'
    miss = [k for k in NEED if k not in obj]
    if miss:
        return f'missing keys {miss}'
    if 'claims' in obj:
        return 'claims must not be output (claims are fixed in the packet)'
    if obj['anchor_id'] != packet['identity_value']:
        return f"anchor_id must be {packet['identity_value']!r}"
    if not isinstance(obj['citation_extraction_unknown'], bool):
        return 'citation_extraction_unknown must be true or false'
    if not isinstance(obj['citation_pairs'], list):
        return 'citation_pairs must be a list'
    claims = {c['claim_id'] for c in p['claims']}
    fragments = {f['fragment_id'] for b in p['source_fragments'] for f in b['fragments']}
    for n, q in enumerate(obj['citation_pairs'], 1):
        if not isinstance(q, dict):
            return f'pair {n} is not an object'
        miss = [k for k in PAIR if k not in q]
        if miss:
            return f'pair {n}: missing keys {miss}'
        if q['claim_id'] not in claims:
            return f"pair {n}: claim_id {q['claim_id']!r} is not one of the packet claims {sorted(claims)}"
        t = q['citation_text']
        if not isinstance(t, str) or not t or t not in p['raw_answer']:
            return f'pair {n}: citation_text not verbatim in raw_answer'
        k = q['citation_occurrence']
        if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= count(p['raw_answer'], t):
            return f'pair {n}: citation_occurrence {k!r} must be 1..{count(p["raw_answer"], t)}'
        s = q['source_id']
        if not isinstance(s, str) or not s:
            return f'pair {n}: source_id must be a non-empty string'
        if FRAGMENT.fullmatch(s) and s not in fragments:
            return f'pair {n}: source_id {s!r} is not a fragment_id of this packet'
        if q['label'] not in LABELS:
            return f'pair {n}: label must be one of {sorted(LABELS)}'
    return None


def main(phase):
    root = Path(__file__).resolve().parent / phase
    man = json.loads((root / 'manifest.json').read_text(encoding='utf8'))
    problems, ok = [], 0
    for i in man['index']:
        job = i['job_id']
        packet = json.loads((root / i['packet_file']).read_text(encoding='utf8'))
        r = root / 'responses' / f'{job}.json'
        if not r.exists():
            problems.append((job, 'missing response file')); continue
        try:
            obj = json.loads(r.read_text(encoding='utf8'))
        except Exception as e:
            problems.append((job, f'invalid JSON: {e}')); continue
        v = check(obj, packet)
        if v:
            problems.append((job, v)); continue
        ok += 1
    print(json.dumps({'phase': phase, 'packets': len(man['index']), 'valid': ok, 'problems': len(problems), 'first_problems': problems[:20]}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'calibration-citation-r03'))
