import asyncio
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).parent


def module(name):
    if not (HERE / (name + '.py')).exists():
        pytest.fail(f'{name} implementation is missing')
    spec = importlib.util.spec_from_file_location('answer_' + name, HERE / (name + '.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


@pytest.fixture
def g():
    return module('generate')


def config():
    return dict(protocol='openai_compatible', model='synthetic', base_url=None,
                timeout_seconds=1, output_tokens=2048, temperature_supported=True,
                seed_supported=True, provider_window_tokens=10000,
                provider_input_tokens=100, capability_evidence='synthetic fixture only')


class Client:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    async def ainvoke(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def answer(text='Synthetic only'):
    return SimpleNamespace(content=text, id='synthetic-id', response_metadata={'model_name': 'synthetic'}, usage_metadata=None)


def run(g, tmp_path, responses, **kw):
    client = Client(responses)
    result = asyncio.run(g.run_cell({'cell_id': 'x', 'query': 'Q', 'context': '[S1] C'},
                                   config(), 'a' * 64, tmp_path, client=client,
                                   synthetic=True, **kw))
    return result, client


def test_frozen_prompt_and_reject_reference():
    g = module("generate")
    assert g.build_request({'query': 'Q', 'context': 'C'})[0]['content'].endswith('Question:\nQ\n\nContext:\nC')
    with pytest.raises(ValueError, match='fields'):
        g.build_request({'query': 'Q', 'context': 'C', 'reference_answer': 'leak'})


def test_first_success_visible_retry_and_saved_hash(tmp_path):
    g = module("generate")
    result, client = run(g, tmp_path, [TimeoutError(), answer('first'), answer('second')])
    assert len(client.calls) == 2
    assert result['raw_answer'] == 'first'
    assert result['record_kind'] == 'synthetic'
    assert result['finish_reason'] is None
    assert result['usage'] is None and result['usage_unavailable_reason']
    assert len(result['attempts']) == 2
    saved = json.loads((tmp_path / 'x.json').read_text())
    assert saved == result
    assert saved['response_sha256'] == g.sha('first')


def test_failure_keeps_cell_and_does_not_retry_semantic_error(tmp_path):
    g = module("generate")
    result, client = run(g, tmp_path, [TimeoutError(), TimeoutError(), TimeoutError()])
    assert result['generation_status'] == 'generation_failed' and len(client.calls) == 3
    other, client = run(g, tmp_path / 'other', [ValueError('private error text')])
    assert len(client.calls) == 1 and 'private error text' not in json.dumps(other)


def test_no_overwrite_or_implicit_reuse(tmp_path):
    g = module("generate")
    result, _ = run(g, tmp_path, [answer()])
    with pytest.raises(FileExistsError):
        run(g, tmp_path, [answer()])
    assert g.exact_reuse(tmp_path / 'x.json', result['request_sha256'], result['config_sha256'], 'a' * 64) == result
    with pytest.raises(ValueError):
        g.exact_reuse(tmp_path / 'x.json', result['request_sha256'], result['config_sha256'], 'b' * 64)
    result['raw_answer'] = 'changed'
    (tmp_path / 'x.json').write_text(json.dumps(result))
    with pytest.raises(ValueError):
        g.exact_reuse(tmp_path / 'x.json', result['request_sha256'], result['config_sha256'], 'a' * 64)


def test_window_and_secrets_rejected_before_call(tmp_path):
    g = module("generate")
    bad = config() | {'provider_window_tokens': 100}
    with pytest.raises(ValueError, match='window'):
        asyncio.run(g.run_cell({'cell_id': 'x', 'query': 'Q', 'context': 'C'}, bad, 'a'*64, tmp_path, client=Client([]), synthetic=True))
    with pytest.raises(ValueError, match='config'):
        g.validate_config(config() | {'api_key': 'secret'})


def test_real_requires_gates_and_disallows_fake_client(tmp_path):
    g = module("generate")
    with pytest.raises(ValueError, match='prerequisite'):
        asyncio.run(g.run_cell({'cell_id': 'x', 'query': 'Q', 'context': 'C'}, config(), 'a'*64, tmp_path))
    with pytest.raises(ValueError, match='synthetic'):
        asyncio.run(g.run_cell({'cell_id': 'x', 'query': 'Q', 'context': 'C'}, config(), 'a'*64, tmp_path, client=Client([])))


def test_blind_export_has_no_strategy_model_or_l2(tmp_path):
    r = module('review')
    packets, mapping = r.export_blind([{'cell_id': 'A1-8192:q', 'intent_id': 'q', 'query': 'Q', 'raw_answer': 'A', 'arm': 'A1-8192', 'model': 'secret model', 'l2_sufficient': 'yes'}],
                                     {'q': {'reference_answer': 'R', 'key_targets': ['c1']}}, {'version': 'r1'})
    assert set(packets[0]) == {'packet_id', 'query', 'answer', 'reference', 'rubric'}
    assert 'A1-8192' not in json.dumps(packets) and 'secret model' not in json.dumps(packets)
    assert mapping[packets[0]['packet_id']]['cell_id'] == 'A1-8192:q'


def test_explicit_nonthinking_provider_option(tmp_path):
    g = module('generate')
    cfg = config() | {'extra_body': {'thinking': {'type': 'disabled'}}}
    client = Client([answer()])
    result = asyncio.run(g.run_cell({'cell_id': 'x', 'query': 'Q', 'context': 'C'}, cfg, 'a'*64, tmp_path, client=client, synthetic=True))
    assert client.calls[0][1]['extra_body'] == cfg['extra_body']
    assert result['parameters']['extra_body'] == cfg['extra_body']


def test_blind_decision_import_requires_actual_complete_review():
    r = module('review')
    with pytest.raises(ValueError):
        r.import_decisions([{'packet_id': 'answer-000001'}], [], {}, 'v1')
    with pytest.raises(ValueError):
        r.import_decisions([{'packet_id': 'answer-000001'}], [{'packet_id': 'answer-000001', 'version': 'v1', 'actual_read': False}], {}, 'v1')


def test_provider_response_id_distinct_from_sdk_run_id(tmp_path):
    g = module('generate')
    msg = answer()
    msg.response_metadata['id'] = 'provider-response-id'
    record, _ = run(g, tmp_path, [msg])
    assert record['response_id'] == 'provider-response-id'
    assert record['sdk_message_id'] == 'synthetic-id'


def test_blind_reference_whitelist_excludes_oracle_and_nested_identity():
    r=module('review')
    reference={'reference_answer':'R','key_targets':['t'],'target_definitions':{'t':{'text':'Conclusion','arm':'LEAK_ARM','model':'LEAK_MODEL'}},'required_conditions':['c'],'condition_definitions':{'c':'range'},'allowed_claim_groups':[['a']],'claim_definitions':{'a':'Explanation'},'integration_applicable':True,'integration_rule':'Compare','numeric_targets':[{'id':'n','value':1.2,'unit':'m/s','tolerance':0}], 'oracle':{'serialized_context':'LEAK_ORACLE','segments':[{'exact_text':'LEAK_BODY'}]},'selected_candidate_sha256':'LEAK_VERSION','uncertainty_mechanism':'LEAK_MECHANISM'}
    packets,_=r.export_blind([{'cell_id':'i::A0-4096','intent_id':'i','query':'Q','raw_answer':'A'}],{'i':reference},{'version':'r1'})
    encoded=json.dumps(packets)
    assert 'LEAK_' not in encoded
    for field in ['target_definitions','condition_definitions','claim_definitions','numeric_targets','integration_rule']:
        assert field in packets[0]['reference']
