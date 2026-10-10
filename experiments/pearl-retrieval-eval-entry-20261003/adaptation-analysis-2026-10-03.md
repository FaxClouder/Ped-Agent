# PEARL Retrieval 阶段 B 入口适配分析

*独立合成输入验证与原入口兼容性分析 · status: current · 2026-10-03*

## 范围与验收状态

本交付执行 [post-r02 计划阶段 B](../../docs/superpowers/plans/2026-10-03-pearl-retrieval-post-r02-next-session.md)，阶段 A 不重做。新增实验适配层在合成 80／200 输入上验证；真实 200 题仍封存，真实检索运行数为 0。阶段 C 的完整真实 release、隔离 query 导出和阶段 D 正式评价尚未执行。

阶段 B 已完成。最终稳定源码联合回归 **126 项通过**（新增 58、原 dev80／r02 回归 68），执行期间源码 SHA 未变，见 [final-tests.json](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/final-tests.json)。[独立规格与代码审查](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/code-review-03.md)均通过；审查发现的消费文件覆盖、实际模型资产、原生 Gold、forward 身份、失败退出码和持久化问题已修复并复测。

完整 CLI 的 [运行收据](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/synthetic-cli-receipt.json)和 [保存后重开验证](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/saved-delivery-verification.json)均通过；后者使用独立 `custody.py verify` 命令核对两套保存产物，再以 `runtime.py --verify-release-only` 核验所选合成 200 release 的 71 条文件绑定，未初始化模型。最终 [阶段完成记录](../../outputs/pearl-retrieval-eval-entry-synthetic-20261003-01/stage-B-completion.json)和 [交付清单](../../outputs/pearl-retrieval-eval-entry-synthetic-20261003-01/delivery-manifest.json)绑定输入、输出、源码快照、报告及导航身份。

## 最小适配与复用

| 环节 | 旧入口限制 | 新适配职责 | 保留的算法／校验 |
| --- | --- | --- | --- |
| 运行输入 | 原 prepare/run 固定开发 80、r01 身份 | 显式 split、expected_count、query-only、独立开发预热与 raw-run 身份 | 原检索、模型 forward 核验 |
| 启动门禁 | 原 preflight 绑定开发运行，方法冻结不是完整发布 | 外部所选 release SHA；启动前核验实际消费文件、代码、方法／统计与模型身份 | FTS／向量、正文与模型资产校验 |
| 审查准备 | blind 默认固定 Gold | 保管端显式 Gold；首遍排名密封后生成中性实际 child 包 | packet、递归盲化、正文身份 |
| 审查选择 | 开发及 r02 各有固定身份链 | 明确唯一版本、packet SHA、原决定全文 SHA、共同映射 | 原 validate_decision 的联合路径／逐 child 摘录校验 |
| 评分分析 | 验证器与部分分层／分母固定 80 | 动态矩阵、四层配额、所有 K、配对／来源统计、失败及未知深度 | 原 DNF scorer、统计函数、布尔 oracle |
| Gold 修订 | r02 固定三题、七字段及继承全文约束 | 新 raw-run 与 revision-analysis 明确区分，旧修订入口继续保留 | 原 revision.py 全部约束 |

实现见 [runtime.py](runtime.py)、[stub_backend.py](stub_backend.py)、[custody.py](custody.py)、[synthetic.py](synthetic.py)。检索运行端不导入 Gold 保管、审查或评分模块；Gold SHA 作为不透明身份绑定，运行端不解析 Gold。保管端核对 query、split、child 及 Gold 的冻结身份后才生成包和评分。

R1 保持英文正文 FTS5 BM25；R2 保持归一化 float32 精确点积；R3 保持等权 RRF k=60；R4 只重排固定 R3 Top-100 的完整 child。D=100，K=1/5/10/20，CEGR@10 为主指标，seed=20260929，同分按 chunk ID 升序。三项预设比较为 R2−R1、R3−R2、R4−R3，沿用精确 McNemar、Holm 和配对分层 bootstrap 10,000 次；来源连通分量敏感性单列。

## 合成验证的含义

合成 query、Gold、child、来源和支持决定均独立构造，不改写封存题。四层名称沿用 `single_source`、`numeric_table`、`within_paper_multi`、`cross_paper`，开发各 20、评估各 50。合成组包含联合 child、必要条件、AND／OR 与跨来源结构，仅用于工程固定参考。

合成后端执行真实 FTS5、精确向量点积及固定 RRF；embedding、reranker 和 token forward 使用显式 stub。由此证明入口、记录、排名／正文身份、动态评分与拒绝门禁的行为，不能据此宣称真实 BGE-M3、reranker 或 GPU 验证通过，也不能将合成分数解释为检索质量。

首遍 80／200 分别为 320／800 个题×方法评分单元；三遍分别为 240／600 个 timed query。后两遍用于确定性及 instrumented 时延记录，不增加独立题数。预热单独记录并排除计分；评估预热来自独立开发 query。R4 pair 按实际候选累加，600 个 timed query 只有在每次均为 100 个候选时才是 60,000 对。

最终保存的 [合成计数](../../outputs/pearl-retrieval-eval-entry-synthetic-20261003-01/synthetic-summary.json)与独立 CLI 重开验证如下；每次实际返回 24 个候选：

| 验证项目 | 合成 80 | 合成 200 |
| --- | ---: | ---: |
| 首遍唯一评分单元 | 320 | 800 |
| 三遍 timed query | 240 | 600 |
| timed R4 pairs | 5,760 | 14,400 |
| 开发预热 query／pairs（另计） | 5／120 | 5／120 |
| 独立 oracle 前缀／总体指标 | 1,280／48 | 3,200／48 |
| 合成来源连通分量（大小） | 2（40、40） | 2（100、100） |
| 深度 100 未审关系（题×方法×child） | 1,144 | 2,864 |

另存的固定失败参考在两次尝试后为 `failed`、`quality_scores=null`；成功重试参考保留一次 attempt failure、无 terminal failure。0／3／100 候选的 200 题执行测试分别核对 0／1,800／60,000 timed pairs。合成质量未完整单元分别为 173／437，它们是成功运行后的证据路径算例，不等同于执行失败，也不代表真实方法效果。原始逐题时延、forward 输入及计数保存在各 `pass-*` 审计和逐题 journal；stub 时长不用于报告模型性能。

执行失败与未运行单元拒绝计分；合法空／短返回在成功身份和原因完整时按实际排名计分。失败及重试记录保留。审查选择不 glob 全部草稿，每题只选一个版本；K≤20 必须已审定，21–100 未充分审定者仍为未知。

实际运行命令、输入和源码 SHA、矩阵／时延计数、失败参考、保存后 oracle 与拒绝测试详见 [README](README.md) 和 [合成输出](../../outputs/pearl-retrieval-eval-entry-synthetic-20261003-01/)。

## 原入口和封存资产

执行前的 [保存核验](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/before.json)核对原 dev80 538 项、难例／方法冻结 93 项、r02 59 项交付产物、244 项冻结输入和 200 个封存文件；无哈希异常，封存文件均为 Windows 只读。另保存 722 个旧源码／产物文件的字节快照，交付后逐项比较。

封存内容只以二进制流计算 SHA，并检查只读属性；没有解析、搜索、摘要、改写或试跑 Gold、答案、标签、作者日志、QC 或混合材料。证据来自 [审计脚本](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/preservation_audit.py)及前后核验记录；Windows 只读属性本身不提供角色隔离，阶段 C 仍须安排独立保管流程。

交付后的 [保存核验](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/after.json)再次通过 690 项原交付产物、244 项冻结输入与 200 项封存哈希／只读检查；[722 个旧文件前后比较](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/old-files-after-comparison.json)无变化或缺失。没有重做阶段 A 的修订、检索或语义判断。

旧 manifest 的文档快照在本阶段开始前已有导航／协议状态文本差异，见 before.json 的 `workspace_snapshot_differences`；原评分、运行源码及旧交付字节身份通过。本阶段仅追加新入口与报告并更新导航，旧 manifest 不追改 SHA。

原 dev80 与 r02 回归在执行前为 68 项通过。原 dev80 只读验证见 [r01-entry-verification.json](../../outputs/pearl-retrieval-stage-b-audit-20261003-01/r01-entry-verification.json)，r02 `--verify-only` 为 passed；两者均核验 80 个审查全文绑定、1,280 前缀及 48 总体指标，未重跑检索或语义审查。

## 阶段 C／D 的剩余门槛

阶段 B 的合成 release 不能充当真实发布。阶段 C 需要登记 retrieval-v0.2、固定 106 篇／6,433 child、两套真实模型 revision／SHA、原方法冻结、开发 Gold r02、支持审查／评分／统计及新入口代码、硬件、种子、输出目录和访问角色；通过实际启动门禁后，再由独立保管流程导出评估 query-only。阶段 D 才运行正式 200 题，并由独立 `fork_turns=none` Agent 阅读中性实际 child 包完成语义判断。

原研究限制全部保留：替代完整组为 0，原目标未达；开发与评估出题来源互斥，但共同检索全部 106 篇，不是未见文献测试；dev034 的处理缺失保留分母，dev030 保留源内方向矛盾，pilot006 保留 f1(N) 分母，dev079 保留建模子群范围；pilot001、dev070、dev071 的既有 R4 退步不撤销。深层未知和来源依赖继续报告，instrumented 时延及审计扣除估计不等同干净时延。

真实 Gold／支持结果仍为 `agent_reviewed_preliminary`、`human_verified=false`。合成审查决定明确标为 fixture，没有新增真实语义复核或研究结论。本阶段不 commit、push、清理、建立工作树或更新个人记忆。
