"""Create separately named development revision assets; never read sealed content."""
import copy
import hashlib
import json
import random
import sys
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'outputs/pearl-retrieval-dev80-20261003-01'
SOURCE = ROOT / 'outputs/pearl-dev-review-freeze-20261003-01'
OUT = ROOT / 'outputs/pearl-retrieval-dev80-gold-r02-20261003-01'
sys.path.insert(0, str(ROOT / 'experiments/pearl-retrieval-dev80-20261003'))
from score import load_run, read, sha, validate_gold_set

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')

def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    proposal = read(SOURCE / 'gold-correction-proposal.json')
    base_gold = ROOT / proposal['base_gold_path']
    assert sha(base_gold) == proposal['base_gold_sha256']
    inputs = load_run(BASE, base_gold)
    old = inputs['gold']; revised = copy.deepcopy(old)
    changes = []
    def replace(path, value):
        target = revised
        for key in path[:-1]:
            target = target[key]
        changes.append(dict(path=path, old_value=copy.deepcopy(target[path[-1]]), new_value=copy.deepcopy(value)))
        target[path[-1]] = value
    positions = {q['intent_id']: i for i, q in enumerate(old['intents'])}
    for item in proposal['mandatory_corrections']:
        assert sha(ROOT / item['source_review_path']) == item['source_review_sha256']
        i = positions[item['intent_id']]
        field = item['field']
        path = ['intents', i, 'reference_answer'] if field == 'reference_answer' else ['intents', i, 'requirements', int(field.split('[r')[1][0]) - 1, field.split('].')[1]]
        target = revised
        for key in path:
            target = target[key]
        assert target == item['old_value'], item
        replace(path, item['new_value'])
    i = positions['pearl-dev-080']
    atom = dict(atom_id='a3', locator_type='text_anchor', page=14,
        source_id='pearl-src-49fbc8413e27f3f1',
        anchor_text='On the other hand, it was veriﬁed numerically that the second order model captures better the structure of interactions between pedestrians and is able to produce the above behaviors.',
        supports='Numerical verification of the second-order model qualitative interaction behavior, distinguished from empirical validation.')
    replace(['intents', i, 'atoms'], revised['intents'][i]['atoms'] + [atom])
    replace(['intents', i, 'requirements', 1, 'support_bundles'], [['a2', 'a3']])
    replace(['dataset_id'], 'pearl-retrieval-dev-80-adobe106-20261003-r02')
    replace(['revision'], dict(number=2, date='2026-10-03', base_gold_sha256=sha(base_gold), status='agent_reviewed_preliminary', human_verified=False))
    validate_gold_set(revised, 80)
    changed = ['pearl-dev-012', 'pearl-dev-050', 'pearl-dev-080']
    assert all(a['query'] == b['query'] for a, b in zip(old['intents'], revised['intents']))
    assert all(a == b for a, b in zip(old['intents'], revised['intents']) if a['intent_id'] not in changed)
    OUT.mkdir()
    write(OUT / 'gold-r02.json', revised)
    write(OUT / 'gold-diff.json', dict(status='agent_reviewed_preliminary', human_verified=False,
        proposal_sha256=sha(SOURCE / 'gold-correction-proposal.json'), changes=changes,
        rationale='Adopt five proposed fields; explicitly encode dev080 numerical verification as a3 AND a2. dev012 exception numbers qualify mechanism scope; query does not ask for an exception enumeration.'))
    source_checks = []
    pages = {'pearl-dev-012': [1, 6, 8, 13], 'pearl-dev-050': [1, 2, 3, 4], 'pearl-dev-080': [14]}
    for ident in changed:
        sp = read(SOURCE / 'packets' / (ident + '.json'))
        for source in sp['sources']:
            assert sha(ROOT / source['source_path']) == source['sha256']
            assert sha(ROOT / source['document_path']) == source['document_sha256']
            if ident.endswith('080') and source['source_id'] != atom['source_id']:
                continue
            doc = pymupdf.open(ROOT / source['source_path'])
            for page in pages[ident]:
                text = doc[page - 1].get_text()
                name = source['source_id'] + '-p' + str(page)
                p = OUT / 'source-check' / (name + '.txt'); p.parent.mkdir(exist_ok=True)
                with p.open('x', encoding='utf8') as f: f.write(text)
                image_path = p.with_suffix('.png')
                doc[page - 1].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(image_path)
                source_checks.append(dict(intent_id=ident, source=source, page=page,
                    text_path=p.relative_to(OUT).as_posix(), text_sha256=sha(p),
                    render_path=image_path.relative_to(OUT).as_posix(), render_sha256=sha(image_path)))
                if ident.endswith('080'):
                    norm=lambda s:' '.join(s.split())
                    assert norm(atom['anchor_text']) in norm(text)
        packet = read(BASE / 'review/packets' / (ident + '.json'))
        packet['intent'] = {k: revised['intents'][positions[ident]][k] for k in packet['intent']}
        # Preserve the neutral original full pool; add no retrieval context.
        rnd = random.Random(20260929)
        rnd.shuffle(packet['candidates']); rnd.shuffle(packet['supplementary_candidates'])
        for child in packet['candidates'] + packet['supplementary_candidates']:
            assert child['text'] == inputs['children'][child['chunk_id']]['text']
            assert not set(child) & {'rank', 'score', 'method', 'channel'}
        write(OUT / 'review/packets' / (ident + '.json'), packet)
    write(OUT / 'source-check/bindings.json', dict(status='current', checks=source_checks,
        boundary='Source facts checked separately; these PDF texts are excluded from child support packets.'))
    write(OUT / 'preparation-verification.json', dict(status='passed', queries_unchanged=80,
        pilot_intents_unchanged=8, full_semantic_objects_unchanged=77, quotas='4 x 20',
        base_gold_sha256=sha(base_gold), revised_gold_sha256=sha(OUT / 'gold-r02.json'),
        frozen_child_sha256=inputs['preflight']['frozen_child_sha256'],
        original_rankings_sha256=sha(BASE / 'rankings.jsonl')))

if __name__ == '__main__':
    prepare()
