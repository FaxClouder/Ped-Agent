"""Deterministic Layer 3 scoring; semantic labels must come from selected reviews."""
import argparse
import json
import math
from pathlib import Path

import numpy as np

SCHEMA = 'pearl-answer-score-input-v1'
ARMS = ('A0-4096', 'A1-4096', 'A0-8192', 'A1-8192')
PAIRS = [('A1-4096', 'A0-4096'), ('A1-8192', 'A0-8192'),
         ('A0-8192', 'A0-4096'), ('A1-8192', 'A1-4096'), ('Aref-8192', 'A1-8192')]
LABELS = {'correct', 'incorrect', 'missing', 'unknown'}
UNITS = {'m/s': ('speed', 1), 'cm/s': ('speed', .01), 'km/h': ('speed', 1/3.6),
         'people': ('count', 1), 'persons': ('count', 1), '%': ('percentage', 1),
         'fraction': ('percentage', 100), 'percentage_points': ('percentage_points', 1),
         'people/m2': ('density', 1), 'people/s': ('flow', 1), 'people/min': ('flow', 1/60),
         'm': ('length', 1), 'cm': ('length', .01), 's': ('time', 1), 'min': ('time', 60),
         '1/m': ('inverse_length', 1), 'persons/(m*s)': ('specific_flow', 1),
         'degrees': ('angle', 1), 'm/s2': ('acceleration', 1), 'dimensionless': ('dimensionless', 1),
         'years': ('age', 1)}
UNITS.update({
    'degree': ('angle', 1), 'integer': ('dimensionless', 1), 'proportion': ('percentage', 100),
    'pedestrians': ('count', 1), 'ped': ('count', 1),
    'ped/m2': ('density', 1), 'ped/m²': ('density', 1), 'pedestrians/m²': ('density', 1),
    'pedestrians/m2': ('density', 1), 'persons/m²': ('density', 1), 'people/m²': ('density', 1),
    'people/m': ('linear_density', 1), 'ped/m': ('linear_density', 1), 'pedestrians/m': ('linear_density', 1),
    'ped/s': ('flow', 1), 'pedestrians/s': ('flow', 1), 'ped/min': ('flow', 1/60),
    'm2/person': ('area_per_pedestrian', 1), 'm2/ped': ('area_per_pedestrian', 1),
    'm²/person': ('area_per_pedestrian', 1), 'm²/ped': ('area_per_pedestrian', 1),
    'cm²/ped': ('area_per_pedestrian', .0001), 'cm2/person': ('area_per_pedestrian', .0001)
})


def numeric_error(target, answer):
    base = {'id': target['id'], 'dimension': target['dimension'], 'unit': target['unit'],
            'absolute_error': None, 'relative_error': None, 'within_tolerance': None}
    status = answer.get('status', 'missing')
    if status not in {'parsed', 'missing', 'unknown'}:
        raise ValueError('invalid numeric status')
    base['status'] = status
    if status != 'parsed':
        return base
    src, dst = UNITS.get(answer['unit']), UNITS.get(target['unit'])
    canonical_dimension={'proportion':'percentage','relative_time_improvement':'percentage','integer':'dimensionless','count_per_width':'linear_density'}.get(target['dimension'],target['dimension'])
    if src is None or dst is None or src[0] != dst[0] or dst[0] != canonical_dimension:
        base['status'] = 'wrong_unit'
        base['within_tolerance'] = False
        return base
    if not all(math.isfinite(float(x)) for x in (target['value'], answer['value'], target['tolerance'])):
        raise ValueError('nonfinite numeric data')
    if target['tolerance'] < 0:
        raise ValueError('negative scientific tolerance')
    value = answer['value'] * src[1] / dst[1]
    error = abs(value - target['value'])
    if math.isclose(value, target['value'], rel_tol=1e-12, abs_tol=1e-12):
        error = 0.0
    accepted = error <= target['tolerance']
    if 'allowed_values' in target:
        alternatives=target['allowed_values']
        if (not isinstance(alternatives,list) or not alternatives or target['tolerance']!=0 or not target.get('tolerance_basis') or any(not isinstance(x,(float,int)) or isinstance(x,bool) or not math.isfinite(x) for x in alternatives)):
            raise ValueError('invalid exact numeric alternatives')
        accepted=any(math.isclose(value,x,rel_tol=1e-12,abs_tol=1e-12) for x in alternatives)
    base.update(absolute_error=error,
                relative_error=error / abs(target['value']) if target['value'] else None,
                within_tolerance=accepted)
    return base


def score_cell(reference, cell):
    failed = cell['generation_status'] == 'generation_failed'
    if cell['generation_status'] not in {'returned', 'generation_failed'}:
        raise ValueError('invalid generation status')
    d = {} if failed else cell.get('decision', {})
    def labels(field, ids):
        values = [d.get(field, {}).get(i, 'missing') for i in ids]
        if any(v not in LABELS for v in values):
            raise ValueError('invalid semantic label')
        return values
    groups = reference['allowed_claim_groups']
    if not groups or any(not g or len(g) != len(set(g)) for g in groups):
        raise ValueError('invalid allowed groups')
    lower = max(sum(v == 'correct' for v in labels('claims', g)) / len(g) for g in groups)
    upper = max(sum(v in {'correct', 'unknown'} for v in labels('claims', g)) / len(g) for g in groups)
    targets = labels('targets', reference['key_targets'])
    conditions = labels('conditions', reference['required_conditions'])
    if not targets:
        raise ValueError('key targets required')
    integration = d.get('integration', 'unknown') if reference['integration_applicable'] else 'na'
    if integration not in {'yes', 'no', 'unknown', 'na'}:
        raise ValueError('invalid integration')
    contradiction = d.get('contradiction', 'unknown')
    if contradiction not in (True, False, 'unknown'):
        raise ValueError('invalid contradiction')
    numeric = [numeric_error(t, d.get('numeric', {}).get(t['id'], {})) for t in reference['numeric_targets']]
    refusal = d.get('refusal', False)
    if not isinstance(refusal, bool):
        raise ValueError('invalid refusal')
    failure_kind = 'generation_failed' if failed else 'refusal' if refusal else None
    if not reference['resolved']:
        ac = None
    elif failed or refusal or contradiction is True or 'incorrect' in targets or any(n['within_tolerance'] is False for n in numeric):
        ac = 0
    elif contradiction == 'unknown' or 'unknown' in targets + conditions or integration == 'unknown' or any(n['status'] == 'unknown' for n in numeric):
        ac = None
    elif all(v == 'correct' for v in targets + conditions) and integration in {'yes', 'na'} and all(n['within_tolerance'] is True for n in numeric):
        ac = 1
    elif 'correct' in targets:
        ac = .5
    else:
        ac = 0
    if failed:
        lower = upper = 0.0
        integration = 'no' if reference['integration_applicable'] else 'na'
    strict = 'unknown' if ac is None else 'yes' if ac == 1 else 'no'
    l2 = cell['l2_sufficient']
    if l2 not in {'yes', 'no', 'unknown'}:
        raise ValueError('invalid L2')
    state = 'unknown' if l2 == 'unknown' or strict == 'unknown' else 'n' + str(int(l2 == 'yes')) + str(int(strict == 'yes'))
    return dict(intent_id=cell['intent_id'], arm=cell['arm'], stratum=reference['stratum'],
                reference_resolved=reference['resolved'], response_returned=not failed,
                ac=ac, strict=strict, coverage_lower=lower, coverage_upper=upper,
                complete_claim_group=lower == 1, integration=integration, numeric=numeric,
                failure_kind=failure_kind, four_state=state)


def exact_mcnemar(gains, losses):
    n = gains + losses
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(gains, losses) + 1)) / 2**n) if n else 1.0


def holm(values):
    adjusted = [0.0] * len(values); previous = 0
    for rank, index in enumerate(sorted(range(len(values)), key=lambda i: values[i])):
        previous = max(previous, min(1, (len(values) - rank) * values[index]))
        adjusted[index] = previous
    return adjusted


def summarize(rows):
    n = len(rows)
    def bounds(field):
        return [sum(0 if r[field] is None else r[field] for r in rows) / n,
                sum(1 if r[field] is None else r[field] for r in rows) / n] if n else [None, None]
    states = {key: sum(r['four_state'] == key for r in rows) for key in ('n11', 'n10', 'n01', 'n00', 'unknown')}
    denominator = states['n11'] + states['n10']
    states.update(sufficient_N=denominator,
                  new_failure_rate=states['n10'] / denominator if denominator else None,
                  sufficient_strict_success=states['n11'] / denominator if denominator else None,
                  generation_failed=sum(r['failure_kind'] == 'generation_failed' for r in rows),
                  sufficient_technical_failures=sum(r['failure_kind'] == 'generation_failed' and r['four_state'] == 'n10' for r in rows),
                  sufficient_semantic_failures=sum(r['failure_kind'] != 'generation_failed' and r['four_state'] == 'n10' for r in rows))
    applicable = [r for r in rows if r['integration'] != 'na']
    ni = len(applicable)
    numeric = {}
    for r in rows:
        for item in r['numeric']:
            key = item['dimension'] + ':' + item['unit']
            numeric.setdefault(key, []).append(item)
    diagnostics = {}
    for key, items in numeric.items():
        parsed = [x for x in items if x['status'] == 'parsed']
        diagnostics[key] = {status + '_N': sum(x['status'] == status for x in items) for status in ('parsed', 'missing', 'wrong_unit', 'unknown')}
        diagnostics[key]['MAE'] = sum(x['absolute_error'] for x in parsed) / len(parsed) if parsed else None
    return dict(N=n, reference_resolved_N=sum(r['reference_resolved'] for r in rows),
                response_returned_N=sum(r['response_returned'] for r in rows),
                ac_bounds=bounds('ac'), strict_bounds=[sum(r['strict'] == 'yes' for r in rows)/n, sum(r['strict'] != 'no' for r in rows)/n] if n else [None, None],
                coverage_bounds=[sum(r['coverage_lower'] for r in rows)/n, sum(r['coverage_upper'] for r in rows)/n] if n else [None, None],
                integration_N=ni, integration_bounds=[sum(r['integration'] == 'yes' for r in applicable)/ni, sum(r['integration'] != 'no' for r in applicable)/ni] if ni else [None, None],
                four_state=states, numeric=diagnostics)


def score_bundle(bundle, require_real=False):
    if bundle['schema_version'] != SCHEMA:
        raise ValueError('unsupported schema')
    refs = {r['intent_id']: r for r in bundle['references']}
    if len(refs) != len(bundle['references']):
        raise ValueError('duplicate reference')
    expected = [(r['intent_id'], r['arm']) for r in bundle['expected_cells']]
    actual = [(r['intent_id'], r['arm']) for r in bundle['cells']]
    scientific = {(i, a) for i in refs for a in ARMS} | {(i, 'Aref-8192') for i, r in refs.items() if r['oracle_eligible']}
    if len(expected) != len(set(expected)) or len(actual) != len(set(actual)) or set(expected) != set(actual) or set(expected) != scientific:
        raise ValueError('missing, duplicate or unexpected cell')
    if any(c['record_kind'] not in {'real', 'synthetic'} or (require_real and c['record_kind'] != 'real') for c in bundle['cells']):
        raise ValueError('non-real/mock generation record')
    rows = [score_cell(refs[c['intent_id']], c) for c in sorted(bundle['cells'], key=lambda c: (c['intent_id'], c['arm']))]
    lookup = {(r['intent_id'], r['arm']): r for r in rows}
    arms = {a: summarize([r for r in rows if r['arm'] == a]) for a in ARMS + ('Aref-8192',)}
    strata = {a: {s: summarize([r for r in rows if r['arm'] == a and r['stratum'] == s]) for s in sorted({r['stratum'] for r in rows})} for a in arms}
    comparisons = []
    for left, right in PAIRS:
        ids = sorted(i for i in refs if (i, left) in lookup and (i, right) in lookup)
        pairs = [(lookup[i, left], lookup[i, right]) for i in ids]
        gains = sum(a['strict'] == 'yes' and b['strict'] == 'no' for a, b in pairs)
        losses = sum(a['strict'] == 'no' and b['strict'] == 'yes' for a, b in pairs)
        unresolved = sum(a['strict'] == 'unknown' or b['strict'] == 'unknown' for a, b in pairs)
        n = len(pairs)
        lo = sum(int(a['strict'] == 'yes') - int(b['strict'] != 'no') for a, b in pairs) / n if n else None
        hi = sum(int(a['strict'] != 'no') - int(b['strict'] == 'yes') for a, b in pairs) / n if n else None
        # The same stratified draws are shared by both arms, for each paired eligible population.
        rng = np.random.default_rng(20261004)
        draws = []
        for st in sorted({refs[i]['stratum'] for i in ids}):
            positions = [j for j, i in enumerate(ids) if refs[i]['stratum'] == st]
            draws.append(rng.choice(positions, size=(10000, len(positions)), replace=True))
        sampled = np.concatenate(draws, axis=1) if draws else None
        intervals = {}
        for metric in ('ac', 'coverage', 'integration'):
            endpoints = []
            for bound in ('lower', 'upper'):
                def val(r, side):
                    endpoint = bound if side == 'left' else ('upper' if bound == 'lower' else 'lower')
                    if metric == 'ac': return r['ac'] if r['ac'] is not None else (0 if endpoint == 'lower' else 1)
                    if metric == 'coverage': return r['coverage_' + endpoint]
                    return None if r['integration'] == 'na' else int(r['integration'] == 'yes') if endpoint == 'lower' else int(r['integration'] != 'no')
                differences = np.array([np.nan if val(a, 'left') is None or val(b, 'right') is None else val(a, 'left') - val(b, 'right') for a, b in pairs])
                if n and np.isfinite(differences).any():
                    selected = differences[sampled]
                    counts = np.isfinite(selected).sum(axis=1)
                    means = np.divide(np.nansum(selected, axis=1), counts, out=np.full(10000, np.nan), where=counts > 0)
                    ci = np.quantile(means[np.isfinite(means)], [.025, .975], method='linear').tolist()
                else: ci = [None, None]
                endpoints.append(ci)
            intervals[metric + '_delta_ci_bounds'] = endpoints
            intervals[metric + '_delta_ci'] = endpoints[0] if endpoints[0] == endpoints[1] else None
        comparisons.append(dict(left=left, right=right, N=n, gains=gains, losses=losses,
                                resolved_pairs=n-unresolved, unknown_pairs=unresolved, testable=n-unresolved > 0,
                                strict_delta_bounds=[lo, hi], exact_p=exact_mcnemar(gains, losses), **intervals))
    for item, adjusted in zip(comparisons, holm([c['exact_p'] for c in comparisons])):
        item['holm_p'] = adjusted
    return dict(schema_version='pearl-answer-score-result-v1', rows=rows, arms=arms,
                strata=strata, comparisons=comparisons, bootstrap={'iterations': 10000, 'seed': 20261004, 'quantile': 'linear', 'unit': 'intent', 'stratified': True})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input'); parser.add_argument('output'); parser.add_argument('--require-real', action='store_true')
    args = parser.parse_args()
    result = score_bundle(json.loads(Path(args.input).read_text(encoding='utf-8')), args.require_real)
    with Path(args.output).open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)


if __name__ == '__main__':
    main()
