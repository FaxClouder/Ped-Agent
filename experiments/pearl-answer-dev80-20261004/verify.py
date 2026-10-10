"""Independent Layer 3 arithmetic and byte provenance verifier (no scorer imports)."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def recompute(data, require_real=False):
    if data['schema_version'] != 'pearl-answer-score-input-v1':
        raise ValueError('schema')
    references = {x['intent_id']: x for x in data['references']}
    if len(references) != len(data['references']): raise ValueError('duplicate reference')
    arm_names = ['A0-4096', 'A1-4096', 'A0-8192', 'A1-8192', 'Aref-8192']
    required = {(i, a) for i in references for a in arm_names[:4]}
    required.update((i, arm_names[4]) for i, x in references.items() if x['oracle_eligible'])
    planned = [(x['intent_id'], x['arm']) for x in data['expected_cells']]
    observed = [(x['intent_id'], x['arm']) for x in data['cells']]
    if set(planned) != required or set(observed) != required or len(planned) != len(required) or len(observed) != len(required):
        raise ValueError('cell matrix')
    conversions = [('speed', {'m/s': 1, 'cm/s': .01, 'km/h': 1/3.6}),
                   ('count', {'people': 1, 'persons': 1, 'pedestrians':1, 'ped':1}), ('percentage', {'%': 1, 'fraction': 100, 'proportion':100}),
                   ('percentage_points', {'percentage_points': 1}), ('density', {'people/m2': 1, 'ped/m2':1, 'ped/m²':1, 'pedestrians/m²':1, 'pedestrians/m2':1, 'persons/m²':1, 'people/m²':1}),
                   ('flow', {'people/s': 1, 'people/min': 1/60, 'ped/s':1, 'pedestrians/s':1, 'ped/min':1/60}), ('length', {'m': 1, 'cm': .01}),
                   ('time', {'s': 1, 'min': 60}), ('inverse_length', {'1/m': 1}),
                   ('specific_flow', {'persons/(m*s)': 1}), ('angle', {'degrees': 1, 'degree':1}),
                   ('acceleration', {'m/s2': 1}), ('dimensionless', {'dimensionless': 1, 'integer':1}),
                   ('linear_density', {'people/m':1, 'ped/m':1, 'pedestrians/m':1}),
                   ('area_per_pedestrian', {'m2/person':1, 'm2/ped':1, 'm²/person':1, 'm²/ped':1, 'cm²/ped':.0001, 'cm2/person':.0001}), ('age', {'years': 1})]
    rows = []
    for c in sorted(data['cells'], key=lambda x: (x['intent_id'], x['arm'])):
        if c['record_kind'] not in ['real', 'synthetic'] or require_real and c['record_kind'] != 'real': raise ValueError('mock/non-real')
        if c['generation_status'] not in ['returned', 'generation_failed']: raise ValueError('generation status')
        if c['l2_sufficient'] not in ['yes', 'no', 'unknown']: raise ValueError('L2')
        ref = references[c['intent_id']]; d = {} if c['generation_status'] == 'generation_failed' else c.get('decision', {})
        permitted = ['correct', 'incorrect', 'missing', 'unknown']
        def lookup(field, ids):
            result = [d.get(field, {}).get(i, 'missing') for i in ids]
            if any(x not in permitted for x in result): raise ValueError('semantic label')
            return result
        if not ref['allowed_claim_groups'] or any(not g or len(g) != len(set(g)) for g in ref['allowed_claim_groups']): raise ValueError('groups')
        group_labels = [lookup('claims', g) for g in ref['allowed_claim_groups']]
        coverage = [max(sum(x == 'correct' for x in g)/len(g) for g in group_labels),
                    max(sum(x in ['correct', 'unknown'] for x in g)/len(g) for g in group_labels)]
        key = lookup('targets', ref['key_targets']); conditions = lookup('conditions', ref['required_conditions'])
        if not key: raise ValueError('no targets')
        relation = d.get('integration', 'unknown') if ref['integration_applicable'] else 'na'
        if relation not in ['yes', 'no', 'unknown', 'na']: raise ValueError('integration')
        contradiction = d.get('contradiction', 'unknown')
        if contradiction not in [True, False, 'unknown']: raise ValueError('contradiction')
        if not isinstance(d.get('refusal', False), bool): raise ValueError('refusal')
        numeric = []
        for t in ref['numeric_targets']:
            answer = d.get('numeric', {}).get(t['id'], {})
            status = answer.get('status', 'missing')
            if status not in ['parsed', 'missing', 'unknown']: raise ValueError('numeric status')
            item = {'id': t['id'], 'dimension': t['dimension'], 'unit': t['unit'], 'absolute_error': None,
                    'relative_error': None, 'within_tolerance': None, 'status': status}
            if status == 'parsed':
                canonical_dimension={'proportion':'percentage','relative_time_improvement':'percentage','integer':'dimensionless','count_per_width':'linear_density'}.get(t['dimension'],t['dimension'])
                table = next((units for dim, units in conversions if dim == canonical_dimension), {})
                if answer['unit'] not in table or t['unit'] not in table:
                    item.update(status='wrong_unit', within_tolerance=False)
                else:
                    if t['tolerance'] < 0 or any(not math.isfinite(float(v)) for v in [answer['value'], t['value'], t['tolerance']]): raise ValueError('numeric range')
                    normalized = answer['value'] * table[answer['unit']] / table[t['unit']]
                    error = abs(normalized - t['value'])
                    if abs(normalized-t['value']) <= max(1e-12 * max(abs(normalized), abs(t['value'])), 1e-12): error = 0.0
                    accepted=error<=t['tolerance']
                    if 'allowed_values' in t:
                        alternatives=t['allowed_values']
                        if not isinstance(alternatives,list) or not alternatives or t['tolerance']!=0 or not t.get('tolerance_basis') or any(not isinstance(x,(float,int)) or isinstance(x,bool) or not math.isfinite(x) for x in alternatives): raise ValueError('invalid numeric alternatives')
                        accepted=any(abs(normalized-x)<=max(1e-12*max(abs(normalized),abs(x)),1e-12) for x in alternatives)
                    item.update(absolute_error=error, relative_error=error/abs(t['value']) if t['value'] != 0 else None,
                                within_tolerance=accepted)
            numeric.append(item)
        failed = c['generation_status'] == 'generation_failed'
        failure = 'generation_failed' if failed else 'refusal' if d.get('refusal', False) else None
        if not ref['resolved']: ac = None
        elif failed or failure == 'refusal' or contradiction is True or 'incorrect' in key or any(x['within_tolerance'] is False for x in numeric): ac = 0
        elif contradiction == 'unknown' or 'unknown' in key+conditions or relation == 'unknown' or any(x['status'] == 'unknown' for x in numeric): ac = None
        elif key+conditions == ['correct'] * len(key+conditions) and relation in ['yes', 'na'] and all(x['within_tolerance'] is True for x in numeric): ac = 1
        elif 'correct' in key: ac = .5
        else: ac = 0
        strict = {None: 'unknown', 0: 'no', .5: 'no', 1: 'yes'}[ac]
        state = 'unknown' if 'unknown' in [strict, c['l2_sufficient']] else 'n{}{}'.format(int(c['l2_sufficient'] == 'yes'), int(strict == 'yes'))
        if failed:
            coverage = [0.0, 0.0]; relation = 'no' if ref['integration_applicable'] else 'na'
        rows.append(dict(intent_id=c['intent_id'], arm=c['arm'], stratum=ref['stratum'], reference_resolved=ref['resolved'],
                         response_returned=not failed, ac=ac, strict=strict, coverage_lower=coverage[0], coverage_upper=coverage[1],
                         complete_claim_group=coverage[0] == 1, integration=relation, numeric=numeric, failure_kind=failure, four_state=state))
    def aggregate(selection):
        n = len(selection)
        def fraction(values): return sum(values)/n if n else None
        distribution = {s: sum(x['four_state'] == s for x in selection) for s in ['n11', 'n10', 'n01', 'n00', 'unknown']}
        ns = distribution['n11'] + distribution['n10']
        distribution.update(sufficient_N=ns, new_failure_rate=distribution['n10']/ns if ns else None,
                            sufficient_strict_success=distribution['n11']/ns if ns else None,
                            generation_failed=sum(x['failure_kind'] == 'generation_failed' for x in selection),
                            sufficient_technical_failures=sum(x['four_state'] == 'n10' and x['failure_kind'] == 'generation_failed' for x in selection),
                            sufficient_semantic_failures=sum(x['four_state'] == 'n10' and x['failure_kind'] != 'generation_failed' for x in selection))
        applicable = [x for x in selection if x['integration'] != 'na']; ni = len(applicable)
        diagnostics = {}
        for dimunit in sorted({(v['dimension'], v['unit']) for x in selection for v in x['numeric']}):
            values = [v for x in selection for v in x['numeric'] if (v['dimension'], v['unit']) == dimunit]
            counts = {s+'_N': sum(v['status'] == s for v in values) for s in ['parsed', 'missing', 'wrong_unit', 'unknown']}
            counts['MAE'] = sum(v['absolute_error'] for v in values if v['status'] == 'parsed') / counts['parsed_N'] if counts['parsed_N'] else None
            diagnostics[':'.join(dimunit)] = counts
        return dict(N=n, reference_resolved_N=sum(x['reference_resolved'] for x in selection), response_returned_N=sum(x['response_returned'] for x in selection),
                    ac_bounds=[fraction([x['ac'] or 0 for x in selection]), fraction([1 if x['ac'] is None else x['ac'] for x in selection])],
                    strict_bounds=[fraction([x['strict']=='yes' for x in selection]), fraction([x['strict']!='no' for x in selection])],
                    coverage_bounds=[fraction([x['coverage_lower'] for x in selection]), fraction([x['coverage_upper'] for x in selection])],
                    integration_N=ni, integration_bounds=[sum(x['integration']=='yes' for x in applicable)/ni, sum(x['integration']!='no' for x in applicable)/ni] if ni else [None, None],
                    four_state=distribution, numeric=diagnostics)
    arms = {a: aggregate([x for x in rows if x['arm'] == a]) for a in arm_names}
    strata = {a: {s: aggregate([x for x in rows if x['arm'] == a and x['stratum'] == s]) for s in sorted({x['stratum'] for x in rows})} for a in arm_names}
    matrix = {(x['intent_id'], x['arm']): x for x in rows}
    pairs = [('A1-4096', 'A0-4096'), ('A1-8192', 'A0-8192'), ('A0-8192', 'A0-4096'), ('A1-8192', 'A1-4096'), ('Aref-8192', 'A1-8192')]
    comparisons = []
    for a, b in pairs:
        ids = sorted(i for i in references if (i, a) in matrix and (i, b) in matrix)
        paired = [(matrix[i, a], matrix[i, b]) for i in ids]; n = len(ids)
        gains = sum(x['strict']=='yes' and y['strict']=='no' for x,y in paired)
        losses = sum(x['strict']=='no' and y['strict']=='yes' for x,y in paired)
        unknown = sum('unknown' in [x['strict'], y['strict']] for x,y in paired)
        discordant = gains + losses
        probability = min(1., 2.*sum(math.comb(discordant, k) for k in range(min(gains, losses)+1))/2**discordant) if discordant else 1.
        generator = np.random.default_rng(20261004); chunks = []
        for category in sorted({references[i]['stratum'] for i in ids}):
            indexes = [j for j,i in enumerate(ids) if references[i]['stratum'] == category]
            chunks.append(generator.choice(indexes, size=(10000, len(indexes)), replace=True))
        draws = np.concatenate(chunks, axis=1) if chunks else None
        intervals = {}
        for metric in ['ac', 'coverage', 'integration']:
            cis = []
            for upper in [False, True]:
                def value(x, right=False):
                    use_upper = not upper if right else upper
                    if metric == 'ac': return x['ac'] if x['ac'] is not None else int(use_upper)
                    if metric == 'coverage': return x['coverage_upper' if use_upper else 'coverage_lower']
                    if x['integration'] == 'na': return None
                    return int(x['integration'] != 'no') if use_upper else int(x['integration'] == 'yes')
                delta = np.array([np.nan if value(x) is None or value(y, True) is None else value(x)-value(y, True) for x,y in paired])
                if n and np.isfinite(delta).any():
                    sample = delta[draws]; sizes = np.isfinite(sample).sum(axis=1)
                    estimates = np.divide(np.nansum(sample, axis=1), sizes, out=np.full(10000, np.nan), where=sizes > 0)
                    cis.append(np.quantile(estimates[np.isfinite(estimates)], [.025, .975], method='linear').tolist())
                else: cis.append([None, None])
            intervals[metric+'_delta_ci_bounds'] = cis
            intervals[metric+'_delta_ci'] = cis[0] if cis[0] == cis[1] else None
        lower = sum(int(x['strict']=='yes')-int(y['strict']!='no') for x,y in paired)/n if n else None
        upper = sum(int(x['strict']!='no')-int(y['strict']=='yes') for x,y in paired)/n if n else None
        comparisons.append(dict(left=a, right=b, N=n, gains=gains, losses=losses, resolved_pairs=n-unknown, unknown_pairs=unknown,
                                testable=n-unknown > 0, strict_delta_bounds=[lower, upper], exact_p=probability, **intervals))
    running = 0.
    for rank, index in enumerate(sorted(range(5), key=lambda j: comparisons[j]['exact_p'])):
        running = max(running, min(1., (5-rank)*comparisons[index]['exact_p']))
        comparisons[index]['holm_p'] = running
    return dict(schema_version='pearl-answer-score-result-v1', rows=rows, arms=arms, strata=strata, comparisons=comparisons,
                bootstrap={'iterations': 10000, 'seed': 20261004, 'quantile': 'linear', 'unit': 'intent', 'stratified': True})


def digest(value):
    text=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def cross_bind(data, artifacts, mode):
    """Bind scoring cells to separately frozen records; performs no semantic judging."""
    def fail(message): raise ValueError('cross-binding '+message)
    def load(path):
        path=Path(path)
        if path.suffix=='.jsonl': return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        return json.loads(path.read_text(encoding='utf-8'))
    def rows(value):
        if isinstance(value,list): return value
        if isinstance(value,dict) and isinstance(value.get('rows'),list): return value['rows']
        if isinstance(value,dict) and isinstance(value.get('references'),list): return value['references']
        return [value]
    roles={}
    answer_file_hashes={}
    for artifact in artifacts:
        role=artifact['role']
        if role in {'input','result'}: continue
        value=load(artifact['path']); values=rows(value)
        roles.setdefault(role,[]).extend(values)
        if role=='answer' and isinstance(value,dict) and 'intent_id' in value and 'arm' in value:
            answer_file_hashes[(value['intent_id'],value['arm'])]=artifact['sha256']
    def mapping(role):
        out={}
        for row in roles.get(role,[]):
            if not isinstance(row,dict) or 'intent_id' not in row or 'arm' not in row: fail(role+' row identity missing')
            key=(row['intent_id'],row['arm'])
            if key in out: fail(role+' duplicate identity')
            out[key]=row
        return out
    sources=mapping('answer'); contexts=mapping('context'); decisions=mapping('decision'); labels=mapping('l2')
    expected={(c['intent_id'],c['arm']) for c in data['cells']}
    if set(sources)!=expected or not expected<=set(contexts) or not expected<=set(labels): fail('source cell matrix mismatch')
    returned={k for k,v in sources.items() if v.get('generation_status')=='returned'}
    if set(decisions)!=returned: fail('selected decision matrix mismatch')
    references={}
    for row in roles.get('reference',[]):
        ident=row.get('intent_id')
        if not ident or ident in references: fail('reference identity missing/duplicate')
        references[ident]=row
    if {r['intent_id'] for r in data['references']}!=set(references): fail('selected reference matrix mismatch')
    for ref in data['references']:
        if ref!=references[ref['intent_id']]: fail('selected reference content differs')
    if len(roles.get('config',[]))!=1 or len(roles.get('prompt',[]))!=1: fail('config/prompt selection ambiguous')
    config=roles['config'][0]; template=roles['prompt'][0].get('prompt_template')
    if not isinstance(template,str) or not template: fail('prompt template missing')
    for cell in data['cells']:
        key=(cell['intent_id'],cell['arm']); answer=sources[key]; context=contexts[key]; label=labels[key]
        if mode=='real' and answer.get('record_kind')!='real': fail('real answer provenance missing')
        content={k:v for k,v in answer.items() if k!='record_sha256'}
        record_sha=digest(content)
        if answer.get('record_sha256')!=record_sha: fail('generation saved record digest mismatch')
        accepted={record_sha}
        if key in answer_file_hashes: accepted.add(answer_file_hashes[key])
        if cell.get('generation_record_sha256') not in accepted: fail('selected generation record hash differs')
        if cell.get('record_kind')!=answer.get('record_kind') or cell.get('generation_status')!=answer.get('generation_status'): fail('generation status/identity differs')
        body=context.get('context'); query=context.get('query')
        if not isinstance(body,str) or not isinstance(query,str): fail('frozen query/context missing')
        try: request=template.format(query=query,exact_saved_context=body)
        except (KeyError,ValueError): fail('prompt template invalid')
        if answer.get('query')!=query or answer.get('request')!=request: fail('saved request differs from exact context/prompt')
        if answer.get('config')!=config: fail('selected model config differs')
        actual={'request_sha256':digest(request),'context_sha256':digest(body),'config_sha256':digest(config)}
        for field,value in actual.items():
            if answer.get(field)!=value or cell.get(field)!=value: fail(field+' differs')
        if context.get('context_sha256')!=actual['context_sha256'] or context.get('request_sha256')!=actual['request_sha256'] or context.get('request')!=request: fail('generation input digest differs')
        if 'prompt_sha256' in answer and answer['prompt_sha256']!=digest(template): fail('prompt digest differs')
        response=digest(answer['raw_answer']) if answer.get('generation_status')=='returned' else None
        if answer.get('response_sha256')!=response or cell.get('response_sha256')!=response: fail('raw answer digest differs')
        if cell.get('l2_sufficient')!=label.get('sufficient') or label.get('context_sha256')!=actual['context_sha256']: fail('L2 selected label/context differs')
        if key in returned and cell.get('decision')!=decisions[key].get('decision'): fail('selected decision differs')
        if key not in returned and cell.get('decision'): fail('technical failure has fabricated semantic decision')
    return {'cross_bound_cells':len(expected),'selected_references':len(references),'selected_decisions':len(decisions)}


def verify_saved(bindings):
    if bindings['schema_version'] != 'pearl-answer-score-bindings-v1' or bindings['mode'] not in ['real', 'synthetic']:
        raise ValueError('bindings schema/mode')
    roles = {a['role'] for a in bindings['artifacts']}
    required = {'input', 'result', 'answer', 'prompt', 'reference', 'context', 'config', 'decision', 'l2'}
    if not required <= roles: raise ValueError('missing artifact roles')
    paths = [str(Path(a['path']).resolve()) for a in bindings['artifacts']]
    if len(paths) != len(set(paths)): raise ValueError('duplicate artifact paths')
    for artifact in bindings['artifacts']:
        actual = hashlib.sha256(Path(artifact['path']).read_bytes()).hexdigest()
        if actual != artifact['sha256']: raise ValueError('changed ' + artifact['role'])
    input_path, result_path = Path(bindings['input_path']).resolve(), Path(bindings['result_path']).resolve()
    for role, path in [('input', input_path), ('result', result_path)]:
        if not any(a['role'] == role and Path(a['path']).resolve() == path for a in bindings['artifacts']): raise ValueError('unbound '+role)
    data = json.loads(input_path.read_text(encoding='utf-8'))
    saved = json.loads(result_path.read_text(encoding='utf-8'))
    cross_report = cross_bind(data, bindings['artifacts'], bindings['mode'])
    calculated = recompute(data, require_real=bindings['mode'] == 'real')
    if calculated != saved: raise ValueError('saved result differs from independent recomputation')
    return {'verified': True, 'mode': bindings['mode'], 'cells': len(calculated['rows']), 'artifacts': len(paths), **cross_report}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('bindings'); parser.add_argument('output')
    args = parser.parse_args()
    report = verify_saved(json.loads(Path(args.bindings).read_text(encoding='utf-8')))
    with Path(args.output).open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)


if __name__ == '__main__': main()
