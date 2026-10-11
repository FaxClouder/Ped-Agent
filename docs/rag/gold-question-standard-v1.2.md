# PEARL Gold 问题设计、证据标注与质量控制规范 v1.2

*知识侧 PDF RAG 新题集的维护规范；status: current · 2026-10-10；建设规模为目标，正式数据划分、题集登记与冻结尚未完成*

## 1. 身份、优先级与适用范围

本版依据用户提供的 v1.1 整理稿和已同步云端试标记录修订，用户于 2026-10-10 授权按核对建议修改。它是后续新题集构建的统一规范，不表示题集已经冻结、旧评分脚本已兼容或系统效果已经验证。

适用于行人流与疏散科研 PDF 的 Retrieval、Context/Evidence、Answer 与 Grounding 评价；不包含 Agent-Core、Agent-Harness、动态工具控制和视频任务。

- 题集身份、存放、封存访问、实验管理遵循[评测总规范](../../experiments/EVALUATION-STANDARD.md)和[登记表](../../experiments/EVALUATION-REGISTRY.yaml)。登记表只说明已经登记的资产，不能替尚未登记的新题集补造身份。
- 验收遵循[研究验收标准](../research-review-standard.md)：完成规定 Agent 审查与验证可构成正式项目内容；人工核验仅在用户明确指定时成为对应阶段门槛。审查来源、是否盲审、是否冻结与实验用途分别记录。
- 新题集的题型、标注与质量要求以本文为维护入口。旧 authoring/review、Phase 2 和 v1.1 文件保留原阶段效力，不回写原记录，也不宣称本文追溯性地验证了历史样本。
- [v1.1 原稿快照](../../outputs/gold-standard-revision-20261010-01/PedRAGent_PEARL_Gold_v1.1.original.md)仅作修订来源；其中人工前置门槛、100 篇固定口径、结构配额、旧测试选题和单字段可回答性不用于本版。

## 2. 语料、规模与已完成状态

当前新题集使用 106 篇 Adobe-only PDF，对应试标记录 `corpus-pearl-adobe106-v02`；来源身份必须绑定[语料 manifest](../../outputs/pearl-question-redesign-pilot-20261008-01/corpus_manifest.json)及 PDF SHA-256，不能仅凭数量或目录名判断一致。本文不批准删减至 100 篇、扩库或恢复已移除来源。

PDF 是事实核验依据，Adobe 用于定位和结构阅读。解析缺失不等于原文缺证据。Gold 正证据只来自冻结语料；被引用但未入库的原论文不能暗中当作已读原始证据，转述按当前来源的转述身份记录。取证前检查 manifest；依赖索引时另核对 Catalog/索引指纹，不相符须按另行授权构建新索引，不覆盖旧索引。

### 2.1 建设目标

| 主任务 | 定义 | 试标 | 开发目标 | 测试目标 |
| --- | --- | ---: | ---: | ---: |
| A_source_guided | 已知文献中的方法、定义、结果或数据查询 | 10 | 15 | 60 |
| B_open_research | 围绕有限研究问题发现和总结证据 | 10 | 15 | 60 |
| C_contextual | 判断研究对指定场景的适用性与条件 | 10 | 10 | 40 |
| D_evidence_critical | 检查主张的证据、局限、前提与可判定范围 | 10 | 10 | 40 |
| 合计 | 不含语言变体或配对上下文条件 | 40 | 50 | 200 |

这是任务覆盖目标，不代表真实用户频率；不足时报告实际通过数量，不降低质量。正式测试生成前冻结配额，任何调整记录版本与理由，不得按测试方法成绩选题。

多需求题按首要需求归类；存在歧义时依 D→C→A→B 判定并写理由。task_type 与 authoring_path、source_hint 分开：若以已知论文评估局限，可为 D，但必须如实记录来源定向输入，不能伪称主题先行。

不设 75 道跨论文、20 道不可答或固定“180 可答”的证据结构配额。数值、表格、公式、图、来源覆盖和推理操作均作交叉分布报告；可据盲于系统成绩的覆盖诊断提出新候选，不能制造事实、删去替代证据或改标签凑数。允许简单真实问题，不要求每篇论文出题。

### 2.2 最新试标快照

依据[云端本地接收包](../../outputs/pearl-question-redesign-pilot-20261008-01/cloud-revision-import-20261010-01/README.md)及其[统计核验](../../outputs/pearl-question-redesign-pilot-20261008-01/cloud-revision-import-20261010-01/validation.json)：40 题，39 ACCEPT、D-004 未决；284 atoms（223 文本、34 公式、25 表格、2 图像），116 requirements（72 required、44 optional）；2 题标记严格跨论文必要，题干本次修改 0。

这些是记录统计，非本版重新完成的 PDF 语义审核。云端审核非盲、human_verified=false、gold_frozen=false；ACCEPT 表示本轮候选审查通过，不自动满足正式冻结条件。源 QA 引用的云端独立文件与 contract 尚未单独提供，本地导出不冒充其原始字节文件，绑定限制见接收包。

按现有任务分布，39 个接受候选为 A/B/C/D=10/10/10/9，距 50 的目标缺 11（5/5/0/1）；若 D-004 后续通过，则缺 10。此为数量差额，仍需最终资格、题族和来源划分核查；不是冻结资格保证。不向试标参与者提供旧封存题目。

## 3. 出题输入与语言要求

1. A 路径只读允许的真实标题、摘要和元数据，不提供预选答案片段。允许点名论文；表格精准提取任务才使用必要位置提示，并记录 locator_hint。
2. B/C/D 默认只读中性主题概况和任务卡，不接收目标论文、预期结论、atoms、旧答案、系统排名或成绩。若实际看过来源元数据，记录路径，不能假称隔离。
3. 每题提供 research_need、requested_output、known_inputs、scope、origin_type。LLM 合成需求不能宣称来自访谈或真实用户日志；假设场景明确标 hypothetical。
4. 英文问题，表达自然、中性且范围有限；不得复述答案、预设效果方向、把相关性当因果或机械替换名词生成题族。摘要可答性单独标注，不设未经验证的 20% 自动淘汰阈值。
5. 统一任务说明规定“仅依据冻结语料回答”；题干通常不重复 within the corpus，除非语料范围本身是研究对象。该统一说明须版本化并随评测输入保存。
6. C 类保留必要场景条件；不把缺少现实输入的任务强写成精确预测。若需改核心问法，增加 question_revision 并重新取证，不能悄悄把原问题改为更易回答的问题。
7. 数值须明确对象、单位、基准、条件和统计量；估读标 estimated，± 不自行解释为标准差。计算题保存输入、公式、转换与容差依据。
8. required 仅来自题干需求；发现的额外知识列 optional。不同结论、条件或研究方法不得拼成虚假统一答案。

## 4. 取证与分开的判断维度

Solver 先按问题字面范围查找术语和相关来源，阅读正文及必要图表、单位、条件和局限，再构建答案和证据；主动检查替代来源与反证。单次 top-k 不是全库取证，实际工具不可用就记录限制。

| 字段 | 允许值 | 判断对象 |
| --- | --- | --- |
| corpus_answerability | fully / partially / unsupported / unresolved | 冻结语料能否满足问题的明确需求 |
| premise_status | supported / contradicted / unresolved / not_applicable | 问题中的可检验前提 |
| input_sufficiency | sufficient / underspecified / not_applicable | 所问具体结果所需场景输入 |
| expected_response | answer / qualified_answer / correct_premise / request_clarification / explain_evidence_gap 数组 | 合理回答行为，可多选 |
| context_sufficiency | sufficient / partial / insufficient / unassessed | 实验实际给定上下文；试标未运行时为 unassessed |

错误前提可由完整反证充分回答；“还缺什么输入”也可完全回答，不能按 false premise 或 underspecified 直接排出检索分母。full/partial/insufficient 上下文是配对条件，不是新题，也不改变语料可回答性。

unsupported 必须有可审计的全语料相关性筛查、相关全文核查、最强相关但不足证据和剩余不确定性。无法核验完标 unresolved，不把未找到当作不存在。

search_audit 至少含 corpus_version、实际 search_terms/search_routes、逐源筛查范围、relevant_sources_reviewed、strongest_related_evidence、missing_information、核验者与 residual_uncertainty。verified_gap 仅指已完成所声明范围核验的缺口；未完成研究谱系或全库核查列 unresolved_issues。

## 5. 答案、证据与支持路径

每题同时保存 reference_answer、required/optional requirements、accepted_variants 和 unsupported_or_prohibited_claims。每个 required 写 query_basis，定位题干实际需求。答案按事实与证据评判，不按字符串相似度。

### 5.1 三种要求与空证据

- evidence 要求通常必须有充分原文支持。每个局部 support_bundle 必须独立支持 statement 的全部要素；不足就补证或修订，不以主题相关代替。
- behavior 要求可以无正向束，但须保存 trigger、allowed_outputs、prohibited_outputs、rationale；不作为检索漏检项。
- 经核验的缺口可作为 evidence 模式的 gap requirement，列入 gap_requirements，保存可追溯的 gap_audit_ref；其 statement 明确是已核验缺口。它可以无正向束，但不能按空集合计为检索成功。
- 未决调查不能放入 gap_requirements。纯行为或已核验缺口任务可以有空 atoms，但必须有非空、可审核的 requirements 与核验/行为依据；空占位样本不得入 Gold。

### 5.2 Atom 与完整路径

每个 atom 保存题内唯一 atom_id、source_id、pdf_sha256、pdf_page_1based（物理页，从 1 开始）、anchor_text 原文、locator_type、locator_detail、supports_requirement_ids、evidence_role、verification_status。印刷页码另记。表格加表号、行列标题、值、单位、表注和条件；公式/图保留图号、子图、转写/估读方法。Adobe Path、bbox、canonical span 和 parser_version 有据可得时记录，未知留 null 和原因。

support_bundles 为组内 AND、组间 OR；例如 [[a1,a2],[a3]] 表示 a1+a2 或 a3。answer_support_bundles 显式保存覆盖全部需要正证据的 required 且条件兼容的完整 atom 路径。behavior 和已核缺口的要求单独判断，不能由完整正证据束推定通过。

保留合法替代束；仅列 acceptable_alternative_sources 不代表已完成事实支持标注。共同研究被多篇论文转述时记录 study_family_ids，文献数不等于独立研究数。综述与原作冲突均保留来源与角色；未核定研究分母不得声称“多数/主要”。

### 5.3 证据结构后标注

存在合法完整路径时，按最小充分路径判定 single_source_single_evidence、within_paper_multi 或 cross_paper_multi；无完整路径则为 not_applicable 或 unresolved，并说明原因。

cross_paper_required=true 仅当所有已核验完整路径至少需两篇 PDF；有合法单篇路径即为 false；路径未形成则为 null。保存 min_sources_over_valid_bundles、support_sources_count、study_family_ids；不把多来源等同严格多跳，也不宣称穷尽所有潜在路径。

## 6. 审查、裁决与质量门槛

Author、Solver 和审查者使用分离上下文。Auditor 可作答案感知型原文复核，但 is_blind=false；宣称盲审必须先保存独立求解，再打开草案。单 Agent 自复核必须如实标记，不能冒充独立审查；存在独立复核要求的阶段仍应完成该要求。

decision 使用 ACCEPT、REVISE、UNRESOLVED、REJECT。验收、审查方式和冻结分别记录；ACCEPT 不是自动冻结，也不只是“等待人工”的代名词。human_verified 仅在实际人工核验时为 true；用户未指定时不新增人工门槛。裁决保存争议、原文依据、执行者及决议，不使用含义不明的 adjudicated 绕过验收。

硬缺陷包括虚构来源/事实/定位、答案泄露、隐性扩大必答项、证据不足、条件/单位/因果混淆、删替代束凑跨论文、未核实的缺证据结论、未解决泄漏、按系统成绩筛题、审查或版本声明不实。出现缺陷应修订、拒绝或未决，不能用分数抵消。

五维 diagnostic_scores 为 naturalness、non_leading、boundary_clarity、answer_auditability、evidence_or_gap_verification，各 0/1/2 并写理由。任一 0 不得直接接受；总分仅诊断，不设 8/10 自动入选规则。高分比例不代表事实准确率。机器检查不代替逐题语义复核。

## 7. 题族、来源划分与旧集边界

1. 建设目标是新独立题集，不从旧封存 200 题筛选或改写进入新开发/测试。旧题、原报告、登记身份与正式验收结论保留；没有人工参与不构成降格理由。
2. 试标和已用于提示词、规则、参数选择的题及近重复族只用于开发。正式测试在提示、rubric、配额、来源划分与指标资格规则冻结后，用独立上下文新建。
3. 按需求与核心答案事实建立 family_id；换措辞、数字、单位、语言或作者别名不自动产生新题族。机器相似度只作筛查，之后进行全体语义核查。
4. 开发与测试可共享同一检索语料，但出题及有效支持来源保持互斥。A 记录作者所见来源；开放题按已核验有效支持来源及合法替代路径检查，不只比较 primary_source。
5. 题目—来源形成连通关系时共同检查；不得删除正确替代束制造互斥。冲突题隔离或留作开发，若无法划分则报告实际数量并停止冻结。另记研究谱系重叠，不能宣称未见论文泛化。
6. 本规范不授权读取旧封存题正文。新旧题族独立性核验由有明确访问权限的独立角色执行，仅回传碰撞及处置；未执行就记录未核验。

## 8. 数据契约与版本绑定

各阶段 JSONL 一行一题，ID 唯一不回收；版本为正整数，缺失来源参数用 null 加原因。新的序列化文件独立命名，不覆盖已有内容。源云端字段与哈希保持原样，未来适配须另存并留映射，不能把本地导出冒充云端原件。

| 阶段 | 必需字段 |
| --- | --- |
| candidate | candidate_id, question_revision, question, query_language=en, proposed_task_type, research_need, requested_output, known_inputs, scope, origin_type, authoring_path, source_hint, locator_hint, source_metadata_ids, author_suspects_abstract_answerable, authoring_provenance |
| answer | candidate_id, question_revision, answer_revision, corpus_version, reference_answer, requirements, atoms, answer_support_bundles, gap_requirements, accepted_variants, unsupported_or_prohibited_claims, corpus_answerability, premise_status, input_sufficiency, expected_response, context_sufficiency, evidence_scope, cross_paper_required, min_sources_over_valid_bundles, support_sources_count, study_family_ids, information_modalities, reasoning_tags, search_audit, unresolved_issues, solver_provenance |
| QA | candidate_id, question_revision, answer_revision, qa_revision, decision, is_blind, human_verified, gold_frozen, diagnostic_scores, evidence_checked, requirements_checked, answer_bundles_checked, issues, resolution, reviewer_provenance, input_bindings |
| final | 经核验的以上内容，加 intent_id, family_id, task_type, abstract_answerable, metric_eligibility, dataset_split, review_status, acceptance_status, version_locked, review_log |

- known_inputs 为对象数组：statement 与 input_type（hypothetical/user_supplied/metadata_supported）。origin_type 为 real_need_record/title_abstract_inspired/llm_synthetic_need；无真实需求记录不能写 real_need_record。source_metadata_ids 是作者实际看过的元数据，不是预设 Gold 来源。
- requirement：requirement_id、statement、importance（required/optional）、query_basis、assessment_mode（evidence/behavior）、support_bundles；行为项另有 behavior_criteria，缺口项另有 gap_audit_ref。无关 atoms 标 context，不能虚挂 supports_requirement_ids。
- provenance 记录角色、实际模型/提供方、提示版本、输入 manifest、时间、工具范围、复核方式与限制；未知模型/采样参数不猜。
- input_bindings 记录 candidate/answer/corpus 的实际文件名与 SHA-256、record_id、记录 SHA-256 和 record_hash_algorithm；记录哈希规范为 UTF-8 的 JSON（sort_keys=true, ensure_ascii=false, separators=(',', ':'), allow_nan=false），无尾随换行；文件哈希按实际字节。文件级 JSONL 使用 UTF-8 无 BOM，每条紧凑 JSON 后加 LF。
- 改问题文本增加 question_revision，答案重新验证；只改答案/证据增加 answer_revision；QA 每次重新裁决增加 qa_revision，绑定确切问题/答案。历史版本号不自动重写；首次采用 answer_revision 时单独声明迁移。
- 新版冻结前必须完成该契约的结构验证与现有评分脚本适配核验。本次仅维护规范，没有实现或验证新版评分代码。

## 9. 指标资格、映射与冻结

metric_eligibility 为按指标名索引的对象，各含 eligible（true/false/null）、reason、rule_version；null 表示待决，不能进入该指标正式分母。运行前冻结资格与分母 N，不随系统成绩变更。

| 对象 | 资格与边界 |
| --- | --- |
| Layer 1 | 有审定非空完整正证据路径且该指标适用；按实际 child 语义支持计分，非同源/同页命中；行为或空束不自动成功，也不随意计零 |
| Layer 2 | 评价实际预算后的上下文及条件；parent 补证不回填 Layer 1 |
| Layer 3 | required 事实与行为要求按各自 rubric 评价，optional 不升级为隐藏必答 |
| Layer 4 | 检查实际事实与引用支持、条件和外推；与答案正确性分开 |
| 部分可答/缺口/澄清 | 审定专门资格与分母，单独报告；不混入未经说明的完整证据率 |

错误前提的完整反证可适用检索评价。Gold atom 映射至 PDF span/表格、Adobe canonical 对象和具体配置下 chunk；记录 parsed/indexed/mapping_status 及缺失原因。Gold 的答案、标注、评分规则不得进入运行时索引；索引映射不是 Gold 唯一身份。

冻结前核对题号和引用唯一性、每条局部/完整路径、数值条件、缺口审计、题族/来源互斥、审查 provenance、版本哈希与指标资格。未决项不得混为通过；报告候选/拒绝/修订/未决/实际纳入数、来源及独立研究覆盖，不把同一研究多次转述算独立复现。

交付独立版本目录、candidate/answer/QA、query-only 导出、split_audit、dataset_manifest、gold_span_alignment 与研究谱系记录。query-only 仅 ID 和英文问题，统一任务说明单独冻结，不泄漏题型/答案。正式存放及登记遵循评测总规范；冻结不代表系统实验已运行。任何原件受清单绑定时保持路径和哈希。

## 10. 可交给执行者的简明指令

以下提示必须同时提供本文版本、角色允许输入、批次范围、输出位置与停止条件；提示不能单独覆盖本文，也不授权额外阶段。

**Author：**按 §2–3 生成英文候选；A 仅读允许标题/摘要，主题先行 B/C/D 不读目标来源、答案或旧测试内容。输出 §8 candidate 全部字段，不输出答案/atoms，不预定跨论文必要性和可回答性。不足就报告，不凑数；完成指定批次停止。

**Solver：**独立按题干需求阅读冻结语料和原 PDF，核验事实、图表、条件、替代路径和反证。分别填写 §4 的判断维度，按 §5 构建 requirements、atoms 与完整路径；未完成调查记 unresolved。输出 §8 answer 字段及实际 provenance，不修改问题或宣布冻结。

**Auditor：**逐题核对原文、必答范围、局部/完整束和合法替代路径，检查输入/前提/语料判断及缺口依据。如看过草案必须记录非盲；独立求解需先落盘。输出 §8 QA，五维评分仅诊断，硬缺陷不得抵消；接受不是人工核验或版本冻结。

**Curator：**只依据实际审查结果与冻结规则整理；执行 §7 来源/题族划分和 §9 资格审定，保留全部去向和未知项。独立新建测试，不能从旧封存题挑选；不读取未获授权的旧内容。条件不足就报告并停止冻结；不运行被测系统、不覆盖旧资产。

## 11. 本次变更与未执行事项

相对原 v1.1：统一 106 篇 manifest；采用项目 Agent 验收标准；保留任务数量目标而取消证据结构/不可答固定配额；分离判断维度和空证据规则；保留新测试独立构建与支持来源互斥；补齐版本、哈希、指标资格契约和角色提示。试标数字采用云端新包，不回写本地历史 v2。

50/200 正式题集、补题、D-004 裁决、来源划分最终可行性、独立审查缺口及云端原始绑定补全、Gold 冻结、评分适配和系统实验均不由本次文档修订视为完成。相关文档处置见[文档核对与整理建议](gold-document-disposition-2026-10-10.md)。
