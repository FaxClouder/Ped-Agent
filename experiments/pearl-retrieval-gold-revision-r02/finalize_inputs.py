"""Bind explicitly selected independent decisions to original run and revision."""
import json
from pathlib import Path
from prepare_revision import ROOT, BASE, SOURCE, OUT, read, sha, write

def finalize():
    selected = read(BASE / 'review/selected-review-files.json')
    changed = ['pearl-dev-012', 'pearl-dev-050', 'pearl-dev-080']
    files = []
    for entry in selected['files']:
        ident = entry['intent_id']
        old_path = ROOT / entry['path']
        assert sha(old_path) == entry['sha256']
        name = ident + ('-r02.json' if ident == 'pearl-dev-080' else '.json')
        path = OUT / 'review/decisions' / name if ident in changed else old_path
        packet = (OUT if ident in changed else BASE) / 'review/packets' / (ident + '.json')
        files.append(dict(intent_id=ident, path=str(path.resolve()), sha256=sha(path),
            packet_path=str(packet.resolve()), packet_sha256=sha(packet),
            origin='independent_r02_review' if ident in changed else 'inherited_exact_r01_selected_decision'))
    assert len(files) == len({f['intent_id'] for f in files}) == 80
    selection_path = OUT / 'selected-review-manifest.json'
    write(selection_path, dict(status='agent_reviewed_preliminary', human_verified=False,
        base_selection_sha256=sha(BASE / 'review/selected-review-files.json'), files=files))
    original_gold = ROOT / read(SOURCE / 'gold-correction-proposal.json')['base_gold_path']
    mapping = BASE / ('pearl-retrieval-dev-80-adobe106-support-map-' + BASE.name + '.json')
    write(OUT / 'revision-manifest.json', dict(schema_version='pearl-gold-revision-r02-v1',
        status='agent_reviewed_preliminary', human_verified=False,
        base=dict(gold_sha256=sha(original_gold), rankings_sha256=sha(BASE / 'rankings.jsonl'),
            run_manifest_sha256=sha(BASE / 'run_manifest.json'), preflight_sha256=sha(BASE / 'preflight.json'),
            mapping_path=str(mapping.resolve()), mapping_sha256=sha(mapping)),
        revised_gold_sha256=sha(OUT / 'gold-r02.json'), selected_review_manifest_sha256=sha(selection_path),
        diff_path='gold-diff.json', diff_sha256=sha(OUT / 'gold-diff.json'), changed_intent_ids=changed,
        method_freeze_sha256=sha(ROOT / 'experiments/pearl-dev-review-freeze-20261003/method-freeze.json'),
        original_queries_sha256=read(BASE / 'run_manifest.json')['queries_sha256']))

if __name__ == '__main__':
    finalize()
