"""Frozen, directly invoked answer experiment; no EvidenceGraph or hidden retries."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

PROMPT = '''Answer the research question in English using only the supplied context.
State the requested findings and retain the relevant experimental conditions,
numerical values and units. For comparisons, explicitly explain the relationship
between the findings rather than listing unrelated facts. Use the supplied
source labels for citations where possible. Do not invent missing evidence.
If the context does not establish part of the answer, state that limitation.

Question:
{query}

Context:
{exact_saved_context}'''
CELL_FIELDS = {'cell_id', 'intent_id', 'arm', 'query', 'context', 'context_sha256', 'request', 'request_sha256'}
CONFIG_FIELDS = {'protocol', 'model', 'base_url', 'timeout_seconds', 'output_tokens',
                 'temperature_supported', 'seed_supported', 'provider_window_tokens',
                 'provider_input_tokens', 'capability_evidence'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(value):
    return hashlib.sha256((value if isinstance(value, str) else canonical(value)).encode('utf-8')).hexdigest()


def build_request(cell):
    if set(cell) - CELL_FIELDS or not {'query', 'context'} <= set(cell):
        raise ValueError('generation fields must contain only query/context and declared identity metadata')
    if not all(isinstance(cell[k], str) and cell[k] for k in ('query', 'context')):
        raise ValueError('query/context must be nonempty strings')
    request = [{'role': 'user', 'content': PROMPT.format(query=cell['query'], exact_saved_context=cell['context'])}]
    if 'context_sha256' in cell and cell['context_sha256'] != sha(cell['context']):
        raise ValueError('context SHA mismatch')
    if 'request' in cell and cell['request'] != request[0]['content']:
        raise ValueError('saved request differs from frozen template')
    if 'request_sha256' in cell and cell['request_sha256'] != sha(request[0]['content']):
        raise ValueError('request SHA mismatch')
    return request


def validate_config(config):
    if set(config) - CONFIG_FIELDS - {'extra_body'} or not CONFIG_FIELDS <= set(config):
        raise ValueError('config must contain precisely nonsecret declared fields')
    if 'extra_body' in config and config['extra_body'] != {'thinking': {'type': 'disabled'}}:
        raise ValueError('only frozen explicit nonthinking extra_body is supported')
    if config['protocol'] not in ('openai_compatible', 'anthropic') or not config['model']:
        raise ValueError('invalid provider config')
    for key in ('temperature_supported', 'seed_supported'):
        if type(config[key]) is not bool:
            raise ValueError('explicit supported/unsupported config required')
    for key in ('output_tokens', 'provider_window_tokens', 'provider_input_tokens'):
        if type(config[key]) is not int or config[key] <= 0:
            raise ValueError('provider window and full request token count required')
    if config['output_tokens'] != 2048:
        raise ValueError('frozen output reserve is 2048')
    if config['provider_input_tokens'] + 2048 > config['provider_window_tokens']:
        raise ValueError('provider window does not accommodate full request plus output reserve')
    if not isinstance(config['capability_evidence'], str) or not config['capability_evidence']:
        raise ValueError('provider capability evidence required')
    if config['timeout_seconds'] <= 0:
        raise ValueError('timeout must be positive')
    if config['base_url']:
        parsed = urlsplit(config['base_url'])
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('config base URL must not contain credentials or query')
    return dict(config)


def _gates(prerequisites, config_sha256, *, preflight):
    needed = ['provider_capabilities'] if preflight else ['provider_capabilities', 'reference_freeze', 'calibration', 'preflight']
    if not prerequisites or any(k not in prerequisites for k in needed):
        raise ValueError('research prerequisite evidence missing')
    result = {}
    for name in needed:
        item = prerequisites[name]
        path = Path(item['path'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item['sha256']:
            raise ValueError('prerequisite SHA mismatch: ' + name)
        evidence = json.loads(path.read_text(encoding='utf-8'))
        if evidence.get('status') != 'passed' or evidence.get('record_kind') == 'synthetic':
            raise ValueError('prerequisite must be actual verified evidence: ' + name)
        if name in ('provider_capabilities', 'preflight') and evidence.get('config_sha256') != config_sha256:
            raise ValueError('prerequisite provider config changed')
        if name == 'calibration' and (evidence.get('resolved_anchors') != 40 or evidence.get('ac_exact_agreement', 0) < .9 or evidence.get('claim_micro_agreement', 0) < .9 or evidence.get('sentinels_passed') is not True):
            raise ValueError('calibration prerequisite threshold not met')
        result[name] = {'sha256': digest, 'path': str(path)}
    return result


def _real_client(config):
    from ped_research_agent.config import load_settings
    from ped_research_agent.model_gateway import _build_chat_client
    settings = load_settings().answer
    if (settings.model, settings.protocol, settings.base_url) != (config['model'], config['protocol'], config['base_url']):
        raise ValueError('requested config differs from configured direct model')
    settings = settings.model_copy(update={'max_tokens': 2048, 'temperature': 0 if config['temperature_supported'] else None,
                                          'max_retries': 0, 'timeout_seconds': config['timeout_seconds']})
    return _build_chat_client(settings)


def _technical(exc):
    return isinstance(exc, (TimeoutError, ConnectionError)) or type(exc).__name__ in {
        'APITimeoutError', 'APIConnectionError', 'RateLimitError', 'ConnectError', 'ReadTimeout'}


async def run_cell(cell, config, manifest_sha256, output_dir, *, client=None, synthetic=False, prerequisites=None, preflight=False):
    if client is not None and not synthetic:
        raise ValueError('injected client is synthetic only')
    request = build_request(cell)
    config = validate_config(config)
    if not re.fullmatch('[0-9a-f]{64}', manifest_sha256):
        raise ValueError('explicit manifest SHA required')
    config_digest = sha(config)
    gates = {} if synthetic else _gates(prerequisites, config_digest, preflight=preflight)
    request_bytes = len(canonical(request).encode('utf-8'))
    if not synthetic and request_bytes > config['provider_input_tokens']:
        raise ValueError('full serialized request exceeds frozen conservative UTF-8 admission bound')
    if preflight and not cell['cell_id'].startswith('preflight-'):
        raise ValueError('preflight must use a separate nonresearch cell')
    cell_id = cell['cell_id']
    if not re.fullmatch(r'[A-Za-z0-9_.:-]+', cell_id):
        raise ValueError('unsafe cell ID')
    path = Path(output_dir) / (cell_id.replace(':', '_') + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive reservation occurs before any network activity, including construction.
    with path.open('x', encoding='utf-8') as handle:
        record = {'schema_version': 'pearl-answer-generation-v1', 'cell_id': cell_id,
                  'intent_id': cell.get('intent_id'), 'arm': cell.get('arm'), 'query': cell['query'],
                  'record_kind': 'synthetic' if synthetic else 'real', 'purpose': 'nonresearch_preflight' if preflight else 'research',
                  'manifest_sha256': manifest_sha256, 'context_sha256': sha(cell['context']),
                  'request': request[0]['content'], 'request_sha256': sha(request[0]['content']),
                  'messages': request, 'messages_sha256': sha(request), 'prompt_sha256': sha(PROMPT),
                  'config': config, 'config_sha256': config_digest, 'prerequisites': gates,
                  'request_utf8_bytes': request_bytes,
                  'provider_window_accounting': 'conservative UTF-8 byte admission bound; not provider tokenization',
                  'parameters': {'max_tokens': 2048, 'temperature': 0 if config['temperature_supported'] else None,
                                 'seed': 20261004 if config['seed_supported'] else None, 'sdk_max_retries': 0,
                                 'extra_body': config.get('extra_body')},
                  'attempts': [], 'generation_status': 'generation_failed', 'raw_answer': None,
                  'response_sha256': None, 'finish_reason': None, 'usage': None,
                  'usage_unavailable_reason': 'no response returned', 'finish_reason_unavailable_reason': 'no response returned'}
        def persist():
            record['record_sha256'] = sha({key: value for key, value in record.items() if key != 'record_sha256'})
            handle.seek(0)
            handle.write(canonical(record) + '\n')
            handle.truncate()
            handle.flush()
        persist()
        try:
            client = client if synthetic else _real_client(config)
            if client is None:
                raise ValueError('synthetic requires explicit synthetic client')
        except Exception as exc:
            record['construction_error_category'] = type(exc).__name__
            persist()
            raise ValueError('direct client configuration unavailable; inspect credential presence privately') from None
        for number in range(1, 4):
            start = time.perf_counter()
            attempt = {'number': number, 'started_at': datetime.now(timezone.utc).isoformat(),
                       'parameters': record['parameters'], 'response_id': None, 'usage': None}
            try:
                kwargs = {'seed': 20261004} if config['seed_supported'] else {}
                if config.get('extra_body'):
                    kwargs['extra_body'] = config['extra_body']
                message = await client.ainvoke(request, **kwargs)
                metadata = getattr(message, 'response_metadata', {}) or {}
                usage = getattr(message, 'usage_metadata', None) or metadata.get('token_usage') or metadata.get('usage')
                content = message.content
                # Preserve content blocks rather than flattening/rewriting the first raw answer.
                record.update(generation_status='returned', raw_answer=content,
                              response_sha256=sha(content), provider_response_metadata=metadata,
                              response_id=metadata.get('id'), sdk_message_id=getattr(message, 'id', None), usage=usage,
                              finish_reason=metadata.get('finish_reason', metadata.get('stop_reason')),
                              returned_model=metadata.get('model_name', metadata.get('model')))
                record['usage_unavailable_reason'] = None if usage is not None else 'provider SDK did not expose usage'
                record['finish_reason_unavailable_reason'] = None if record['finish_reason'] is not None else 'provider SDK did not expose finish reason'
                attempt.update(status='returned', response_id=record['response_id'], usage=usage,
                               provider_response_metadata=metadata, response_sha256=record['response_sha256'])
            except Exception as exc:
                attempt.update(status='technical_failure' if _technical(exc) else 'nonretryable_failure', error_category=type(exc).__name__)
            attempt['latency_seconds'] = time.perf_counter() - start
            record['attempts'].append(attempt)
            record['latency_seconds'] = sum(a['latency_seconds'] for a in record['attempts'])
            persist()
            if attempt['status'] != 'technical_failure':
                break
    return record


def exact_reuse(path, request_sha256, config_sha256, manifest_sha256, *, require_real=False):
    record = json.loads(Path(path).read_text(encoding='utf-8'))
    if require_real and record.get('record_kind') != 'real':
        raise ValueError('synthetic generation cannot be reused as real research')
    if record.get('record_sha256') != sha({key: value for key, value in record.items() if key != 'record_sha256'}):
        raise ValueError('reuse full saved record SHA mismatch')
    for key, expected in [('request_sha256', request_sha256), ('config_sha256', config_sha256), ('manifest_sha256', manifest_sha256)]:
        if record.get(key) != expected:
            raise ValueError('reuse provenance mismatch: ' + key)
    if sha(record['request']) != request_sha256 or sha(record['config']) != config_sha256:
        raise ValueError('reuse saved payload SHA mismatch')
    if record['generation_status'] == 'returned' and sha(record['raw_answer']) != record['response_sha256']:
        raise ValueError('reuse answer SHA mismatch')
    if record['prompt_sha256'] != sha(PROMPT) or sha(record['messages']) != record['messages_sha256']:
        raise ValueError('reuse frozen prompt/message SHA mismatch')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cell', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--prerequisites', required=True, type=Path)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    asyncio.run(run_cell(read(args.cell), read(args.config), args.manifest_sha256, args.output_dir,
                         prerequisites=read(args.prerequisites), preflight=args.preflight))


if __name__ == '__main__':
    main()
