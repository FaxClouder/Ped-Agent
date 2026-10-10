"""Audit source-grounded PEARL questions and flag leakage before sealing."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
STRATA = ('single_source', 'numeric_table', 'within_paper_multi', 'cross_paper')

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalized(text: str) -> str:
    text = unicodedata.normalize('NFKC', text).replace('\u00ad', '')
    return re.sub(r'\s+', ' ', text).casefold().strip()

def relaxed(text: str) -> str:
    return re.sub(r'[^\w]+', '', normalized(text))

def table_field_present(value: str, text: str) -> bool:
    # PDF extraction can split decimal digits and unit glyphs with spaces.
    # Preserve punctuation: 2.41 must never become equivalent to 241.
    value, text = normalized(value), normalized(text)
    return value in text or re.sub(r'\s+', '', value) in re.sub(r'\s+', '', text)

def read_rows(path: Path) -> list[dict]:
    if path.suffix == '.json':
        data = json.loads(path.read_text(encoding='utf-8'))
        return data['intents'] if isinstance(data, dict) else data
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def validate_structure(q: dict, allowed_sources: set[str]) -> None:
    ident = q['intent_id']
    require(all(q.get(field) for field in ('family_id', 'query', 'reference_answer', 'main_stratum')), f'{ident}: missing identity/content')
    require(q['main_stratum'] in STRATA, f'{ident}: unknown stratum')
    atoms = {a['atom_id']: a for a in q['atoms']}
    requirements = {r['requirement_id']: r for r in q['requirements']}
    require(atoms and len(atoms) == len(q['atoms']), f'{ident}: empty/duplicate atoms')
    require(requirements and len(requirements) == len(q['requirements']), f'{ident}: empty/duplicate requirements')
    require(q['evidence_groups'] and len({g['group_id'] for g in q['evidence_groups']}) == len(q['evidence_groups']), f'{ident}: group identity')
    for atom in atoms.values():
        require(atom['source_id'] in allowed_sources, f'{ident}: source outside assigned corpus')
        require(isinstance(atom['page'], int) and atom['page'] > 0 and atom.get('supports'), f'{ident}: invalid atom page/support')
        require(atom['locator_type'] in ('text_anchor', 'table_cell'), f'{ident}: locator type')
        if atom['locator_type'] == 'text_anchor':
            require(bool(atom.get('anchor_text')), f'{ident}: empty source anchor')
        else:
            require(all(atom.get(field) for field in ('table', 'row', 'column', 'value')), f'{ident}: incomplete table locator')
    for req in requirements.values():
        require(req.get('claim') and req.get('scope'), f'{ident}: claim/scope empty')
        bundles = req['support_bundles']
        require(bundles and all(bundle and len(bundle) == len(set(bundle)) and set(bundle) <= atoms.keys() for bundle in bundles), f'{ident}: bundle atom reference')
        require(len({tuple(sorted(bundle)) for bundle in bundles}) == len(bundles), f'{ident}: duplicate bundles')
        require(not any(set(a) < set(b) for a in bundles for b in bundles), f'{ident}: redundant bundle')
    groups = [set(g['requirements']) for g in q['evidence_groups']]
    require(all(group and group <= requirements.keys() for group in groups), f'{ident}: empty/unknown group requirements')
    require(not any(a <= b for i, a in enumerate(groups) for j, b in enumerate(groups) if i != j), f'{ident}: redundant complete group')
    require(set.union(*groups) == requirements.keys(), f'{ident}: unused requirement')
    require({a for req in requirements.values() for bundle in req['support_bundles'] for a in bundle} == atoms.keys(), f'{ident}: unused atom')
    sources = {a['source_id'] for a in atoms.values()}
    if q['main_stratum'] == 'cross_paper':
        for group in groups:
            for bundles in itertools.product(*(requirements[r]['support_bundles'] for r in group)):
                require(len({atoms[a]['source_id'] for bundle in bundles for a in bundle}) >= 2, f'{ident}: cross-paper complete path needs two sources')
    else:
        require(len(sources) == 1, f'{ident}: non-cross stratum has multiple sources')
    if q['main_stratum'] == 'within_paper_multi':
        require(all(len(group) >= 2 for group in groups), f'{ident}: multi-evidence group requires two necessary facts')
        require(len({(a['page'], a.get('anchor_text', a.get('row'))) for a in atoms.values()}) >= 2, f'{ident}: multi-evidence location count')
    if q['main_stratum'] == 'numeric_table':
        require(bool(re.search(r'\d', q['reference_answer'])), f'{ident}: numeric answer lacks a number')

def leakage_candidates(left: list[dict], right: list[dict]) -> list[dict]:
    flags = []
    def study_template(query: str) -> str:
        text = normalized(query)
        text = re.sub(r"\b[\w'-]+\s+et\s+al\.?", '<study>', text)
        return re.sub(r'\b(?:19|20)\d{2}\b', '<year>', text)
    for a in left:
        aq = normalized(a['query'])
        at = re.sub(r'\d+(?:\.\d+)?', '<number>', aq)
        aw = set(re.findall(r'[a-z]+', aq))
        for b in right:
            bq = normalized(b['query'])
            bw = set(re.findall(r'[a-z]+', bq))
            types = []
            if a['family_id'] == b['family_id']:
                types.append('shared_family_id')
            if aq == bq:
                types.append('exact_query')
            elif at == re.sub(r'\d+(?:\.\d+)?', '<number>', bq):
                types.append('numeric_template')
            if normalized(a['reference_answer']) == normalized(b['reference_answer']):
                types.append('exact_answer')
            if aq != bq and '<study>' in study_template(aq) and study_template(aq) == study_template(bq):
                types.append('study_masked_template')
            similarity = len(aw & bw) / len(aw | bw) if aw | bw else 0.0
            if similarity >= 0.70:
                types.append('query_token_overlap')
            for kind in types:
                flags.append({'type': kind, 'left': a['intent_id'], 'right': b['intent_id'],
                              'query_jaccard': similarity, 'left_query': a['query'], 'right_query': b['query']})
    return flags

def all_leakage_candidates(dev: list[dict], evaluation: list[dict]) -> list[dict]:
    result = [dict(flag, comparison_scope='cross_split') for flag in leakage_candidates(dev, evaluation)]
    for scope, rows in (('within_dev', dev), ('within_eval', evaluation)):
        for left, right in itertools.combinations(rows, 2):
            result.extend(dict(flag, comparison_scope=scope) for flag in leakage_candidates([left], [right]))
    return result

def audit(candidates: Path, directory: Path, role: str, output: Path) -> dict:
    import pymupdf

    if output.exists():
        raise FileExistsError(f'refusing to overwrite {output}')
    allocation = json.loads((directory / 'source-allocation.json').read_text(encoding='utf-8'))
    source_inventory = json.loads((directory / role / 'sources.json').read_text(encoding='utf-8'))['sources']
    sources = {row['source_id']: row for row in source_inventory}
    rows = read_rows(candidates)
    problems, checks, opened = [], [], {}
    adobe_pages = {}
    try:
        for q in rows:
            try:
                validate_structure(q, set(sources))
            except (ValueError, KeyError, TypeError) as error:
                problems.append({'intent_id': q.get('intent_id'), 'type': 'structure', 'error': str(error)})
                continue
            for atom in q['atoms']:
                sid = atom['source_id']
                if sid not in opened:
                    source = sources[sid]
                    require(sha(ROOT / source['source_path']) == source['sha256'], f'source PDF hash changed: {sid}')
                    require(sha(ROOT / source['document_path']) == source['document_sha256'], f'Adobe hash changed: {sid}')
                    opened[sid] = pymupdf.open(ROOT / source['source_path'])
                    document = json.loads((ROOT / source['document_path']).read_text(encoding='utf-8'))
                    page_text = defaultdict(list)
                    for element in sorted(document['elements'], key=lambda item: item['order']):
                        page_text[element['page_number']].append(element['text'])
                    adobe_pages[sid] = {page: normalized('\n'.join(parts)) for page, parts in page_text.items()}
                doc = opened[sid]
                if not 1 <= atom['page'] <= len(doc):
                    problems.append({'intent_id': q['intent_id'], 'atom_id': atom['atom_id'], 'type': 'invalid_pdf_page'})
                    continue
                pdf_text = normalized(doc[atom['page'] - 1].get_text('text'))
                if atom['locator_type'] == 'text_anchor':
                    anchor = normalized(atom['anchor_text'])
                    strict = anchor in pdf_text
                    fallback = relaxed(anchor) in relaxed(pdf_text)
                    adobe = anchor in adobe_pages[sid].get(atom['page'], '') or relaxed(anchor) in relaxed(adobe_pages[sid].get(atom['page'], ''))
                    mode = 'strict' if strict else 'punctuation_or_linebreak_normalized' if fallback else 'missing'
                    if mode == 'missing':
                        problems.append({'intent_id': q['intent_id'], 'atom_id': atom['atom_id'], 'type': 'pdf_anchor_missing', 'page': atom['page'], 'anchor_text': atom['anchor_text']})
                else:
                    strict_fields = {field: normalized(str(atom[field])) in pdf_text for field in ('table', 'row', 'column', 'value')}
                    fields = {field: table_field_present(str(atom[field]), pdf_text) for field in strict_fields}
                    mode = ('table_fields_present' if all(strict_fields.values()) else
                            'table_fields_space_normalized' if all(fields.values()) else 'table_visual_review_needed')
                    adobe = None
                    if not all(fields.values()):
                        problems.append({'intent_id': q['intent_id'], 'atom_id': atom['atom_id'], 'type': 'table_locator_text_missing', 'fields': fields})
                checks.append({'intent_id': q['intent_id'], 'atom_id': atom['atom_id'], 'source_id': sid,
                               'page': atom['page'], 'pdf_match_mode': mode, 'adobe_page_anchor_present': adobe})
    finally:
        for doc in opened.values():
            doc.close()
    counts = dict(Counter(q['main_stratum'] for q in rows))
    expected = allocation['stratum_quotas'][role]
    if counts != expected:
        problems.append({'type': 'stratum_quota', 'actual': counts, 'expected': expected})
    if len({q['intent_id'] for q in rows}) != len(rows):
        problems.append({'type': 'duplicate_intent_id'})
    result = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'role': role,
              'candidate_sha256': sha(candidates), 'source_allocation_sha256': sha(directory / 'source-allocation.json'),
              'code_sha256': sha(Path(__file__)), 'intent_count': len(rows), 'strata': counts,
              'source_count': len(opened), 'atom_count': len(checks), 'problems': problems,
              'atom_checks': checks, 'status': 'traceability_passed' if not problems else 'repair_required',
              'interpretation': 'Structural and source locator checks only; independent Agent semantic review remains required.'}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('role', 'intent_count', 'source_count', 'atom_count', 'strata', 'status')}))
    print('problems', len(problems))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--role', choices=('dev', 'eval_a', 'eval_b'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit(args.candidates.resolve(), args.directory.resolve(), args.role, args.output.resolve())
