"""Exclusive run-local E1 packaging after actual execution and independent checks."""
import argparse
import json
import re
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from runtime import ROOT,EXP,sha,save_json
from e1 import configurations,verify_frozen,verify_input_copies

REUSED_FILES=(
    'build-cost.json','child_chunks.jsonl','chunk-profile.json','dense_ids.json',
    'dense_vectors.npy','fts.sqlite3','manifest.json','model_inputs.jsonl',
    'query-vectors.npy','rankings.jsonl','retrieval-audits.jsonl',
    'retrieval-cost.json','source-conservation.json','verification.json',
)
STATISTICS_RECEIPT='statistics-e1-r02.json'
TEST_COMMAND_RECEIPT='command-tests-r04.json'
TEST_CODE_SIDECAR='command-tests-r04-code-sha256.json'

def load(p):return json.loads(Path(p).read_text('utf8'))

def validate_stage(matrix,scores,verified):
    if matrix.get('status')!='passed' or matrix.get('configuration_count')!=13 or matrix.get('failed_configurations') or matrix.get('generation_calls')!=0:raise ValueError('full real E1 matrix required')
    if scores.get('details_count')!=22880 or len(scores.get('summaries',[]))!=286 or len(scores.get('execution',[]))!=13:raise ValueError('E1 score dimensions incomplete')
    if any(r['n']!=80 or r['failure_n'] for r in scores['summaries']):raise ValueError('score denominator/failure drift')
    if any(r['status']!='scored' or r['retrieved']!=80 or r['assembled']!=160 or r['retrieval_failed'] or r['assembly_failed'] for r in scores['execution']):raise ValueError('incomplete configuration cannot be sealed')
    if verified.get('status')!='passed' or any(verified.get(k)!=v for k,v in [('rankings',1040),('contexts',2080),('score_details',22880)]):raise ValueError('independent saved-output verification required')
    return True

def _resolved_mapping(output,scores):
    path=Path(scores.get('mapping_path',''))
    if not path.is_absolute():path=output/path
    return path.resolve()

def validate_analysis_receipts(output,config_ids,verified,scores,statistics,cases):
    """Bind statistics/cases to the exact verifier, score, map, and direct inputs."""
    verification_path=output/'verification-e1-r01.json';score_path=output/'scores-e1-r01.json';mapping_path=_resolved_mapping(output,scores)
    if mapping_path!=(output/'common-support-map-e1-r05.json').resolve():raise ValueError('packaging requires the current r05 scoring map')
    if not verification_path.is_file() or not score_path.is_file() or not mapping_path.is_file():raise ValueError('statistics/cases binding input missing')
    expected_common=dict(verification_receipt_sha256=sha(verification_path),score_file_sha256=sha(score_path),mapping_sha256=sha(mapping_path))
    if scores.get('mapping_sha256')!=expected_common['mapping_sha256'] or verified.get('score_file_sha256')!=expected_common['score_file_sha256'] or verified.get('mapping_sha256')!=expected_common['mapping_sha256']:raise ValueError('verification/score/map binding drift')
    for label,receipt in (('statistics',statistics),('cases',cases)):
        if receipt.get('status')!='completed' or any(receipt.get(k)!=v for k,v in expected_common.items()):raise ValueError(label+' verification/score/map binding drift')
        if receipt.get('generation_calls')!=0:raise ValueError(label+' generation-call drift')
    if any(statistics.get(k)!=0 for k in ('semantic_judgments_added','remote_model_calls','remote_judge_calls')):raise ValueError('statistics bootstrap metadata drift')
    if Path(statistics.get('mapping_path','')).resolve()!=mapping_path:raise ValueError('statistics mapping path drift')
    expected_configs=set(config_ids);checks=verified.get('checks',{})
    if set(checks)-{'E0_frozen_release'}!=expected_configs:raise ValueError('verifier configuration coverage drift')
    if 'E0_frozen_release' in checks and checks['E0_frozen_release'].get('status')!='passed':raise ValueError('E0 frozen verification incomplete')
    stat_bindings=statistics.get('score_detail_bindings',{})
    case_bindings=cases.get('verified_direct_artifact_bindings',{})
    if set(stat_bindings)!=expected_configs or set(case_bindings)!=expected_configs:raise ValueError('statistics/cases direct artifact configuration coverage drift')
    case_names={'score-details-e1-r01.jsonl','rankings.jsonl','contexts.jsonl'}
    for config in config_ids:
        verifier_hashes=checks[config].get('artifact_sha256',{})
        detail_hash=verifier_hashes.get('score-details-e1-r01.jsonl')
        if stat_bindings.get(config)!=detail_hash or not detail_hash:raise ValueError('statistics direct artifact binding drift '+config)
        if set(case_bindings.get(config,{}))!=case_names:raise ValueError('cases direct artifact set drift '+config)
        for name in case_names:
            expected=verifier_hashes.get(name);path=output/('index-'+config)/name
            if not expected or case_bindings[config].get(name)!=expected or not path.is_file() or sha(path)!=expected:raise ValueError('cases direct artifact binding drift '+config+'/'+name)
        detail_path=output/('index-'+config)/'score-details-e1-r01.jsonl'
        if not detail_path.is_file() or sha(detail_path)!=detail_hash:raise ValueError('statistics direct artifact binding drift '+config)
    auxiliary=cases.get('auxiliary_input_sha256',{})
    expected_aux={name:sha(output/name) for name in ('costs-e1-r01.json','chunk-profiles-e1-r01.json')}
    if auxiliary!=expected_aux:raise ValueError('cases auxiliary direct artifact binding drift')
    return True

def validate_reuse(output,attempt,root=ROOT):
    """Revalidate the one accepted same-session C1-L256 build/retrieval reuse."""
    receipt_path=output/'e1-current-run-cache-reuse.json';manifest_path=attempt/'attempt-delivery-manifest.json'
    receipt=load(receipt_path);manifest=load(manifest_path);config='C1-L256-O0-M0'
    expected_run=output.resolve().relative_to(Path(root).resolve()).as_posix()
    required_manifest={'status':'aborted_performance_restart','accepted_run':expected_run,'completed_real_configuration':config,'generation_calls':0,'historical_scores_loaded':False,'logical_rerank_pairs_completed':8000,'stored_contexts':160,'retained_partial_configuration':'C1-L384-O0-M0'}
    if any(manifest.get(k)!=v for k,v in required_manifest.items()):raise ValueError('retained attempt accepted-run/configuration/status drift')
    if manifest.get('artifact_count')!=len(manifest.get('artifacts_sha256',{})):raise ValueError('retained attempt manifest artifact count drift')
    expected_origin=(attempt/('index-'+config)).resolve()
    if receipt.get('configuration_id')!=config or Path(receipt.get('origin','')).resolve()!=expected_origin:raise ValueError('reuse receipt origin/configuration drift')
    if receipt.get('real_recorded_intents')!=80 or receipt.get('new_build_model_calls')!=0 or receipt.get('new_retrieval_model_calls')!=0:raise ValueError('reuse receipt count/model-call drift')
    copied=receipt.get('copied_sha256',{})
    if set(copied)!=set(REUSED_FILES):raise ValueError('reuse receipt copied file count/set drift')
    target=(output/('index-'+config)).resolve();artifacts=manifest['artifacts_sha256']
    for name in REUSED_FILES:
        source=expected_origin/name;accepted=target/name;key=source.relative_to(Path(root).resolve()).as_posix();expected=copied[name]
        if artifacts.get(key)!=expected or not source.is_file() or not accepted.is_file() or sha(source)!=expected or sha(accepted)!=expected:raise ValueError('reuse file hash drift '+name)
    copy_manifest=load(output/'input-copy-manifest.json')
    if copy_manifest.get('copied_sha256',{}).get(receipt_path.name)!=sha(receipt_path):raise ValueError('input-copy/reuse receipt binding drift')
    return dict(status='passed',configuration_id=config,files=len(copied),real_builds=1,retrieval_intents=80,logical_rerank_pairs_completed=manifest['logical_rerank_pairs_completed'],stored_contexts=manifest['stored_contexts'],receipt_sha256=sha(receipt_path),attempt_manifest_sha256=sha(manifest_path))

def validate_retrieval_and_zero_costs(config_ids,matrix,scores,verified,decision,statistics,cases,rerun,costs):
    """Gate the 104,000 fresh pairs and every claimed zero generation/API counter."""
    config_ids=list(config_ids);expected_pairs=len(config_ids)*80*100
    if expected_pairs!=104000:raise ValueError('E1 configuration arithmetic must equal 104000 reranker pairs')
    if rerun.get('status')!='passed':raise ValueError('passed independent retrieval verification required')
    totals=rerun.get('totals',{});records=rerun.get('configurations',[])
    if totals.get('configurations')!=len(config_ids) or totals.get('query_intents_per_configuration')!=80 or totals.get('R4_pairs_recomputed')!=104000:raise ValueError('fresh retrieval verification must total 104000 R4 pairs')
    if len(records)!=len(config_ids) or {r.get('configuration_id') for r in records}!=set(config_ids):raise ValueError('fresh retrieval configuration coverage drift')
    recomputed=0
    for row in records:
        r4=row.get('R4',{});recomputed+=r4.get('pairs_compared',-1)
        if r4.get('status')!='passed' or r4.get('queries')!=80 or r4.get('pairs_compared')!=8000:raise ValueError('fresh retrieval per-configuration pair count drift')
    if recomputed!=104000:raise ValueError('fresh retrieval configuration sum must equal 104000')
    provenance=rerun.get('provenance',{});rerun_cost=rerun.get('cost',{})
    zero_values=[matrix.get('generation_calls'),scores.get('generation_calls'),verified.get('generation_calls'),verified.get('remote_judge_calls'),decision.get('generation_calls'),statistics.get('generation_calls'),statistics.get('semantic_judgments_added'),statistics.get('remote_model_calls'),statistics.get('remote_judge_calls'),cases.get('generation_calls'),cases.get('semantic_judgments_added'),rerun_cost.get('generation_calls'),rerun_cost.get('remote_calls'),rerun_cost.get('dense_model_loads')]
    if any(value!=0 for value in zero_values) or any(provenance.get(k) is not False for k in ('historical_scores_loaded','gold_loaded','dense_model_loaded')):raise ValueError('generation/API/dense/historical zero-call provenance drift')
    if len(costs)!=len(config_ids) or {r.get('configuration_id') for r in costs}!=set(config_ids):raise ValueError('cost configuration coverage drift')
    for row in costs:
        if any(row.get(k)!=0 for k in ('generation_calls','remote_judge_calls','remote_model_calls')):raise ValueError('cost zero-call drift '+row.get('configuration_id',''))
        stages=row.get('stages',{})
        if set(stages)!={'build','retrieval','context'} or any(not isinstance(stages[name],dict) for name in stages):raise ValueError('cost stage coverage drift')
        if any(stages[name].get('generation_calls')!=0 for name in stages) or stages['build'].get('remote_calls')!=0 or stages['retrieval'].get('remote_calls')!=0:raise ValueError('stage cost zero-call drift '+row['configuration_id'])
    return dict(R4_pairs_recomputed=recomputed,generation_calls=0,external_model_api_calls=0,external_judge_api_calls=0)

def validate_supplemental_costs(output,config_ids,rerun,supplemental,scheduling,root=ROOT):
    supplemental_path=output/'supplemental-cost-accounting-e1-r01.json';scheduling_path=output/'verification-scheduling-e1.json';rerun_path=output/'independent-retrieval-verification-e1-r01.json'
    if not supplemental_path.is_file() or load(supplemental_path)!=supplemental or not scheduling_path.is_file() or load(scheduling_path)!=scheduling:raise ValueError('supplemental cost/scheduling receipt drift')
    verification=supplemental.get('verification',{});totals=rerun.get('totals',{})
    captured_sequences=sum(row.get('R4',{}).get('actual_forward_call_count',-1) for row in rerun.get('configurations',[]))
    expected_verification={'receipt':rerun_path.name,'receipt_sha256':sha(rerun_path),'logical_pairs':104000,'captured_forward_input_sequences_including_probes':captured_sequences,'additional_probe_input_sequences':totals.get('R4_adaptive_probe_repeat_forward_calls'),'actual_forward_input_tokens_including_probes':totals.get('R4_actual_forward_tokens_including_probe_repetitions'),'additional_probe_input_tokens':totals.get('R4_adaptive_probe_repeat_tokens')}
    if any(verification.get(k)!=v for k,v in expected_verification.items()):raise ValueError('supplemental verification accounting drift')
    primary=supplemental.get('primary_model_accounting',{})
    if primary.get('unique_query_encodings')!=1040 or primary.get('logical_reranker_pairs')!=104000:raise ValueError('supplemental primary model accounting drift')
    if any(supplemental.get(k)!=0 for k in ('generation_calls','external_model_api_calls','external_judge_api_calls')):raise ValueError('supplemental zero-call accounting drift')
    assembly=supplemental.get('context_assembly',{});probes=assembly.get('probes',[])
    if assembly.get('accepted')!=2080 or assembly.get('retained_original_attempt')!=160 or assembly.get('additional_equivalence_probe_batch_assemblies')!=12 or assembly.get('known_executed_total')!=2252 or sum(p.get('additional_batch_assemblies',-1) for p in probes)!=12:raise ValueError('supplemental context assembly accounting drift')
    for probe in probes:
        path=(Path(root)/probe.get('receipt','')).resolve()
        if not path.is_relative_to(Path(root).resolve()) or not path.is_file() or sha(path)!=probe.get('sha256'):raise ValueError('supplemental equivalence-probe receipt drift')
    events=scheduling.get('primary_retrieval_completion_events',[])
    if scheduling.get('status')!='recorded' or scheduling.get('primary_retrieval_completed_configurations')!=len(config_ids) or len(events)!=len(config_ids) or {e.get('configuration_id') for e in events}!=set(config_ids) or any(e.get('stage')!='retrieve' or e.get('status')!='completed' for e in events):raise ValueError('verification scheduling retrieval coverage drift')
    if scheduling.get('independent_verification_command')!='command-independent-retrieval-r01.json' or scheduling.get('concurrent_primary_stage')!='B0 P0 context assembly on CPU' or 'only after all primary GPU retrieval has completed' not in scheduling.get('GPU_concurrency',''):raise ValueError('verification scheduling chronology drift')
    return dict(status='passed',supplemental_cost_receipt=supplemental_path.name,supplemental_cost_receipt_sha256=sha(supplemental_path),verification_scheduling_receipt=scheduling_path.name,verification_scheduling_receipt_sha256=sha(scheduling_path),known_context_assemblies=assembly['known_executed_total'],captured_forward_input_sequences_including_probes=captured_sequences,additional_probe_input_sequences=verification['additional_probe_input_sequences'],actual_forward_input_tokens_including_probes=verification['actual_forward_input_tokens_including_probes'],additional_probe_input_tokens=verification['additional_probe_input_tokens'])

def validate_baseline_conservation(output):
    path=output/'index-B0-regex320-overlap48-M0'/'source-conservation.json';record=load(path);gaps=record.get('gaps',[])
    if record.get('status')!='baseline_legacy_gaps_recorded' or record.get('missing_characters',0)<=0 or record.get('duplicate_core_characters')!=0 or not gaps or any(g.get('reason')!='legacy_regex_boundary' for g in gaps):raise ValueError('B0 legacy core-gap disclosure/provenance drift')
    return dict(configuration_id='B0-regex320-overlap48-M0',status=record['status'],missing_core_characters=record['missing_characters'],gap_records=len(gaps),evaluated_visible_evidence='authenticated core_spans + overlap_spans',interpretation='Necessary legacy regex/overlap baseline; unlike C1-C4, core-only conservation has recorded boundary gaps by design.')

def experiment_code_hashes():
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(EXP.glob('*.py'))}

def write_test_code_sidecar(output,current_code=None):
    """Snapshot tested code after an exclusive successful final test receipt."""
    receipt_path=output/TEST_COMMAND_RECEIPT;tests=load(receipt_path)
    stdout=output/tests.get('stdout','');stderr=output/tests.get('stderr','')
    if tests.get('exit_code')!=0 or not stdout.is_file() or not stderr.is_file():raise ValueError('successful test receipt and logs required before code sidecar')
    matches=re.findall(r'(\d+) passed',stdout.read_text('utf8'))
    if not matches:raise ValueError('successful pytest count required before code sidecar')
    value=dict(schema_version='e1-test-code-hash-binding-v1',created_at_utc=datetime.now(timezone.utc).isoformat(),command_receipt=receipt_path.name,command_receipt_sha256=sha(receipt_path),stdout_sha256=sha(stdout),stderr_sha256=sha(stderr),tests_passed=int(matches[-1]),experiment_code_sha256=current_code if current_code is not None else experiment_code_hashes())
    save_json(output/TEST_CODE_SIDECAR,value)
    return value

def validate_test_receipt(output,tests,current_code):
    receipt_path=output/TEST_COMMAND_RECEIPT
    if load(receipt_path)!=tests or tests.get('exit_code')!=0:raise ValueError('fresh final experiment tests required')
    stdout=output/tests.get('stdout','');stderr=output/tests.get('stderr','')
    if not stdout.is_file() or not stderr.is_file():raise ValueError('test receipt logs missing')
    text=stdout.read_text('utf8');matches=re.findall(r'(\d+) passed',text)
    if not matches:raise ValueError('fresh final experiment tests required')
    sidecar=load(output/TEST_CODE_SIDECAR)
    if sidecar.get('schema_version')!='e1-test-code-hash-binding-v1' or sidecar.get('command_receipt')!=receipt_path.name or sidecar.get('command_receipt_sha256')!=sha(receipt_path):raise ValueError('test receipt/code sidecar binding drift')
    if sidecar.get('stdout_sha256')!=sha(stdout) or sidecar.get('stderr_sha256')!=sha(stderr):raise ValueError('test receipt log hash drift')
    if sidecar.get('tests_passed')!=int(matches[-1]):raise ValueError('test receipt count/sidecar drift')
    if sidecar.get('experiment_code_sha256')!=current_code:raise ValueError('test code hash snapshot/current code hash drift')
    return int(matches[-1])

def preservation(output,receipt):
    previous=ROOT/'outputs/pearl-chunking-dev80-20261005-02';e0=ROOT/'outputs/pearl-chunking-dev80-20261005-03'
    collections={'E0_delivery':load(e0/'delivery-manifest.json')['artifacts_sha256'],'historical_protected':load(previous/'protected-assets-sha256.json'),'assets':{p:a['sha256'] for p,a in load(previous/'asset-audit.json')['assets'].items()},'legacy_code':load(previous/'workspace-baseline.json')['code_sha256']}
    checks={}
    for name,files in collections.items():
        drift=[p for p,h in files.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
        checks[name]=dict(count=len(files),drift=drift)
        if drift:raise ValueError('preservation drift '+name+repr(drift))
    save_json(receipt,dict(status='passed',checks=checks,sealed200_access='byte-hash only; no question content loaded',navigation_modified_in_E1=False))
    print('E1 preservation passed',flush=True)

def package(output):
    e0=ROOT/'outputs/pearl-chunking-dev80-20261005-03';attempt=ROOT/'outputs/pearl-chunking-dev80-20261005-04'
    for name in ('handoff.md','reproduction_commands_e1.md','delivery-manifest.json','workspace-final-e1.json','command-ledger-e1.json','budget-e1.json'):
        if (output/name).exists():raise FileExistsError('exclusive E1 delivery targets required: '+name)
    verify_frozen(e0/'delivery-manifest.json');verify_input_copies(e0,output)
    matrix=load(output/'matrix-completion-e1.json');scores=load(output/'scores-e1-r01.json');verified=load(output/'verification-e1-r01.json');validate_stage(matrix,scores,verified)
    checks=[load(output/name) for name in ('preservation-e1-final-r01.json','source-review-integration-r05.json','independent-retrieval-verification-e1-r01.json')]
    if any(r['status']!='passed' for r in checks):raise ValueError('E1 preservation/source/retrieval gates incomplete')
    config_ids=list(configurations());statistics=load(output/STATISTICS_RECEIPT);cases=load(output/'case-inventory-e1-r01.json')
    validate_analysis_receipts(output,config_ids,verified,scores,statistics,cases)
    reuse=validate_reuse(output,attempt)
    decision=load(output/'candidate-selection-e1-r01.json')
    if len(decision['selected'])>2 or decision['status'] not in ('frozen','pending_unknown'):raise ValueError('invalid E1 candidate boundary')
    if verified['candidate_selection_sha256']!=sha(output/'candidate-selection-e1-r01.json'):raise ValueError('verified candidate selection drift')
    for config in config_ids:
        for name,h in verified['checks'][config]['artifact_sha256'].items():
            if sha(output/('index-'+config)/name)!=h:raise ValueError('post-verification direct-input drift')
    costs=load(output/'costs-e1-r01.json');profiles=load(output/'chunk-profiles-e1-r01.json');rerun=load(output/'independent-retrieval-verification-e1-r01.json')
    zero_costs=validate_retrieval_and_zero_costs(config_ids,matrix,scores,verified,decision,statistics,cases,rerun,costs)
    supplemental=load(output/'supplemental-cost-accounting-e1-r01.json');scheduling=load(output/'verification-scheduling-e1.json');supplemental_costs=validate_supplemental_costs(output,config_ids,rerun,supplemental,scheduling)
    baseline_disclosure=validate_baseline_conservation(output)
    code=experiment_code_hashes();tests=load(output/TEST_COMMAND_RECEIPT);test_count=validate_test_receipt(output,tests,code)
    commands=[]
    for p in sorted(output.glob('command-*.json')):
        commands.append(dict(receipt=p.name,receipt_sha256=sha(p),**load(p)))
    save_json(output/'command-ledger-e1.json',dict(commands=commands,external_post_freeze_envelopes=['command-package-r02.json','command-package-r02.stdout.log','command-package-r02.stderr.log','delivery-verification-e1-r01.json'],retained_attempt_manifest_sha256=sha(attempt/'attempt-delivery-manifest.json')))
    save_json(output/'workspace-final-e1.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),status_porcelain=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),experiment_code_sha256=code,commit_push_merge_performed=False))
    budget=dict(generation_calls=zero_costs['generation_calls'],external_model_api_calls=zero_costs['external_model_api_calls'],external_judge_api_calls=zero_costs['external_judge_api_calls'],historical_scores_loaded=False,primary_unique_query_encodings=1040,primary_logical_reranker_pairs=104000,verification_logical_reranker_pairs=zero_costs['R4_pairs_recomputed'],accepted_contexts=2080,retained_discarded_stored_contexts=reuse['stored_contexts'],reused_current_session_real_builds=reuse['real_builds'],reused_current_session_real_retrieval_intents=reuse['retrieval_intents'],reuse_verification=reuse,baseline_core_conservation=baseline_disclosure,supplemental_cost_accounting=supplemental_costs,semantic_calibration_reused=True,new_semantic_calibration_model_calls=0,independent_source_review=dict(new_intents=72,new_bundles=119,accepted_deliverables=2,model='gpt-5.6-sol',tokens=None,monetary_cost=None,scope='In-app agent semantic QA is separate from experiment external API calls; internal calls/tokens and cost were not measured.'),discarded_partial_dense_build=dict(confirmed_logical_passages_at_least=776,exact_forward_rows_and_cost=None,receipt='../pearl-chunking-dev80-20261005-04/attempt-delivery-manifest.json'),local_gpu=dict(device=load(output/'runtime-environment-e1.json')['device_name'],energy=None,monetary_cost=None),latency_definition='Per-query measured R4 retrieval time excludes audit/capture overhead and answer generation. B0 context assembly overlapped only with the independent verifier after all primary GPU retrieval completed; see verification-scheduling-e1.json. Separate stages are not added into an end-to-end answer latency.',primary_cost_file_sha256=sha(output/'costs-e1-r01.json'),verification_cost_receipt_sha256=sha(output/'independent-retrieval-verification-e1-r01.json'))
    save_json(output/'budget-e1.json',budget)
    lookup={(r['configuration_id'],r['cell']):r for r in scores['summaries']};rows=[]
    for p in profiles:
        config=p['configuration_id'];a=lookup[config,'fixed_budget_main/P0/4096/final'];b=lookup[config,'fixed_budget_main/P0/8192/final'];r=lookup[config,'layer1_raw/R4/10']
        rows.append(f"| {config} | {p['children']} | {a['yes']}/80; u={a['unknown']} | {b['yes']}/80; u={b['unknown']} | {r['yes']}/80; u={r['unknown']} |")
    unknown4=sum(lookup[c,'fixed_budget_main/P0/4096/final']['unknown'] for c in configurations());unknown8=sum(lookup[c,'fixed_budget_main/P0/8192/final']['unknown'] for c in configurations())
    status='E1_matrix_complete_selection_pending' if decision['status']=='pending_unknown' else 'E1_complete_candidates_frozen'
    next_text='同一 E1 范围内按实际可见正文审查能改变候选入选的 unknown，再以新 map/run 版本重算全部受影响配置；候选冻结前不进入 E3。' if decision['status']=='pending_unknown' else '另行授权 Session 4 E3；先校验本交付 manifest 和同索引 R4 排名身份。'
    handoff=f'''# Session 3 E1 交接

*真实索引、80题检索与 Layer 1–2 开发评价 · status: current · 2026-10-05*

本阶段状态 `{status}`。E0 的 160 个冻结产物及保存输出、来源、表格、父图和 C4 校准已重新核验通过。C1–C4×256/384/512（O0/M0）和必要 B0 共 13 套真实独立索引、1040 个意图×配置、4160 个方法单元、2080 份 P0 Top100 4096/8192 上下文、22880 个评分明细及 286 个主表单元均已完成并核验。独立样本仍为 80 个 intent，技术失败为 0。{test_count} 个实验测试通过。

实际索引使用英文 FTS5/BM25 和真实 BGE-M3 unit vectors 的 exact float32 dot search；RRF k=60、Top100 与冻结 BGE reranker。所有配置保存完整 R1/R2/RRF union/R3/R4、实际模型输入、来源守恒与正文/表格长度画像。独立核验重新查询全部 BM25，并真实重算全部 104000 个 R4 pair；从保存 dense vectors 独立复算 R2，重开实际文本核验预算、顺序、去重、逐字符最大前缀、截断 trace 与全部评分算术。

来源图 r05 使用 E0 的 8 个来源证书和本阶段独立盲审的另 72 个意图/119 个证据 bundle。保守必要范围未完整可见即 unknown；缺少证书不能机械判 no。4K 主面板有 {unknown4}/1040 个 unknown，8K 有 {unknown8}/1040 个 unknown。下表数字是已证实完整的题数；u 是未知数，可能上界另存，不能当作成绩或置信区间。

B0 是必要的 legacy regex/overlap 基线。它的 core-only 来源守恒按设计保留 {baseline_disclosure['missing_core_characters']} 个边界缺口（{baseline_disclosure['gap_records']} 条 `legacy_regex_boundary` 记录），不具备 C1–C4 的无缺口 core 分区保证；实际评价的可见证据使用已认证的 `core_spans + overlap_spans`。

| 配置 | child | 4K CGC yes / unknown | 8K CGC yes / unknown | R4 CEGR@10 yes / unknown |
| --- | ---: | --- | --- | --- |
'''+ '\n'.join(rows)+f'''

候选状态 `{decision['status']}`；冻结候选 `{decision['selected']}`，保留 `{decision['baseline_retained']}`。暂定下界顺序为 `{decision['provisional_lower_bound_order']}`，不宣称确定获胜。排序依次为 4K CGC、R4 CEGR@10、真实检索均时和 config_id；unknown 能改变入选时保持 pending。等价合并还核验实际排名与两预算上下文合同，没有借用旧方法分数。

交付入口：[13行比较表](comparison-e1-r01.csv)、[完整主表](main-table-e1-r01.csv)、[逐题表](per-intent-table-e1-r01.csv)、[逐题 unknown 来源缺口](unknown-evidence-e1-r01.jsonl)、[预算转换](budget-transitions-e1-r01.csv)、[配对统计](statistics-e1-r02.json)、[成本](costs-e1-r01.json)、[补充成本账](supplemental-cost-accounting-e1-r01.json)、[验证调度](verification-scheduling-e1.json)、[预算账本](budget-e1.json)、[候选判定](candidate-selection-e1-r01.json)、[保存输出核验](verification-e1-r01.json)、[真实重排复验](independent-retrieval-verification-e1-r01.json)、[重现命令](reproduction_commands_e1.md)、[交付 SHA 清单](delivery-manifest.json)。各 `index-<config>/score-details-e1-r01.jsonl` 保存逐前缀要求/AND–OR 证据，`contexts.jsonl` 保存四阶段真实全文与来源区间。

首次 -04 尝试因等价批量计数优化而中止，所有产物已[封存](../pearl-chunking-dev80-20261005-04/attempt-delivery-manifest.json)。仅该次完整 C1-256 的当前会话真实建库与检索按字节复用；其上下文重新组装，未完成 C1-384 建库不计为完整索引。早期来源审查草稿与 r04 图保留，正式结果绑定最终审查 r05。未改解析器、检索模型、生成提示、历史输出或旧200题内容；保护资产复核无漂移。

答案生成为 0，实验外部模型/裁判 API 调用为 0。真实本地 GPU 建库、检索和复验成本分别记录；Agent 语义审查的内部 token/费用、本地电耗与货币费率未测量，均为 null。阶段耗时不拼接成端到端回答延迟。本结果按当前研究验收标准为正式 Agent 开发评价；unknown 与候选未决如实保留，历史 human_verified 标签不改写。

下一入口：{next_text} 本次到 E1 交付后停止，E2/E3/E4/E5、答案生成和旧200评价均未启动。未 commit/push/merge。
'''
    with (output/'handoff.md').open('x',encoding='utf8',newline='\n') as f:f.write(handoff)
    reproduction='# E1 真实命令与复算入口\n\n*Session 3 实际执行记录 · status: current · 2026-10-05*\n\n从仓库根运行，使用 `.venv\\Scripts\\python`，设置 `PYTHONPATH=Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src` 和 `PYTHONIOENCODING=utf-8`。所有结果目标采用新文件名；相同路径不会覆盖。原始执行日志与退出码见 [command ledger](command-ledger-e1.json)。矩阵命令只生成索引、检索与上下文，评分只消费离线来源图。\n\n'
    for command in commands:
        reproduction+=f"- [{command['receipt']}]({command['receipt']}), exit_code={command.get('exit_code')}: `{' '.join(command.get('argv',[]))}`\n"
    reproduction+='\n完全重跑需新 run 目录，按 [input-copy manifest](input-copy-manifest.json) 复制并核验冻结 E0 公共资产和严格 query-only 80 题，运行 `e1_fast.py --e0 <E0> --output <new-run>`；仅本次严格当前会话复用时才指定 `--reuse-first`。来源审查及正式 map r05 同步版本化；随后依照上述成功命令执行 score → independent retrieval verification → saved-output verification → statistics/cases → preservation → package。新复算 receipt 同样采用新名字。后续 session 必须先核对交付 SHA；不能把本表套给不同配置、排名或上下文。\n'
    with (output/'reproduction_commands_e1.md').open('x',encoding='utf8',newline='\n') as f:f.write(reproduction)
    excluded={'delivery-manifest.json','command-package-r02.json','command-package-r02.stdout.log','command-package-r02.stderr.log','delivery-verification-e1-r01.json'}
    paths={p for p in output.rglob('*') if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts}|set(EXP.glob('*.py'))|{EXP/'protocol.md',EXP/'resolved_manifest_session2.yaml',attempt/'attempt-delivery-manifest.json',e0/'delivery-manifest.json'}
    artifacts={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}
    save_json(output/'delivery-manifest.json',dict(schema_version='pearl-chunking-e1-delivery-v1',stage='Session 3 E1',status=status,created_at_utc=datetime.now(timezone.utc).isoformat(),artifact_count=len(artifacts),artifacts_sha256=artifacts,inputs=dict(E0_manifest_sha256=sha(e0/'delivery-manifest.json'),query_sha256=sha(output/'queries.jsonl'),mapping_sha256=scores['mapping_sha256'],phase_code_sha256=matrix['phase_code_sha256']),counts=dict(configurations=13,retrieved=1040,method_cells=4160,contexts=2080,score_details=22880,summary_cells=286,independent_intents=80,failed=0,CGC4K_unknown=unknown4,CGC8K_unknown=unknown8,tests_passed=test_count),decisions=decision,budget=budget,next=next_text,formal_agent_development_result=True,historical_labels_preserved=True,external_post_freeze_envelopes=['command-package-r02.json','command-package-r02.stdout.log','command-package-r02.stderr.log','delivery-verification-e1-r01.json']))
    print('E1 sealed',status,'artifacts',len(artifacts),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage',choices=['preserve','test-code-sidecar','package']);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--receipt',type=Path);args=parser.parse_args()
    if args.stage=='preserve':
        if args.receipt is None:parser.error('--receipt required for preservation')
        preservation(args.output.resolve(),args.receipt.resolve())
    elif args.stage=='test-code-sidecar':
        value=write_test_code_sidecar(args.output.resolve());print('saved',TEST_CODE_SIDECAR,'tests',value['tests_passed'],flush=True)
    else:package(args.output.resolve())
