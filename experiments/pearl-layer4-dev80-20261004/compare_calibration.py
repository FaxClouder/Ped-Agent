"""Independent synthetic calibration comparison; never opens real evaluation data.

Usage: python compare_calibration.py --results DIR --output NEW_REPORT.json
DIR contains {grounding,factuality,answerability,behavior}/cal-01.json etc.
"""
import argparse
import json
from pathlib import Path

TASKS = ('grounding', 'factuality', 'answerability', 'behavior')


def compare(expected, results):
    counters = {k: {'correct': 0, 'denominator': 0} for k in
                ('extraction', 'grounding', 'factuality', 'citation',
                 'answerability', 'behavior', 'refusal_reason')}
    failures, sentinels = [], []

    def record(metric, passed, anchor):
        counters[metric]['denominator'] += 1
        counters[metric]['correct'] += int(passed)
        if not passed:
            failures.append({'anchor_id': anchor, 'metric': metric})

    for exp in expected:
        ident = exp['anchor_id']
        before = len(failures)
        packets = results.get(ident, {})
        for task in TASKS:
            if task not in packets or packets[task].get('anchor_id') != ident:
                failures.append({'anchor_id': ident, 'metric': 'schema', 'task': task})
        gr = packets.get('grounding', {})
        fc = packets.get('factuality', {})
        actual_claims = gr.get('claims', [])
        expected_claims = exp['claims']
        # Text plus all occurrence spans checks completeness and duplicate handling.
        wanted = {(x['text'], tuple(map(tuple, x['occurrences']))) for x in expected_claims}
        try:
            actual = {(x['text'], tuple(map(tuple, x['occurrences']))) for x in actual_claims}
        except (KeyError, TypeError):
            actual = None
        record('extraction', actual == wanted and len(actual_claims) == len(expected_claims)
               and gr.get('extraction_unknown') is False, ident)
        grounded = {x.get('claim_id'): x for x in actual_claims}
        factual = {x.get('claim_id'): x for x in fc.get('claims', [])}
        for x in expected_claims:
            if x['grounding'] != 'unknown':
                record('grounding', grounded.get(x['claim_id'], {}).get('label') == x['grounding'], ident)
            if x['factuality'] != 'unknown':
                record('factuality', factual.get(x['claim_id'], {}).get('label') == x['factuality'], ident)
        actual_pairs = gr.get('citation_pairs', [])
        expected_pairs = exp['citation_pairs']
        def key(p):
            return (p.get('claim_id'), p.get('citation_text'), tuple(p.get('citation_span', [])))
        paired = {key(p): p for p in actual_pairs}
        # Pair count/set equality prevents deleting invalid or inventing supported pairs.
        if len(actual_pairs) != len(expected_pairs) or set(paired) != {key(p) for p in expected_pairs}:
            failures.append({'anchor_id': ident, 'metric': 'citation_schema'})
        for p in expected_pairs:
            if p['label'] != 'unknown':
                record('citation', paired.get(key(p), {}).get('label') == p['label'], ident)
        record('answerability', packets.get('answerability', {}).get('answerability') == exp['answerability'], ident)
        bh = packets.get('behavior', {})
        record('behavior', all(bh.get(k) == exp[k] for k in
               ('behavior', 'abstains_from_unsupported_completion', 'unsupported_completion')), ident)
        record('refusal_reason', 'refusal_reason' in bh and bh['refusal_reason'] == exp['refusal_reason'], ident)
        if exp.get('sentinel'):
            sentinels.append({'anchor_id': ident, 'kind': exp['sentinel'], 'passed': len(failures) == before})
    for val in counters.values():
        val['agreement'] = val['correct'] / val['denominator'] if val['denominator'] else None
        val['passed'] = val['agreement'] is not None and val['agreement'] >= .95
    return {'status': 'passed' if all(v['passed'] for v in counters.values())
            and len(sentinels) == 8 and all(s['passed'] for s in sentinels)
            and not any(f['metric'] in ('schema', 'citation_schema') for f in failures) else 'failed',
            'metrics': counters, 'sentinels': sentinels, 'failures': failures,
            'anchor_count': len(expected), 'notes': 'resolved claim/pair labels exclude expected unknown; answerability includes all four labels; no real data read'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--results', type=Path, required=True)
    p.add_argument('--expected', type=Path, default=Path(__file__).resolve().parents[2] /
                   'outputs/pearl-layer4-dev80-20261004-01/calibration/expected-r01.json')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    expected = json.loads(args.expected.read_text(encoding='utf-8'))['expected']
    results = {}
    for exp in expected:
        results[exp['anchor_id']] = {}
        for task in TASKS:
            path = args.results / task / (exp['anchor_id'] + '.json')
            if path.exists():
                results[exp['anchor_id']][task] = json.loads(path.read_text(encoding='utf-8'))
    report = compare(expected, results)
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({'status': report['status'], 'metrics': report['metrics']}, ensure_ascii=False))
    raise SystemExit(0 if report['status'] == 'passed' else 1)


if __name__ == '__main__':
    main()
