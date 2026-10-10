"""Session 5B final freeze: <=3 complete configurations (incl. B0), 4K E5 inputs and the
E5 call plan. Model-free and network-free: it only builds the exact request bytes with
the frozen Layer 3 template, measures them, and records the plan. No generation.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from runtime import ROOT, sha, save_json, save_rows, load_queries, cache_identity

E1=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
E2=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-13'
CHAIN=ROOT/'outputs/pearl-chunking-chain-20261006'
ANSWER=ROOT/'experiments/pearl-answer-dev80-20261004'
L3OUT=ROOT/'outputs/pearl-answer-dev80-20261004-01'
L4=ROOT/'experiments/pearl-layer4-dev80-20261004'
L4OUT=ROOT/'outputs/pearl-layer4-dev80-20261004-01'
M0='C2-L384-O0-M0';M1='C2-L384-O0-M1';C3='C3-L256-O0-M0';B0='B0-regex320-overlap48-M0'
REPLICATES=('rep1','rep2','rep3')
MAX_TECHNICAL_RETRIES_PER_CELL=2
GLOBAL_RETRY_CAP=144

def load(p):return json.loads(Path(p).read_text('utf8'))
def jsonl(p):
    with Path(p).open(encoding='utf8') as f:return [json.loads(l) for l in f if l.strip()]
def rel(p):return Path(p).relative_to(ROOT).as_posix()

def generator_module():
    spec=importlib.util.spec_from_file_location('_pearl_answer_generate_frozen',ANSWER/'generate.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def index_dir(config):return (OUT if config==M1 else E1)/('index-'+config)
def ctx_path(config,B,panel='fixed_budget_main'):return (OUT if config==M1 else E3)/f'contexts-{config}-P0-{B}-{panel}.jsonl'

def final_configs(decision):
    primary=decision['selected'] if decision['status']=='frozen' else M0
    return [(primary,'primary_development_candidate'),(C3,'second_family_mechanism_control'),(B0,'baseline')]

def identity_record(config,role,scores,mapping_path,gen):
    d=index_dir(config);m=load(d/'manifest.json');binding=m['configuration']
    C,rest=config.split('-',1)
    rec=dict(configuration_id=config,role=role,boundary=config.split('-')[0],index_dir=rel(d),index_manifest_sha256=sha(d/'manifest.json'),child_chunks_sha256=sha(d/'child_chunks.jsonl'),
        rankings_sha256=sha(d/'rankings.jsonl'),source_view_sha256=binding['source'],table_snapshot_sha256=binding['table'],parent_graph_sha256=binding['parent'],calibration_sha256=binding['calibration'],
        tokenizer=binding['tokenizer'],lexical=binding['lexical'],retrieval=binding['retrieval'],models_sha256=binding['models'],recovery='P0',main_budget=4096,panel_id='fixed_budget_main',
        assembly_version='source-assembly-r01',serialization='[Source [[doc_id,source_version,element_id,start,end],...]]\\n<source text>, units joined by blank line; identical header format across configurations',
        contexts_4096_main=rel(ctx_path(config,4096)),contexts_4096_main_sha256=sha(ctx_path(config,4096)),contexts_8192_main_sha256=sha(ctx_path(config,8192)),
        support_map=rel(mapping_path),support_map_sha256=sha(mapping_path),prompt_sha256=gen.sha(gen.PROMPT),generator_config_sha256=sha(ANSWER/'generator-config-r01.json'))
    if config.startswith('B0'):rec.update(C='B0',L='regex320',O='legacy overlap48 (regex tokens)',M='M0',limitations=['E3 local recovery choice for B0 is pending_review (P1/P2 threats under r10 unknowns); B0 uses the common frozen P0 recovery as the reference arm.'])
    else:
        parts=config.split('-');rec.update(C=parts[0],L=int(parts[1][1:]),O=0.0,M=parts[3])
    if config==M1:rec['prefix']=dict(mode='M1',max_tokens=64,implementation='chunkers.render_prefix',retrieval_only=True)
    if config==C3:rec['limitations']=['E2 overlap choice pending_review (O0 is the existing identity, not an optimality claim)','E3 local recovery choice pending_review; common P0 used','E4 not run for C3 (M0 identity)']
    if config==M0 and role=='primary_development_candidate' and scores['decision']['status']!='frozen':rec['limitations']=['E4 M0/M1 choice pending_review; M0 is the existing identity, not an optimality claim']
    rec['layer1_2']=dict(layer2=[{k:r[k] for k in ('budget','panel_id','yes','no','unknown','complete_group_lower','complete_group_upper')} for r in scores['summary'] if r['configuration_id']==config],
        layer1=[{k:r[k] for k in ('method','k','yes','no','unknown','complete_mrr_lower','complete_mrr_upper')} for r in scores['layer1_summary'] if r['configuration_id']==config],cegr10=scores['cegr10'][config])
    rec['config_id']='cfg-'+cache_identity({k:rec[k] for k in ('configuration_id','index_manifest_sha256','child_chunks_sha256','rankings_sha256','source_view_sha256','table_snapshot_sha256','parent_graph_sha256','tokenizer','retrieval','recovery','main_budget','assembly_version','contexts_4096_main_sha256','support_map_sha256','prompt_sha256','generator_config_sha256')})[:24]
    return rec

def freeze(scores_path):
    scores=load(scores_path);mapping_path=ROOT/scores['mapping_path']
    if sha(mapping_path)!=scores['mapping_sha256']:raise ValueError('map drift')
    gen=generator_module();config=gen.validate_config(load(ANSWER/'generator-config-r01.json'))
    queries={q['intent_id']:q['query'] for q in load_queries(OUT/'queries.jsonl',80)}
    finals=final_configs(scores['decision']);records=[identity_record(c,role,scores,mapping_path,gen) for c,role in finals]
    # Exact 4K inputs and request bytes (frozen Layer 3 template, query + saved context only).
    requests=[];by_sha={}
    from smoke import counter
    c=counter()
    for rec in records:
        rows=jsonl(ctx_path(rec['configuration_id'],4096))
        if len(rows)!=80 or {r['intent_id'] for r in rows}!=set(queries):raise ValueError('4K context coverage')
        for r in sorted(rows,key=lambda x:x['intent_id']):
            text=r['final']['serialized_context']
            if c.count(text)!=r['final']['token_count'] or r['final']['token_count']>4096:raise ValueError('4K token recount mismatch')
            if not text:raise ValueError('empty context')
            cell=dict(query=queries[r['intent_id']],context=text);messages=gen.build_request(cell)
            nbytes=len(gen.canonical(messages).encode('utf-8'))
            if nbytes>config['provider_input_tokens']:raise ValueError('request exceeds frozen admission bound')
            rs=gen.sha(messages[0]['content']);first=by_sha.setdefault(rs,(rec['configuration_id'],r['intent_id']))
            requests.append(dict(configuration_id=rec['configuration_id'],config_id=rec['config_id'],intent_id=r['intent_id'],context_id=r['context_id'],context_sha256=gen.sha(text),
                context_bge_tokens=r['final']['token_count'],request_sha256=rs,messages_sha256=gen.sha(messages),request_utf8_bytes=nbytes,
                shares_request_with=None if first==(rec['configuration_id'],r['intent_id']) else dict(configuration_id=first[0],intent_id=first[1]),gold_or_reference_in_request=False))
    save_rows(OUT/'e5-request-inputs-r01.jsonl',requests)
    order=[];configs=[r['configuration_id'] for r in records];intents=sorted(queries)
    for rep in REPLICATES:
        for n,i in enumerate(intents):
            for k in range(len(configs)):
                cfg=configs[(n+k)%len(configs)];order.append(dict(cell_id=f'e5:{cfg}:{i}:{rep}',configuration_id=cfg,intent_id=i,replicate_id=rep))
    req={(r['configuration_id'],r['intent_id']):r for r in requests};provider=[]
    seen=set()
    for o in order:
        r=req[o['configuration_id'],o['intent_id']];key=(r['request_sha256'],o['replicate_id'])
        o['request_sha256']=r['request_sha256'];o['provider_call']=key not in seen
        if not o['provider_call']:o['reuses']='first cell with identical request bytes and the same replicate_id'
        seen.add(key)
    planned_calls=sum(o['provider_call'] for o in order)
    save_rows(OUT/'e5-cell-order-r01.jsonl',order)
    auth=load(CHAIN/'authorization-e5-r01.json')
    maxbytes=max(r['request_utf8_bytes'] for r in requests)
    plan=dict(stage='E5 call plan (frozen in Session 5B; execution belongs to 6A)',status='frozen',
        model=dict(protocol=config['protocol'],model=config['model'],base_url=config['base_url'],provider='DeepSeek (OpenAI-compatible API)',model_note='DeepSeek V4.1 Flash, user-specified for the PEARL Layer 3 run; 6A must verify availability and that the configured direct model equals this config before any call',
            generator_config=rel(ANSWER/'generator-config-r01.json'),generator_config_sha256=sha(ANSWER/'generator-config-r01.json'),generate_py_sha256=sha(ANSWER/'generate.py')),
        parameters=dict(max_tokens=2048,temperature=0,seed=None,seed_reason='provider does not declare seed support; not sent',extra_body=config.get('extra_body'),timeout_seconds=config['timeout_seconds'],sdk_max_retries=0,concurrency=1,
            thinking='disabled (nonthinking)'),
        prompt=dict(template_sha256=gen.sha(gen.PROMPT),historical_prompt_record=rel(L3OUT/'prompt-r01.json'),historical_prompt_record_sha256=sha(L3OUT/'prompt-r01.json'),fields=['query','exact_saved_context'],messages='single user message'),
        request_length=dict(admission_bound_utf8_bytes=config['provider_input_tokens'],admission_bound_definition='canonical JSON of the messages list, UTF-8 bytes; conservative bound below the 100000-token provider input limit, not provider tokenization',
            provider_window_tokens=config['provider_window_tokens'],output_reserve_tokens=2048,context_budget_bge_tokens=4096,max_request_utf8_bytes_planned=maxbytes,per_request_check='6A must recompute bytes of the exact messages before each call and refuse any request above the bound'),
        replicates=dict(ids=list(REPLICATES),definition='three independent real calls per unique (request bytes, replicate_id); identical full requests across configurations reuse the same three real records; a single response is never copied to fill a replicate'),
        request_cache=dict(key='sha256(canonical messages) + generator_config_sha256 + replicate_id',exact_reuse_only=True),
        interleaving=dict(rule='for replicate in rep1..rep3: for intent in sorted intent_id: configurations rotated by intent position (round-robin start)',cells_file=rel(OUT/'e5-cell-order-r01.jsonl'),cells_file_sha256=sha(OUT/'e5-cell-order-r01.jsonl')),
        retries=dict(technical_retries_per_cell_max=MAX_TECHNICAL_RETRIES_PER_CELL,attempts_per_cell_max=1+MAX_TECHNICAL_RETRIES_PER_CELL,retryable='connection, rate limit, timeout only; never on answer content',
            global_retry_cap=GLOBAL_RETRY_CAP,global_retry_cap_rule='stop remote calls and report blocked if total technical retries would exceed this cap'),
        calls=dict(logical_cells=len(order),planned_provider_calls=planned_calls,shared_request_cells=len(order)-planned_calls,planned_attempt_ceiling=planned_calls+min(GLOBAL_RETRY_CAP,planned_calls*MAX_TECHNICAL_RETRIES_PER_CELL)),
        authorization=dict(record=rel(CHAIN/'authorization-e5-r01.json'),record_sha256=sha(CHAIN/'authorization-e5-r01.json'),authorized_generation_max=720,authorized_retries='up to the cap frozen here (global_retry_cap)',
            monetary_cap=auth['monetary_cap'],within_authorization=planned_calls<=720),
        inputs=dict(request_inputs=rel(OUT/'e5-request-inputs-r01.jsonl'),request_inputs_sha256=sha(OUT/'e5-request-inputs-r01.jsonl'),queries=rel(OUT/'queries.jsonl'),queries_sha256=sha(OUT/'queries.jsonl'),
            configurations=[dict(configuration_id=r['configuration_id'],config_id=r['config_id'],contexts=r['contexts_4096_main'],contexts_sha256=r['contexts_4096_main_sha256']) for r in records],
            gold_and_references_excluded=True),
        not_allowed=['8K or any additional generation','E6 or new test set','legacy 200-question set','re-generation to tune configurations','scoring in 6A'])
    save_json(OUT/'e5-call-plan-r01.json',plan)
    evaluation=dict(status='frozen',layer3=dict(protocol=rel(ANSWER/'protocol.md'),protocol_sha256=sha(ANSWER/'protocol.md'),rubrics=rel(ANSWER/'rubrics.md'),rubrics_sha256=sha(ANSWER/'rubrics.md'),
            judge_prompt=rel(ANSWER/'judge-prompt-r01.md'),judge_prompt_sha256=sha(ANSWER/'judge-prompt-r01.md'),scoring_schema_sha256=sha(ANSWER/'scoring-schema.md'),score_py_sha256=sha(ANSWER/'score.py'),
            references=rel(L3OUT/'reference-freeze-r01.json'),references_sha256=sha(L3OUT/'reference-freeze-r01.json'),references_note='independent resolved Layer 3 references (80/80); built without seeing any answer; not in generation input'),
        layer4=dict(protocol=rel(L4/'protocol.md'),protocol_sha256=sha(L4/'protocol.md'),rubrics=rel(L4/'rubrics.md'),rubrics_sha256=sha(L4/'rubrics.md'),judge_prompt=rel(L4/'judge-prompt-r01.md'),judge_prompt_sha256=sha(L4/'judge-prompt-r01.md'),
            context_judge_addendum=rel(L4OUT/'calibration/context-judge-prompt-addendum-r02.json'),context_judge_addendum_sha256=sha(L4OUT/'calibration/context-judge-prompt-addendum-r02.json'),score_py_sha256=sha(L4/'score.py'),
            rule='Layer 4 reads the new answers and their actual E5 4K contexts; NA / no substantive claims never auto-score Faithfulness 100%'),
        layer1_2=dict(support_map=scores['mapping_path'],support_map_sha256=scores['mapping_sha256'],scores=rel(scores_path),scores_sha256=sha(scores_path)),
        statistics=dict(unit='intent; three replicates averaged within intent first',paired='stratified bootstrap 10000, seed 20261005, 95% interval; difference vs B0 per configuration',mcnemar='exact, only for binary panels without unknown'),
        judging=dict(identity='Agent reviewer roles as in the historical Layer 3/4 runs (blind packets hiding configuration identity and scores); model identity recorded per packet; human_verified recorded truthfully',
            units=dict(layer3_primary=len(order),layer3_secondary_fixed_sample=int(len(order)*0.2),layer3_adjudication_max=int(len(order)*0.1),layer4_tasks_per_answer=4,
                layer4_primary=len(order)*4,layer4_secondary_fixed_sample=int(len(order)*4*0.2),layer4_adjudication_max=int(len(order)*4*0.1)),
            judge_call_cap=None,exact_duplicate_rule='an answer packet byte-identical in (query, context, answer) to an already judged packet may reuse that judgment with a recorded binding',
            calibration='re-use frozen calibration anchors; a new judge identity must pass the historical anchor thresholds before research packets'))
    u=evaluation['judging']['units'];evaluation['judging']['judge_call_cap']=sum(v for k,v in u.items() if k!='layer4_tasks_per_answer')
    evaluation['judging']['judge_retry_cap']=dict(technical_retries_per_packet_max=2,global_cap=int(evaluation['judging']['judge_call_cap']*0.1))
    save_json(OUT/'evaluation-versions-r01.json',evaluation)
    save_json(OUT/'final-config-freeze-r01.json',dict(status='frozen',stage='5B final freeze',decision=scores['decision'],configurations=records,max_configurations=3,includes_B0=True,
        e5_allowed=True,e5_entry=rel(OUT/'e5-call-plan-r01.json'),evaluation_versions=rel(OUT/'evaluation-versions-r01.json'),rule=rel(OUT/'e4-prefix-selection-rule-r01.md'),rule_sha256=sha(OUT/'e4-prefix-selection-rule-r01.md'),
        scores=rel(scores_path),scores_sha256=sha(scores_path),human_verified=False,generation_calls=0,judge_calls=0))
    print(json.dumps(dict(configs=[(r['configuration_id'],r['config_id']) for r in records],planned_calls=planned_calls,cells=len(order),max_bytes=maxbytes,judge_cap=evaluation['judging']['judge_call_cap']),ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scores',type=Path,required=True);a=p.parse_args();freeze(a.scores.resolve())
