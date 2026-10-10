"""Reopen the exclusive delivery and verify hashes and run-local document links."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def check_manifest(root, manifest):
    root = Path(root).resolve()
    files = manifest['artifacts_sha256']
    if manifest.get('artifact_count', len(files)) != len(files):
        raise ValueError('artifact cardinality mismatch')
    for relative, expected in files.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('missing or escaping artifact: ' + relative)
        if digest(path) != expected:
            raise ValueError('artifact hash drift: ' + relative)
    return len(files)


def check_document(path, root=None):
    path = Path(path)
    boundary = Path(root).resolve() if root is not None else path.parent.resolve()
    text = path.read_text('utf8')
    if len(re.findall(r'^# ', text, re.M)) != 1 or not re.search(r'^\*[^\n]*status:\s*current[^\n]*\*$', text, re.M | re.I):
        raise ValueError('document title/status mismatch')
    links = []
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
        if '://' in target or Path(target.split('#', 1)[0]).is_absolute():
            raise ValueError('delivery documents require local relative links')
        target = target.split('#', 1)[0]
        resolved=(path.parent / target).resolve()
        if target and not resolved.is_relative_to(boundary):raise ValueError('escaping document link: '+target)
        if target and not resolved.is_file():raise ValueError('broken document link: ' + target)
        links.append(target)
    return len(links)


def check_external_envelopes(root,output,receipt,manifest):
    root=Path(root).resolve();output=Path(output).resolve();receipt=Path(receipt).resolve()
    if not output.is_relative_to(root):raise ValueError('delivery output escapes repository root')
    required={'command-package-r02.json','command-package-r02.stdout.log','command-package-r02.stderr.log','delivery-verification-e1-r01.json'}
    declared=set(manifest.get('external_post_freeze_envelopes',[]))
    if not required.issubset(declared) or any(Path(name).is_absolute() or Path(name).name!=name for name in declared):raise ValueError('required external envelope declaration missing or invalid')
    if receipt!=output/'delivery-verification-e1-r01.json' or receipt.name not in declared:raise ValueError('verification receipt is not the declared external envelope')
    sealed={(root/relative).resolve() for relative in manifest['artifacts_sha256']}
    if any((output/name).resolve() in sealed for name in declared):raise ValueError('external envelope must be excluded from sealed artifacts')
    return True


def check_delivery_fields(manifest):
    counts=manifest['counts']
    expected={'configurations':13,'retrieved':1040,'method_cells':4160,'contexts':2080,'score_details':22880,'summary_cells':286,'independent_intents':80,'failed':0}
    for field,value in expected.items():
        if counts.get(field)!=value:raise ValueError('delivery count mismatch: '+field)
    decision=manifest['decisions'];selected=decision.get('selected',[]);status=decision.get('status')
    candidates={f'{chunker}-L{length}-O0-M0' for chunker in ('C1','C2','C3','C4') for length in (256,384,512)}
    if status not in ('frozen','pending_unknown') or len(selected)>2 or len(set(selected))!=len(selected) or not set(selected)<=candidates:raise ValueError('candidate status mismatch')
    if status=='frozen' and len(selected)!=min(2,len(decision.get('nonduplicate_metrics',[]))):raise ValueError('frozen candidate count mismatch')
    if decision.get('baseline_retained')!='B0-regex320-overlap48-M0':raise ValueError('candidate baseline mismatch')
    expected_status='E1_matrix_complete_selection_pending' if status=='pending_unknown' else 'E1_complete_candidates_frozen'
    if manifest.get('status')!=expected_status:raise ValueError('delivery/candidate status mismatch')
    budget=manifest['budget']
    if decision.get('generation_calls')!=0 or any(budget.get(field)!=0 for field in ('generation_calls','external_model_api_calls','external_judge_api_calls')):raise ValueError('generation/API boundary crossed')
    return True


def main(root, output, receipt):
    root = Path(root).resolve(); output = Path(output).resolve();receipt=Path(receipt).resolve()
    if receipt.exists():
        raise FileExistsError('exclusive verification receipt required')
    manifest_path = output / 'delivery-manifest.json'
    manifest = json.loads(manifest_path.read_text('utf8'))
    check_external_envelopes(root,output,receipt,manifest)
    count = check_manifest(root, manifest)
    nested=('outputs/pearl-chunking-dev80-20261005-03/delivery-manifest.json','outputs/pearl-chunking-dev80-20261005-04/attempt-delivery-manifest.json')
    for relative in nested:
        path=root/relative
        if manifest['artifacts_sha256'].get(relative)!=digest(path):raise ValueError('delivery/nested manifest hash drift: '+relative)
        check_manifest(root,json.loads(path.read_text('utf8')))
    if manifest.get('inputs',{}).get('E0_manifest_sha256')!=digest(root/nested[0]):raise ValueError('delivery E0 input hash drift')
    links = {name: check_document(output / name,root) for name in ('handoff.md', 'reproduction_commands_e1.md')}
    for name in ('command-package-r02.json','command-package-r02.stdout.log','command-package-r02.stderr.log'):
        if not (output/name).is_file():raise ValueError('missing external package envelope: '+name)
    command = json.loads((output / 'command-package-r02.json').read_text('utf8'))
    if command.get('exit_code') != 0:
        raise ValueError('package command failed')
    check_delivery_fields(manifest);counts=manifest['counts'];decision=manifest['decisions']
    result = dict(status='passed',manifest_sha256=digest(manifest_path),
                  artifact_count=count,document_links_checked=links,
                  package_receipt_sha256=digest(output/'command-package-r02.json'),
                  external_envelopes_checked=sorted(manifest['external_post_freeze_envelopes']),
                  E0_manifest_sha256=digest(root/nested[0]),retained_attempt_manifest_sha256=digest(root/nested[1]),E0_and_retained_attempt_reopened=True,counts=counts,
                  candidate_status=decision['status'],selected=decision['selected'])
    with receipt.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print('E1 delivery reopened and verified:', count, 'artifacts', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    main(args.root, args.output, args.receipt)
