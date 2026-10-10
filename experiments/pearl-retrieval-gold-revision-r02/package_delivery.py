"""Freeze new scientific delivery and retain byte-verified old research assets."""
from prepare_revision import ROOT, BASE, SOURCE, OUT, read, sha, write
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).parent))
from revision import verify_saved_outputs
import score

def package():
    proposal = read(SOURCE / 'gold-correction-proposal.json')
    gold = ROOT / proposal['base_gold_path']
    verify = verify_saved_outputs(BASE, gold, OUT / 'gold-r02.json', OUT / 'selected-review-manifest.json',
        OUT / 'revision-manifest.json', OUT / 'analysis-r02-01')
    try:
        score.load_run(BASE, OUT / 'gold-r02.json')
    except ValueError as error:
        assert 'hash mismatch' in str(error)
    else:
        raise AssertionError('original loader must reject revised Gold')
    for root, expected in [(BASE, '6539488c5ea10d6fa1b7737c6c24b7b75c1b5244b3aaa17ae7bc8ebc1ac343b0'),
        (SOURCE, 'e981364b2bd9c2456e99bed00f800a8da800046afca51659b11fbfe5db1fd8a2')]:
        assert sha(root / 'delivery-manifest.json') == expected
        for name, digest in read(root / 'delivery-manifest.json')['artifacts_sha256'].items():
            assert sha(root / name) == digest
    frozen = read(OUT / 'immutable-input-verification.json')
    for name, digest in frozen['frozen_input_sha256'].items():
        assert sha(ROOT / name) == digest
    for name, digest in frozen['sealed_files_sha256'].items():
        assert sha(ROOT / name) == digest
        assert (ROOT / name).stat().st_file_attributes & 1
    review = read(OUT / 'code-review-r02.json')
    assert not review['findings']
    for name, digest in review['source_code_sha256'].items():
        assert sha(ROOT / name) == digest
    snapshots = OUT / 'code-snapshot'; snapshots.mkdir()
    paths = list(Path(__file__).parent.glob('*.py'))
    paths += [ROOT / 'experiments/pearl-retrieval-dev80-20261003' / name
        for name in ['score.py', 'protocol.py', 'analyze.py', 'verify.py']]
    paths += [ROOT / 'experiments/pearl-index-106-adobe-20260929/score_pilot.py']
    for path in paths:
        target = snapshots / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(target)
        shutil.copyfile(path, target)
        assert sha(target) == sha(path)
    write(OUT / 'stage-A-completion.json', dict(status='current', stage='A', completed=True,
        quality_status='agent_reviewed_preliminary', human_verified=False,
        original_loader_rejects_revised_gold=True, independent_verification=verify,
        original_deliveries_verified=[538, 93], frozen_inputs_verified=244, sealed_files_verified=200,
        sealed_content_semantically_read=False, evaluation_200_runs=0, original_rankings_reused=True,
        source_child_index_method_query_changes=0, unchanged_whole_intents=77, pilot_intents_unchanged=8,
        selected_unique_intents=80, independent_blind_changed_intents=3, tests_passed=54,
        stage_B_executed=False, full_release_frozen=False,
        next_checkpoint='Report stage A; stage B uses synthetic split/expected_count/query-only input adaptation.'))
    docs = [Path(__file__).parent / 'README.md', Path(__file__).parent / 'development-gold-r02-analysis-2026-10-03.md',
        ROOT / 'docs/README.md', ROOT / 'experiments/README.md']
    files = [p for p in OUT.rglob('*') if p.is_file()]
    write(OUT / 'delivery-manifest.json', dict(status='stage_A_complete', quality_status='agent_reviewed_preliminary',
        human_verified=False, artifact_count=len(files), artifacts_sha256={p.relative_to(OUT).as_posix():sha(p) for p in files},
        workspace_files_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths + docs},
        base_gold_sha256=sha(gold), revised_gold_sha256=sha(OUT / 'gold-r02.json'),
        rankings_sha256=sha(BASE / 'rankings.jsonl'),
        interpretation='Development Gold r02 revision only; original retrieval/run/preflight/r01 outputs retained; sealed 200 not executed.'))
    print('Stage A delivery frozen', len(files), 'artifacts; original outputs and sealed hashes verified')

if __name__ == '__main__':
    package()
