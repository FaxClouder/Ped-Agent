"""Package already-observed Session 1 audit facts; no experiment execution."""
import hashlib
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
EXP=Path(__file__).resolve().parent
OUT=ROOT/'outputs/pearl-chunking-dev80-20261005-02'
def read(p):return json.loads(p.read_text('utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:
        f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def ref(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))

audit=read(OUT/'asset-audit.json');base=read(OUT/'workspace-baseline.json')
corpus=read(OUT/'source-registry-corpus.json')
literature=[json.loads(s) for s in (ROOT/'paper/RAG_Report/literature.jsonl').read_text('utf-8').splitlines()]
aliases={'Semantic-Chunking':'PDF pp.1-3, sections 2 and opening of 3',
         'Dense-X':'PDF pp.1-3, section 2 and opening of 3',
         'Complex-Chunking-2026':'PDF pp.1-3, Table 1, sections 2 and 3.1-3.3 opening',
         'Late-Chunking':'PDF pp.1-2, abstract/introduction/Figure 1'}
papers=[]
for row in literature:
    if row['alias'] not in aliases:continue
    record={k:row.get(k) for k in ('record_id','alias','title','frozen_url','version','pdf_sha256')}
    record.update(accessed_date='2026-10-05',read_range=aliases[row['alias']],replicated=False)
    for key in ('pdf_path','source_snapshot'):
        p=ROOT/'paper/RAG_Report'/row[key]
        record[key]=ref(p)
    record['pdf_hash_matches_registry']=record['pdf_path']['sha256']==row['pdf_sha256']
    record['reading_text']=ref(ROOT/'paper/RAG_Report/reading_text'/f"{row['alias']}.txt")
    papers.append(record)
docs=read(OUT/'primary-doc-fetch.json')
for d in docs:
    d['read_range']={'parent':'class description and child/parent splitter fields',
        'recursive':'introduction, separator list, length/overlap example',
        'window':'redirected overview only; not accepted as window evidence',
        'contextual':'browser-verified Introducing/Implementing/Methodology/Reranking; HTTP snapshot unavailable'}[d['id']]
    if d['id']=='window':d['status']='redirected_to_unrelated_overview'
    if d['id']=='contextual':d['browser_verified']=True
docs.append(dict(id='window_source',**read(OUT/'window-source-record.json'),
    read_range='class docstring/defaults plus build_window_nodes_from_documents',replicated=False))
registry=dict(schema_version='pearl-chunking-source-registry-v1',status='audit_ready_smoke_pending',
    corpus_manifest=ref(ROOT/'paper/pearl-framework/datasets/retrieval-corpus/corpus-manifest-v02.jsonl'),
    source_count=106,sources=corpus['sources'],research=dict(seed_registry=ref(ROOT/'paper/RAG_Report/literature.jsonl'),
    papers=papers,official_docs=docs),new_source_view=None,new_support_map=None,
    coordinate_contract='canonical element Unicode half-open; PDF character alignment not established')
write(EXP/'source_registry.json',registry)

assets=audit['assets'];b=read(OUT/'legacy-policy-reconstruction.json')
config_files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted((ROOT/'Knowledge-Base/config').rglob('*')) if p.is_file()}
manifest=dict(schema_version='pearl-chunking-session1-resolved-v1',stage='Session 1 R0 and E0 asset/protocol audit',
    protocol_status='protocol_ready',e0_status='audit_ready_smoke_pending',formal_run_allowed=False,
    experiment_root=EXP.relative_to(ROOT).as_posix(),audit_run_id=OUT.name,
    workspace=dict(commit=base['commit'],branch=base['branch'],dirty_snapshot=ref(OUT/'workspace-baseline.json'),
        code_hash_count=len(base['code_sha256']),configuration_sha256=config_files),
    user_draft=base['user_draft'],inputs={role:[a for a in assets.values() if a['role']==role] for role in
        ('corpus_manifest','query_only_dev80','development_gold','legacy_support_map','independent_answer_reference','answer_frozen_configuration')},
    corpus_registry=ref(EXP/'source_registry.json'),asset_audit=ref(OUT/'asset-audit.json'),
    h0=dict(policy=b['policy'],tokenizer=b['tokenizer'],exact_ids_and_text_reconstructed=b['all_exact'],
        child_count=6433,parent_count=2830,heading_injection='render_elements prepends heading_path then element text; heading may repeat',
        tables='ordinary grouped elements; no special table barrier in HierarchicalChunker',
        source_offsets='character_start/end relative to historical parent, not canonical element',
        evidence=dict(seed_depth=10,dedup='unit_id only',serialized_budget_count=True,private_parent=True)),
    b0=dict(boundary='parent-child-v1 regex window within old element/heading grouping logic adapted to public source/table view',
        length_unit='regex-token-v1',parent_target=1200,parent_max=1800,child_window=320,child_max=450,overlap=48,
        note='450 is policy max; actual regex window min(320,450)=320; not 320 BGE tokens',
        tables='common snapshot; old table treatment replaced explicitly',prefix='M0',recovery='public P0/P1/P2',
        equivalence_to_c1=False,adapter_code_sha256=None),
    retrieval=dict(method_configuration=audit['legacy_retrieval'],depth_per_route=100,rrf_k=60,equal_weights=True,
        dense_scoring='exact float32 dot product of stored normalized vectors; tie chunk_id',
        index_storage='independent FTS/vector files; Chroma storage available, not ANN primary scoring',
        model_asset_checks=[a for a in assets.values() if a['role'] in {'dense_model','reranker_model','reranker_config'}],
        current_execution_verified=False,seed=20260929),
    scientific=dict(core_lengths=[256,384,512],core_tokenizer='BGE-M3 tokenizer.json SHA in model asset checks',
        c4=dict(distance='1-cosine',percentile=90,quantile_method='linear',min_core_fraction=.5,threshold=None,
            sentence_splitter_sha256=None,calibration_labels_allowed=False),
        overlaps=[0,.1,.2],prefix_max_tokens=64,prefix_allocation_rule=None,parent_max_tokens=1536,
        budgets=[4096,8192],panels=['layer1_raw','fixed_budget_main','seed10_diagnostic'],
        candidate_order=['4K CGC certain completeness descending','CEGR@10 descending','retrieval latency ascending','config_id ascending'],
        max_candidates=2,bootstrap_repeats=10000,statistics_seed=20261005,unit='intent'),
    unresolved=dict(source_view_sha256=None,table_snapshot_sha256=None,table_split_config=None,
        public_parent_graph_sha256=None,common_source_support_map_sha256=None,smoke_intent_ids=None,
        new_cli_commands=None,new_model_forward_evidence=None,current_generator_model=None,
        current_provider_capabilities=None,current_judge_model=None,current_judge_call_cap=None),
    generation=dict(historical_config=ref(ROOT/'experiments/pearl-answer-dev80-20261004/generator-config-r01.json'),
        historical_prompt=ref(ROOT/'outputs/pearl-answer-dev80-20261004-01/prompt-r01.json'),
        use_historical_model_without_preflight=False,replicates=3,planned_max_answers=720,
        max_attempts_per_request=3,sdk_retries=0,concurrency=1,planned_attempt_ceiling=2160,
        authorization_evidence=None,authorized_call_ceiling=None,authorized_cost_ceiling=None,
        authorized_judge_ceiling=None,actual_generation_calls=0,actual_judge_calls=0,actual_remote_model_calls=0,
        policy='No authorization found for this chunking round; only dependent remote calls paused.'),
    blockers=[dict(id='G1',scope='affected formal comparisons',reason='119 unique atom location candidates; 55 non-exact anchors across 39 intents need source/semantic audit; 261/573 legacy excerpts not unique element matches. No new common support map adjudicated.'),
        dict(id='G2',scope='index and assembly',reason='Public source view/table/parent graph and reversible offsets unbuilt; B0 adapter unbuilt.'),
        dict(id='G3',scope='C4 and M1',reason='Sentence splitter identity/C4 measured threshold and prefix allocation unresolved; freeze before results.'),
        dict(id='G4',scope='E0 completion and E1',reason='Real 5-8 intent smoke and saved-output independent verification pending Session 2.'),
        dict(id='G5',scope='remote generation/judging only',reason='Round-specific authorization/current capabilities/actual judge model and cap unavailable.')],
    prohibited=['full index build','E1','answer generation','eval200 content for development','historical output modification'])
write(EXP/'resolved_manifest.yaml',yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False))

inventory='''# Session 1 资产与实现审计

*真实只读核验结果与待适配边界 · status: current · 2026-10-05*

## 保存身份

commit：`{commit}`；分支`{branch}`。现有dirty工作区保持，相关代码SHA逐项保存在[baseline](../../outputs/pearl-chunking-dev80-20261005-02/workspace-baseline.json)。本阶段仅新增审计/文档，更新维护导航；没有实现chunker、index或运行时adapter。

| 资产 | 实际数量/核验 | 机器证据 |
| --- | --- | --- |
| 原稿 | D:/GoogleDownload原稿存在，SHA与策略方案一致 | baseline.user_draft |
| 语料 | 106 PDF/106 canonical/106 Adobe ZIP；PDF及canonical声明SHA吻合 | [source registry](source_registry.json)含各路径及SHA |
| 派生/模型/索引输入 | 1683项记录，无缺失、无声明SHA不符 | [asset audit](../../outputs/pearl-chunking-dev80-20261005-02/asset-audit.json) |
| H0 child/parent | 6433/2830；offset、containment、parent重建均6433/6433；当前默认实现重建106源所有ID与正文相同 | [policy reconstruction](../../outputs/pearl-chunking-dev80-20261005-02/legacy-policy-reconstruction.json) |
| dev80/Gold r02 | 查询80与Gold query/intent逐项相同；4类各20；r02 SHA 7f64ac4559fbf604c0d4d6aca81e23685f1dcbf009853ee3c8637dc368ad29f5 | resolved_manifest inputs |
| 原support map | analysis-r02-01/support-map.json，绑定原chunk、Gold与真实path_evidence | asset audit与下面迁移分级 |
| 独立答案参考 | reference-freeze-r01.json含80 resolved参考，intent集合一致；不直接以旧答案作为新输出 | resolved_manifest inputs；旧参考/候选包纳入protected哈希 |
| 历史保护 | 10335文件字节SHA，包括H0和Layer1–4、旧eval200结果；Chroma物理文件排除且不打开数据库 | [protected hashes](../../outputs/pearl-chunking-dev80-20261005-02/protected-assets-sha256.json) |
| 旧200身份 | 仅读C/D发布报告与四层汇总，未反序列化题目/Gold/排名用于开发；保护中只读字节hash | [C/D入口](../pearl-retrieval-eval200-20261003/README.md)；原独立评价身份保留，今后仅已暴露回归 |

模型权重及配置已hash，不代表本阶段加载GPU或执行真实forward。真实检索和语义支持审查未运行。

## Gold跨切片追溯的三类

174 atoms的119个有唯一canonical元素文本定位候选；55个无精确元素锚点，涉及39 intents。0个atom的source缺失。这是位置审计，不是119个已完成语义迁移。页码优先选锚点、记录所有匹配，source版本严格固定。[逐原子明细](../../outputs/pearl-chunking-dev80-20261005-02/gold-location-audit.json)保留未决。

573个历史实际支持引文全部在原child中；312可唯一精确定位到canonical元素，261需跨元素/规范化/重复歧义追溯与语义审查。[r02引文明细](../../outputs/pearl-chunking-dev80-20261005-02/legacy-support-location-audit-r02.json)枚举全部出现位置；r01保留为早期定位快照，不作最终唯一性依据。

| 类别 | 当前判定 | Session 2处理 |
| --- | --- | --- |
| 可确定性迁移候选 | 版本/hash、历史parent offsets、精确引文位置可恢复；完整支持范围尚未冻结 | 构建reversible span map后，只有实际保留全部已核验支持范围才能继承；短anchor/quote单独不能证明条件完整 |
| 需语义审查 | 55非精确anchors、261非唯一元素excerpt定位；新切片/联合文本及截尾 | 对真实来源与需求读全文，保留三值；逐题登记受影响requirements/组，不关键词赋true |
| 无法恢复 | 当前source缺失0；不能据此称完整锚点恢复成功 | 若源损坏/支持范围无法回映，登记source_unrecoverable并阻止受影响正式比较，不能偷偷排除题目 |

Layer2 raw与Retrieval r02已有不同审查视图；本轮必须构建共同map，不能混用较高历史标签。39意图是位置审计优先清单，不等于确定失败或可以删除的分母。

## H0/B0逐项差异

| 项 | H0实际实现 | B0公共协议与适配 |
| --- | --- | --- |
| 正文长度 | RegexTokenCounter，窗口min(320,450)=320、overlap48；parent target1200/max1800；不是BGE长度；超长元素可超过parent max | 保留真实正则方法/overlap，但转到公共source view；与C1 BGE O0不等价，B0不是纯边界对照 |
| 表格 | ordinary element参与父分组及文本窗口，无屏障/公共cell snapshot | 公共独立table snapshot，对全部配置相同；表格分组参数待冻结 |
| 标题/前缀 | _render_elements注入heading_path，正文元素还可能包含heading；sparse额外title/heading字段为空 | 正文标题一次、M0无额外prefix；M1仅原文结构，检索表示与支持正文分开 |
| 父图 | child依赖历史parent分组、每child一个parent | 构建独立公共parent≤1536 BGE，P2多父；B0不私用H0父恢复 |
| 候选 | R1/R2 depth100、RRF60、R4 rerank100，固定旧索引路径/6433/80校验 | 相同参数，动态新chunk数、新索引、新排名，不改模型帮助chunker |
| 去重 | Evidence unit_id去重，child重叠仍可重复 | 版本化来源span/cell并集，跨文献同句不去重 |
| 预算 | serialize包含Source/locator/Title，BGE count；首次溢出字符二分截尾并停止 | 复用完整计量，新增可逆截断和最大合法prefix验证；并非新增预算计数 |
| 面板 | 固定Top10 raw/expanded/final | 新Top100 fixed-budget主面板，保留Top10诊断，panel独立 |
| 支持/评分 | r02 atom_paths绑定旧chunk；Evidence三值实际正文审查 | 共同source support图、同AND/OR逻辑、实际final审查；旧映射不直接跨切片复用 |

## 参数与授权缺口

真实检索配置、权重SHA、revision、seed、tokenizer已解析，具体在[resolved manifest](resolved_manifest.yaml)。公共来源视图、表格行组/超长cell、公共父图、共同支持图、C4分句器/实测阈值、M1配额与实际CLI为null。不是自动猜测值，也不能用脚手架替代。

旧Layer3记录的deepseek-flash、nonthinking、temperature0、输出2048、timeout120仅历史配置线索。本轮当前provider/judge能力和调用授权未知；本轮实际生成/裁判/API模型调用0。最多720答案是后续计划，不是授权额度。无需因此暂停独立本地Session2工作。
'''.format(commit=base['commit'],branch=base['branch'])
write(EXP/'inventory.md',inventory)
write(EXP/'README.md','''# PEARL 切片开发研究：Session 1交付

*策略研究与E0资产/协议审计 · status: current · 2026-10-05*

Session 1完成研究依据和只读资产审计，科学协议`protocol_ready`；E0为`audit_ready_smoke_pending`，仍待Session 2来源适配、支持映射及5–8题真实冒烟。没有全量索引、E1、答案生成或新模型执行，不改变历史产物。

| 文件 | 内容 |
| --- | --- |
| [研究依据](research-rationale.md) | 原始来源已读范围、操作定义、反例、成本、未复现差异和五个RQ |
| [资产审计](inventory.md) | H0/B0、真实参数、Gold迁移候选及未决 |
| [公共协议](protocol.md) | 科学规则、三值、预算、面板、筛选、缓存、失败和授权 |
| [来源登记](source_registry.json) | 106来源真实路径/SHA与研究原始来源版本 |
| [解析清单](resolved_manifest.yaml) | 已解析值、null缺口、正式运行阻止范围 |
| [适配任务](implementation-tasks.md) | Session 2逐文件复用、拟建接口、固定反例与真实CLI确认 |
| [交接](../../outputs/pearl-chunking-dev80-20261005-02/handoff.md) | 本阶段实际检查与唯一下一入口 |
| [输出清单](../../outputs/pearl-chunking-dev80-20261005-02/delivery-manifest.json) | 冻结SHA、数量和检查记录 |

audit_session1.py为本阶段只读辅助脚本，package_session1.py只打包已经观察的事实，均不是E0实验运行入口。已执行audit命令的-01失败（element_ids JSON字符串处理）保留，新-02成功；不覆盖现有结果重跑。下一阶段只能按实施任务适配后核验新CLI，不能把拟建接口说成已实现。

执行范围来自[Session计划](../../docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md)及[策略说明](../../docs/superpowers/specs/2026-10-05-pearl-chunking-research-design.md)。协议后续变更须新增版本并说明影响，本阶段完成后停止。
''')
print(json.dumps(dict(papers=len(papers),sources=106,code_hashes=len(base['code_sha256']),created=['source_registry.json','resolved_manifest.yaml','inventory.md','README.md']),ensure_ascii=False))
