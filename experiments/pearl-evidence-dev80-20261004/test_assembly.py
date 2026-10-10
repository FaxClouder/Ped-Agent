import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('assembly_local', Path(__file__).with_name('assemble.py'))
if SPEC is not None and SPEC.loader is not None and Path(SPEC.origin).exists():
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
else:
    module = None


class Counter:
    fingerprint = 'synthetic-character-v1'
    def count(self, text):
        return len(text)


def chunk(cid, text, parent=None, version='v1', **extra):
    import hashlib
    return dict(chunk_id=cid, text=text, text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                parent_chunk_id=parent, version_id=version, source_id='s', source_sha256='v1',
                policy_version='parent-child-v1', parser_version='adobe-pdf-extract-v1',
                title='Title', locator='p.1', **extra)


def assemble(children, parents=None, strategy='C0', budget=4096):
    assert module is not None, 'assembly implementation is missing'
    return module.assemble('intent', 'query', children, parents or {}, Counter(), strategy, budget)


def test_duplicate_parent_is_merged_and_child_links_preserved():
    a, b = chunk('a', 'alpha', 'p'), chunk('b', 'beta', 'p')
    p = chunk('p', 'alpha and beta')
    a['parent_text_sha256'] = b['parent_text_sha256'] = p['text_sha256']
    r = assemble([a, b], {'p': p}, 'C1')
    assert len(r['units']) == 1
    assert r['units'][0]['child_ids'] == ['a', 'b']
    assert len(r['steps']['expanded']['units']) == 2


@pytest.mark.parametrize('parents', [{}, {'p': chunk('p', 'unrelated')}])
def test_missing_or_non_containing_parent_retains_child(parents):
    r = assemble([chunk('a', 'alpha', 'p')], parents, 'C1')
    assert r['units'][0]['text'] == 'alpha'
    assert r['expansion_trace'][0]['reason'] in {'missing_parent', 'containment_failed'}


def test_body_drift_rejected():
    c = chunk('a', 'alpha'); c['text'] = 'changed'
    with pytest.raises(ValueError, match='hash'):
        assemble([c])


def test_cross_version_parent_rejected():
    with pytest.raises(ValueError, match='version'):
        assemble([chunk('a', 'alpha', 'p')], {'p': chunk('p', 'alpha', version='v2')}, 'C1')


def test_parent_hash_drift_rejected():
    c = chunk('a', 'alpha', 'p'); c['parent_text_sha256'] = 'bad'
    with pytest.raises(ValueError, match='hash'):
        assemble([c], {'p': chunk('p', 'alpha')}, 'C1')


def test_duplicate_child_rejected():
    with pytest.raises(ValueError, match='duplicate'):
        assemble([chunk('a', 'alpha'), chunk('a', 'alpha')])


def test_empty_results():
    r = assemble([])
    assert r['units'] == [] and r['serialized_context'] == ''
    assert r['token_count'] == 0


def test_complete_serialization_boundary_and_saved_text(tmp_path):
    r = assemble([chunk('a', 'alpha')])
    n = r['token_count']
    assert n > len('alpha')
    exact = assemble([chunk('a', 'alpha')], budget=n)
    short = assemble([chunk('a', 'alpha')], budget=n-1)
    assert exact['units'][0]['truncated'] is False
    assert short['token_count'] <= n-1
    assert short['units'][0]['text'] == 'alph'
    assert short['units'][0]['discarded_text'] == 'a'
    p = tmp_path / 'contexts.jsonl'
    module.write_jsonl(p, [short])
    assert module.verify_saved(p, Counter()) == 1
    with pytest.raises(FileExistsError):
        module.write_jsonl(p, [short])


def test_long_table_truncation_preserves_exact_prefix_and_trace():
    table = 'Heading | speed (m/s)\n' + 'row | 3.2\n'*200
    r = assemble([chunk('a', table), chunk('b', 'later')], budget=200)
    assert r['token_count'] <= 200
    u = r['units'][0]
    assert u['text'] + u['discarded_text'] == table
    assert r['truncation_trace'][-1]['reason'] == 'after_budget_stop'


def test_gold_labels_are_not_accepted_by_query_input():
    assert module is not None, 'assembly implementation is missing'
    with pytest.raises(ValueError, match='query-only'):
        module.validate_queries([{'intent_id':'i', 'query':'q', 'requirements':[]}])


def test_actual_pinned_tokenizer_utf8_and_budget():
    assert module is not None, 'assembly implementation is missing'
    counter = module.load_counter(Path(__file__).parents[2] / 'memPed/knowledge/models/bge-m3/tokenizer.json')
    r = module.assemble('i', 'q', [chunk('a', '中文速度单位 m/s; table | value\n'*100)], {}, counter, 'C0', 100)
    assert counter.count(r['serialized_context']) == r['token_count'] <= 100
    assert r['units'][0]['text'] + r['units'][0]['discarded_text'] == '中文速度单位 m/s; table | value\n'*100


def test_stage_sampling_is_stable_and_balanced():
    records = [{'intent_id': f'{t}-{i:02}', 'main_stratum':t} for t in 'abcd' for i in range(20)]
    chosen = module.select_intents(records, 20)
    assert chosen == module.select_intents(list(reversed(records)), 20)
    assert len(chosen) == 20
    assert all(sum(x.startswith(t) for x in chosen) == 5 for t in 'abcd')


def test_run_refuses_existing_stage_before_reading_inputs(tmp_path):
    with pytest.raises(FileExistsError):
        module.run_stage(tmp_path, 20, tmp_path / 'absent.json')


def test_relative_input_identity_resolves_against_repository():
    assert module.repository_path('outputs/example.json') == module.ROOT/'outputs/example.json'
