"""Explicit development Gold revision binding; preserves the original retrieval identity.

Manifest v1 binds base gold/ranks/run/preflight/mapping, revised Gold, selection,
and an exact ordered replacement diff. Relative input paths use their manifest's
directory. All outputs are exclusive new files; no evaluation content is loaded.
"""
from __future__ import annotations

import argparse
import copy
import csv
import importlib.util
import math
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1] / 'pearl-retrieval-dev80-20261003'
sys.path.insert(0, str(BASE))


def module(name):
    spec = importlib.util.spec_from_file_location('revision_' + name, BASE / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


score = module('score')
analyze = module('analyze')
verify = module('verify')
# Only this newly loaded analysis module is changed; the original CLI stays intact.
analyze.COMPARISONS = (('R2', 'R1'), ('R3', 'R2'), ('R4', 'R3'))
ALLOWED = {'pearl-dev-012', 'pearl-dev-050', 'pearl-dev-080'}
DELTA_FIELDS = {
    'pearl-dev-012': (('requirements',0,'scope'),),
    'pearl-dev-050': (('reference_answer',),),
    'pearl-dev-080': (('reference_answer',),('requirements',1,'claim'),('requirements',1,'scope'),
                      ('requirements',1,'support_bundles'),('atoms',)),
}
METADATA_FIELDS = {'dataset_id','revision','status','human_verified'}


def resolve(path, manifest):
    path = Path(path)
    return path if path.is_absolute() else Path(manifest).resolve().parent / path


def apply_diff(base, diff):
    result = copy.deepcopy(base)
    changes = diff.get('changes')
    if not isinstance(changes, list) or not changes:
        raise ValueError('empty revision diff')
    used = set()
    for change in changes:
        path = change['path']
        if not isinstance(path, list) or not path or any(type(x) not in (str, int) for x in path):
            raise ValueError('invalid diff path')
        key = tuple(path)
        if key in used:
            raise ValueError('duplicate diff path')
        used.add(key)
        parent = result
        try:
            for part in path[:-1]:parent = parent[part]
            last = path[-1]
            if change.get('op', 'replace') == 'add':
                if not isinstance(parent, dict) or last in parent or change['old_value'] is not None:
                    raise ValueError('invalid diff addition')
            elif change.get('op', 'replace') == 'replace':
                if parent[last] != change['old_value']:
                    raise ValueError('diff old_value mismatch')
            else:raise ValueError('unsupported diff operation')
            parent[last] = copy.deepcopy(change['new_value'])
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError('invalid diff address') from exc
    return result


def validate_authorized_delta(base, revised, diff):
    """Limit the bound diff to adopted fields and keep all existing source atoms."""
    allowed_paths={(key,) for key in METADATA_FIELDS}
    for i,q in enumerate(base['intents']):
        allowed_paths.update(('intents',i)+path for path in DELTA_FIELDS.get(q['intent_id'],()))
    if any(tuple(c['path']) not in allowed_paths for c in diff['changes']):
        raise ValueError('diff contains unauthorized field or metadata path')
    q_by={q['intent_id']:q for q in revised['intents']}
    for prior in base['intents']:
        ident=prior['intent_id']
        if ident not in ALLOWED:continue
        current=q_by[ident]
        expected=copy.deepcopy(prior)
        try:
            for path in DELTA_FIELDS[ident]:
                old_parent=expected;new_parent=current
                for part in path[:-1]:old_parent=old_parent[part];new_parent=new_parent[part]
                old_parent[path[-1]]=copy.deepcopy(new_parent[path[-1]])
        except (KeyError,IndexError,TypeError) as exc:
            raise ValueError('authorized field structure mismatch') from exc
        if current != expected:
            raise ValueError('non-authorized intent fields must be preserved')
        if ident=='pearl-dev-080':
            old_atoms=prior['atoms'];new_atoms=current['atoms']
            if len(new_atoms)!=len(old_atoms)+1 or new_atoms[:-1]!=old_atoms:
                raise ValueError('prior atoms must be preserved with exactly one a3 append')
            a2=next((a for a in old_atoms if a['atom_id']=='a2'),None)
            a3=new_atoms[-1]
            if (a2 is None or a3.get('atom_id')!='a3' or a3.get('locator_type')!='text_anchor'
                    or a3.get('source_id')!=a2.get('source_id') or a3.get('page')!=a2.get('page')
                    or not isinstance(a3.get('anchor_text'),str) or not a3['anchor_text'].strip()
                    or not isinstance(a3.get('supports'),str) or not a3['supports'].strip()):
                raise ValueError('a3 numerical verification source/page/anchor identity mismatch')
            for field in ('source_sha256','source_version','source_path'):
                if a3.get(field)!=a2.get(field):
                    raise ValueError('a3 source binding differs from a2')
            if 'numer' not in a3['anchor_text'].casefold() or 'numer' not in a3['supports'].casefold():
                raise ValueError('a3 lacks explicit numerical verification anchor/supports')
            if current['requirements'][1]['requirement_id']!='r2' or current['requirements'][1]['support_bundles']!=[['a2','a3']]:
                raise ValueError('r2 mandatory a2+a3 bundle mismatch')
    for key in set(base)|set(revised):
        if key not in METADATA_FIELDS|{'intents'} and (key not in base or key not in revised or base[key]!=revised[key]):
            raise ValueError('frozen corpus/source/split metadata changed')
    if revised.get('status')!='agent_reviewed_preliminary' or revised.get('human_verified',False) is not False:
        raise ValueError('Gold preliminary metadata status changed')


def load_revision(base_directory, base_gold_path, revised_gold_path,
                  selected_review_manifest, revision_manifest):
    """Validate original retrieval then independently bind the authorized revision."""
    directory = Path(base_directory)
    # Preserve the original loader's fail-closed run/preflight identity checks.
    original = score.load_run(directory, base_gold_path)
    revision = score.read(revision_manifest)
    if (revision.get('schema_version') != 'pearl-gold-revision-r02-v1'
            or revision.get('status') != 'agent_reviewed_preliminary'
            or revision.get('human_verified') is not False):
        raise ValueError('revision identity/status mismatch')
    binding = revision['base']
    for path, field in ((base_gold_path, 'gold_sha256'), (directory/'rankings.jsonl', 'rankings_sha256'),
                        (directory/'run_manifest.json', 'run_manifest_sha256'), (directory/'preflight.json', 'preflight_sha256')):
        score.verify_hash(path, binding[field])
    base_mapping = resolve(binding['mapping_path'], revision_manifest)
    score.verify_hash(base_mapping, binding['mapping_sha256'])
    old = score.load_validated_inputs(directory, base_mapping, base_gold_path)
    score.verify_hash(revised_gold_path, revision['revised_gold_sha256'])
    score.verify_hash(selected_review_manifest, revision['selected_review_manifest_sha256'])
    diff_path = resolve(revision['diff_path'], revision_manifest)
    score.verify_hash(diff_path, revision['diff_sha256'])
    revised = score.read(revised_gold_path)
    diff=score.read(diff_path)
    if apply_diff(original['gold'], diff) != revised:
        raise ValueError('revised Gold differs from exact authorized diff')
    q_by = score.validate_gold_set(revised, 80)
    if [q['intent_id'] for q in revised['intents']] != list(original['q_by']):
        raise ValueError('intent order/identity changed')
    changed = set()
    for ident, q in q_by.items():
        prior = original['q_by'][ident]
        if q['query'] != prior['query'] or q['main_stratum'] != prior['main_stratum']:
            raise ValueError('query or stratum changed')
        if q != prior:changed.add(ident)
    if changed != ALLOWED or set(revision['changed_intent_ids']) != ALLOWED or len(revision['changed_intent_ids']) != 3:
        raise ValueError('77 unchanged intents or authorized three-intent delta mismatch')
    validate_authorized_delta(original['gold'],revised,diff)
    selection=score.read(selected_review_manifest)
    base_selection=directory/'review/selected-review-files.json'
    score.verify_hash(base_selection,selection['base_selection_sha256'])
    # Resolve the base map's unique assigned decision to its selected whole-file SHA.
    inherited_files={}
    for path,digest in old['mapping']['review_sha256'].items():
        items,_=score.review_files([path])
        for item in items:
            ident=item['intent_id']
            if ident in inherited_files:raise ValueError('duplicate original selected file intent')
            inherited_files[ident]=(str(Path(path).resolve()),digest)
    base_entries=score.read(base_selection)['files']
    if len(base_entries)!=80 or len({e['intent_id'] for e in base_entries})!=80:
        raise ValueError('original selected file manifest coverage mismatch')
    for entry in base_entries:
        ident=entry['intent_id']
        if ident not in inherited_files or entry['sha256']!=inherited_files[ident][1]:
            raise ValueError('original selected file manifest differs from validated base map')
    files = selection['files']
    ids = [entry['intent_id'] for entry in files]
    if len(ids) != 80 or len(set(ids)) != 80 or set(ids) != set(q_by):
        raise ValueError('selected review coverage mismatch')
    decisions = {}; review_hashes = {}; packet_hashes = {}
    for entry in files:
        ident = entry['intent_id']
        path = resolve(entry['path'], selected_review_manifest)
        packet_path = resolve(entry['packet_path'], selected_review_manifest)
        score.verify_hash(path, entry['sha256'])
        score.verify_hash(packet_path, entry['packet_sha256'])
        items, _ = score.review_files([path])
        selected = [d for d in items if d['intent_id'] == ident]
        if len(selected) != 1:
            raise ValueError('selected file lacks unique assigned intent')
        decision = selected[0]
        if ident not in ALLOWED:
            if entry['sha256']!=inherited_files[ident][1]:
                raise ValueError('inherited selected whole-file hash changed')
            old_packet = directory/'review/packets'/(ident+'.json')
            if decision != old['decisions'][ident] or entry['packet_sha256'] != score.sha(old_packet):
                raise ValueError('inherited selected review/packet changed')
        packet = score.read(packet_path)
        for child in packet['candidates'] + packet.get('supplementary_candidates', []):
            score.validate_child(child, original['children'])
        decisions[ident] = score.validate_decision(q_by[ident], packet, decision, entry['packet_sha256'])
        for method in score.METHODS:
            score.require_reviewed([c['chunk_id'] for c in original['ranks'][ident,method]['results']],decision['reviewed_ids'],20)
        review_hashes[str(path.resolve())] = entry['sha256']
        packet_hashes[str(packet_path.resolve())] = entry['packet_sha256']
    mapping = dict(status='agent_reviewed_preliminary_development_80_Gold_r02',human_verified=False,
                   run_id=original['run']['run_id'], gold_sha256=score.sha(revised_gold_path),
                   base_gold_sha256=score.sha(base_gold_path), rankings_sha256=score.sha(directory/'rankings.jsonl'),
                   run_manifest_sha256=score.sha(directory/'run_manifest.json'),preflight_sha256=score.sha(directory/'preflight.json'),
                   frozen_child_sha256=original['preflight']['frozen_child_sha256'],
                   revision_manifest_sha256=score.sha(revision_manifest), selected_review_manifest_sha256=score.sha(selected_review_manifest),
                   review_sha256=review_hashes,packets_sha256=packet_hashes, scoring_range=list(score.KS),intents=list(decisions.values()))
    original.update(gold=revised,q_by=q_by,gold_path=Path(revised_gold_path),decisions=decisions,mapping=mapping,
                    original_inputs=old,revision_manifest=revision,revision_manifest_path=Path(revision_manifest))
    return original


def independent_verification(inputs, scored):
    """Use the independent boolean oracle, never scorer metrics, for 1,280 prefixes."""
    by = {(d['intent_id'],d['method']):d for d in scored['details']}
    if len(scored['details']) != 320 or set(by) != set(inputs['ranks']):
        raise ValueError('verification matrix mismatch')
    sums = {(m,k,f):0 for m in score.METHODS for k in score.KS for f in ('CEGR','BestGroupCov','CompleteRR')}
    prefixes = 0
    for (ident,method),row in inputs['ranks'].items():
        if row['status'] != 'success':raise ValueError('execution failure is not zero')
        ids = [c['chunk_id'] for c in row['results']]
        for k in score.KS:
            actual = verify.oracle(inputs['q_by'][ident],inputs['decisions'][ident]['atom_paths'],ids,k)
            for field,value in actual.items():
                expected = by[ident,method]['scores'][str(k)][field]
                if value is None or expected is None:
                    equal = value == expected
                else:equal = math.isclose(value,expected,rel_tol=0,abs_tol=1e-12)
                if not equal:raise ValueError('independent prefix mismatch')
                if field in ('CEGR','BestGroupCov','CompleteRR'):sums[method,k,field] += value
            prefixes += 1
    aggregates = 0
    for (method,k,field),total in sums.items():
        summary = scored['summary'][method][str(k)]
        label = 'CompleteMRR' if field == 'CompleteRR' else field
        if summary['N'] != 80 or not math.isclose(total/80,summary[label],rel_tol=0,abs_tol=1e-12):
            raise ValueError('independent aggregate mismatch')
        aggregates += 1
    return dict(status='passed',independent_formula_prefixes=prefixes,independent_aggregates=aggregates,
                matrix_cells=320,intent_count=80,all_K_le20_adjudicated=True,
                oracle_code_sha256=score.sha(BASE/'verify.py'),human_verified=False)


def verify_saved_outputs(base_directory, base_gold_path, revised_gold_path,
                         selected_review_manifest, revision_manifest, output_directory):
    """Reopen saved scores/mapping and all original and revision input bindings."""
    inputs=load_revision(base_directory,base_gold_path,revised_gold_path,selected_review_manifest,revision_manifest)
    output=Path(output_directory)
    mapping=score.read(output/'support-map.json')
    scored=score.read(output/'score-details.json')
    if mapping != inputs['mapping']:
        raise ValueError('saved mapping differs from selected review content')
    for path,field in ((output/'support-map.json','mapping_sha256'),(revised_gold_path,'gold_sha256'),
                       (revision_manifest,'revision_manifest_sha256'),(Path(base_directory)/'rankings.jsonl','rankings_sha256')):
        score.verify_hash(path,scored[field])
    expected_codes=(Path(__file__),BASE/'score.py',BASE/'protocol.py',BASE/'analyze.py',BASE/'verify.py',
                    BASE.parent/'pearl-index-106-adobe-20260929/score_pilot.py')
    expected_bindings={str(p.resolve()):score.sha(p) for p in expected_codes}
    if scored.get('scoring_code_sha256') != expected_bindings:
        raise ValueError('saved scoring code binding mismatch')
    if scored.get('intent_count') != 80 or scored.get('human_verified') is not False:
        raise ValueError('saved scoring count/status mismatch')
    result=independent_verification(inputs,scored)
    result.update(revision_manifest_sha256=score.sha(revision_manifest),mapping_sha256=score.sha(output/'support-map.json'),
                  scores_sha256=score.sha(output/'score-details.json'),verification_code_sha256=score.sha(Path(__file__)),
                  selected_review_content_bindings=80,saved_output_bindings_verified=True)
    return result


def deliver(base_directory, base_gold_path, revised_gold_path, selected_review_manifest,
            revision_manifest, output_directory):
    output = Path(output_directory)
    if output.exists():raise FileExistsError(output)
    inputs = load_revision(base_directory,base_gold_path,revised_gold_path,selected_review_manifest,revision_manifest)
    details = score.build_details(inputs)
    scored = dict(status='agent_reviewed_preliminary_80_intent_development_Gold_r02_revision',human_verified=False,
                  run_id=inputs['run']['run_id'],intent_count=80,methods=list(score.METHODS),k=list(score.KS),
                  gold_sha256=score.sha(revised_gold_path),revision_manifest_sha256=score.sha(revision_manifest),
                  rankings_sha256=inputs['mapping']['rankings_sha256'],summary=score.aggregate(details),details=details,
                  strata={h:score.aggregate(details,{q['intent_id'] for q in inputs['gold']['intents'] if q['main_stratum']==h})
                          for h in sorted({q['main_stratum'] for q in inputs['gold']['intents']})})
    verification = independent_verification(inputs,scored)
    stats = analyze.statistics(inputs,details)
    diagnostics = analyze.failures(inputs,details)
    prior_details = score.build_details(inputs['original_inputs'])
    old_by = {(d['intent_id'],d['method']):d for d in prior_details}
    delta = dict(status=scored['status'],base_gold_sha256=score.sha(base_gold_path),revised_gold_sha256=score.sha(revised_gold_path),
                 base_summary=score.aggregate(prior_details),revised_summary=scored['summary'],details=[])
    for d in details:
        prior = old_by[d['intent_id'],d['method']]
        delta['details'].append(dict(intent_id=d['intent_id'],method=d['method'],changed=prior['scores']!=d['scores'],
            scores={str(k):{f:d['scores'][str(k)][f]-prior['scores'][str(k)][f] for f in ('CEGR','BestGroupCov','CompleteRR')} for k in score.KS},
            before=prior['scores'],after=d['scores']))
    output.mkdir(parents=True)
    score.write(output/'support-map.json',inputs['mapping'])
    scored['mapping_sha256']=score.sha(output/'support-map.json')
    scored['scoring_code_sha256']={str(p.resolve()):score.sha(p) for p in (Path(__file__),BASE/'score.py',BASE/'protocol.py',BASE/'analyze.py',BASE/'verify.py',BASE.parent/'pearl-index-106-adobe-20260929/score_pilot.py')}
    score.write(output/'score-details.json',scored)
    flat=[]
    for d in details:
        row={f:d[f] for f in ('intent_id','method','main_stratum','status','returned')}
        for k in score.KS:
            for f in ('CEGR','BestGroupCov','CompleteRR','first_complete_rank'):row[f+'@'+str(k)]=d['scores'][str(k)][f]
        flat.append(row)
    with (output/'scores.csv').open('x',encoding='utf8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
    score.write(output/'statistics.json',stats)
    score.write(output/'per-intent-failures.json',diagnostics)
    score.write(output/'delta-vs-r01.json',delta)
    verification=verify_saved_outputs(base_directory,base_gold_path,revised_gold_path,selected_review_manifest,revision_manifest,output)
    score.write(output/'verification.json',verification)
    return dict(scores=scored,statistics=stats,verification=verification,delta=delta)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('base-directory','base-gold','revised-gold','selected-review-manifest','revision-manifest','output-directory'):
        parser.add_argument('--'+flag,type=Path,required=True)
    parser.add_argument('--verify-only',action='store_true',help='Reopen existing mapping/scores and validate bindings and independent formula without writing')
    args=parser.parse_args()
    function=verify_saved_outputs if args.verify_only else deliver
    result=function(args.base_directory,args.base_gold,args.revised_gold,args.selected_review_manifest,args.revision_manifest,args.output_directory)
    if args.verify_only:
        import json
        print(json.dumps(result,sort_keys=True))
