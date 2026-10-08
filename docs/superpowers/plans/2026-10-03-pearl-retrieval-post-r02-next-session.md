# PEARL Retrieval：Gold r02 之后的新 Session 交接

*阶段 A 已交付后的 B–D 执行说明 · status: plan · 2026-10-03*

> **For agentic workers:** 使用 `executing-plans` 按阶段执行并汇报；需要实施子任务时可采用 `subagent-driven-development`。实际 child 语义复核必须另用 `fork_turns=none` 的独立子 Agent，继承配置且无模型覆盖，只提供中性包。本交接不执行阶段 B–D，不创建新 chat，不更新个人记忆。

**Goal:** 从已完成的开发 Gold r02 开始，先交付合成输入验证的独立评估入口，再登记完整发布，最后执行 200 题盲化检索评价。

**Architecture:** 复用现有检索算法、指标和审查校验；保留原 dev80 和 r02 修订入口，新增独立评估适配层。检索执行者仅获得 query-only；Gold／标签及中性包生成由独立保管与评审流程处理。每阶段使用独立结果目录和明确验收门槛。

**Tech Stack:** Windows PowerShell、仓库 `.venv` Python、SQLite FTS5、BGE-M3、固定 RRF、bge-reranker-v2-m3、pytest。

## 1. 新 Session 从哪里开始

工作目录：`E:\F_Workspace\F-Agent-Paper`。**首项执行阶段 B 全部任务，验收后汇报；不要重做阶段 A，也不要提前进入真实 200 题流程。** 阶段 C、D 保留为后续检查点。

按仓库要求先读 README → AGENTS → docs/project-architecture.md → Knowledge-Base/README.md → docs/README.md。再读下列材料；当前行为以代码、相关 README 和交付 manifest 为准。

| 材料 | 用途／状态 |
| --- | --- |
| [r02 实验 README](../../../experiments/pearl-retrieval-gold-revision-r02/README.md) | 已实现修订 loader、实际命令和边界 |
| [r02 修订分析](../../../experiments/pearl-retrieval-gold-revision-r02/development-gold-r02-analysis-2026-10-03.md) | 阶段 A 实际交付及限制 |
| [阶段 A completion](../../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/stage-A-completion.json) | 阶段门槛实际记录 |
| [阶段 A delivery manifest](../../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/delivery-manifest.json) | 59 项产物、源码／文档快照身份 |
| [原 dev80 实验](../../../experiments/pearl-retrieval-dev80-20261003/README.md) | 原运行、算法、盲审和复现入口 |
| [方法冻结](../../../experiments/pearl-dev-review-freeze-20261003/method-freeze.json) | 现行四方法配置；不等于完整发布 |
| [配置与入口审计](../../../outputs/pearl-dev-review-freeze-20261003-01/reviews/configuration-audit.json) | 原入口的固定 80／开发模式限制 |
| [Layer 1 协议](../../../paper/pearl-framework/layer-1-retrieval/experiments.md)、[指标](../../../paper/pearl-framework/layer-1-retrieval/metrics.md) | 评价公式、预设比较及执行规则 |
| [child 盲审规范](../../../experiments/pearl-retrieval-dev80-20261003/review-spec.md) | 语义独立性、摘录和联合支持规则 |
| [题集公开记录](../../../experiments/pearl-dataset-80-200-20261003/README.md) | dev 四类各20、eval 四类各50及封存状态；不据此打开评估内容 |
| [原交接计划](2026-10-03-pearl-retrieval-next-session.md) | 保留原 A–D 方案；A 的未勾选条目不是当前未完成状态 |

## 2. 已完成事实与身份基线

- 阶段 A 已完成新 Gold、五字段提案采用、080 新 a3 与 `r2=[[a2,a3]]`、三题实际 child 独立盲审、80 唯一选择清单、共同映射、全部评分／统计／差异、源码快照和修订报告。
- r02 CEGR@10 为 **R1 47/80、R2 49/80、R3 51/80、R4 58/80**；r01 为 47/48/51/58。只有 dev012 的 R1/R2/R4 出现标量变化；R1/R4 @1 各下降一题，050/080 指标不变。不能把 R2 增加一题解释为新算法改善。
- 最终新测试21＋原针对性33，共54项通过；原开发全专项另有47项通过。独立 oracle 核验1,280前缀、48总体指标；77题的308个方法评分对象与r01全文一致。
- 三题125个必审关系全部审定；共138个关系充分审定、487个补充关系未知。080 显式选择 `review/decisions/pearl-dev-080-r02.json`，初份序列化草稿保留，不能 glob 全部决定。
- 三项预设 Holm p 均 >0.05；来源图12个分量、最大33题，差区间均跨零。仍为 `agent_reviewed_preliminary`、`human_verified=false`。
- 全部query、原8题、77题完整对象、106篇Adobe-only来源、6,433 child、索引、方法和原首遍排名不变。原输出538项、难例输出93项、244项冻结输入、200个封存文件身份已核验。
- **阶段 B–D 未执行，完整 release 未冻结，200题正式运行数为0。**

下面的哈希在本次交接整理中重新核验；新 session 仍需读取文件验证。

| 文件（相对于 `outputs/pearl-retrieval-dev80-gold-r02-20261003-01/`） | SHA-256 |
| --- | --- |
| delivery-manifest.json | `a6418a7d6584978c0cf97a1d8dd5aefd90e258886591e14fce63feb882b8a230` |
| gold-r02.json | `7f64ac4559fbf604c0d4d6aca81e23685f1dcbf009853ee3c8637dc368ad29f5` |
| revision-manifest.json | `3cf512f73f05b74343f5d8929cde92dd38bd7a060fdb4c6d6f404feebe89b9b0` |
| selected-review-manifest.json | `383a6f8c775f9832c28dbf18469fa51dbf2947d220c6ca64f8fb83046d6a8e28` |
| analysis-r02-01/support-map.json | `6de0e4eafc0b8563eb9f255102eb46b3d9093640e84213f10b57c89e3ee92df6` |
| analysis-r02-01/score-details.json | `8796c853170c4f531353285efcb070fa1da81fdb65b2b9e84b3496d3ff1f7c78` |

`workspace_files_sha256` 是交付时快照。此次仅新建交接文档并更新 `docs/README.md`，所以导航 SHA 将正常变化；不能修改旧 manifest 来追平。评分源码、修订 README／报告和旧研究产物仍须核对，导航差异必须明确记录。

## 3. 全局边界

- 保留全部旧 Gold、排名、映射、审查草稿、run/preflight/checkpoint、评分和交付 manifest；不覆盖、改名、删除或追改旧状态。
- 阶段 B 对200题Gold、答案、标签、作者日志、QC及混合材料仅核验byte hash和只读属性，不做内容解析、搜索、摘要或试跑。合成测试不得从封存题改写。
- 固定方法：R1正文FTS5 BM25；R2归一化float32精确点积；R3等权RRF k=60；R4固定R3 Top-100完整child重排。D=100，K=1/5/10/20，主指标CEGR@10，seed=20260929，同分chunk ID升序。
- 不调参、换模型、重新解析／切块、扩展parent或做Agentic比较；旧Gold-v5／Stage资产仅historical，不进入PEARL输入或分母。
- 语义复核者与作者／执行者分离；实际child单片段／联合路径需要独立判断，PDF内容不能补入child。K≤20无未决才能评分；21–100未审保持未知。
- 保留dev034处理缺失与分母、030源内矛盾、pilot006分母、079建模子群限制、三个既有R4退步，以及替代完整组为0且未达原目标的限制。
- 不自动commit、push、清理或建立新工作树；保留当前工作区及并行修改。若需要隔离，先核对已有附件和未提交依赖。

## 4. 现有可运行的只读起步

以下是**现有命令**；不调用真实评估，不重跑检索：

```powershell
Set-Location -LiteralPath 'E:\F_Workspace\F-Agent-Paper'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = 'Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src'
git status --short --untracked-files=no
.\.venv\Scripts\python experiments/pearl-retrieval-gold-revision-r02/revision.py --base-directory outputs/pearl-retrieval-dev80-20261003-01 --base-gold outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json --revised-gold outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-r02.json --selected-review-manifest outputs/pearl-retrieval-dev80-gold-r02-20261003-01/selected-review-manifest.json --revision-manifest outputs/pearl-retrieval-dev80-gold-r02-20261003-01/revision-manifest.json --output-directory outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01 --verify-only
.\.venv\Scripts\python -m pytest experiments/pearl-retrieval-gold-revision-r02 experiments/pearl-retrieval-dev80-20261003/test_protocol.py experiments/pearl-retrieval-dev80-20261003/test_score_analysis.py experiments/pearl-retrieval-dev80-20261003/test_verify.py -q
```

预期verify-only为passed、80审查绑定、1,280前缀、48指标；测试数量以新session实际输出为准。旧原 `score.py` 拒绝新Gold是正确行为。r02专用loader固定开发80和三题修订，**不能将它改数量后当作eval200原始运行入口**。

Byte-only封存核验的现有身份清单来自原 `run_manifest.json` 的 `input_binding.sealed_files_sha256`。逐项读取二进制计算SHA并检查只读；禁止以 `json.loads` 打开清单指向的封存内容。244项冻结输入身份可从r02 `immutable-input-verification.json` 读取并逐项核验。不要运行 `prepare_revision.py`、`finalize_inputs.py`、`document_delivery.py` 或 `package_delivery.py` 试图刷新已存在的A交付。

## 5. 阶段 B：合成验证的独立评估入口

**计划目录，不表示已存在：** `experiments/pearl-retrieval-eval-entry-20261003/`；合成验证输出 `outputs/pearl-retrieval-eval-entry-synthetic-20261003-01/`。开始前检查存在性；已有则选新编号，禁止覆盖。先盘点现有函数及测试，再决定最小适配文件；不得重写已验证的检索／计分公式。

| 现有代码 | 已知适配点 |
| --- | --- |
| `experiments/pearl-retrieval-dev80-20261003/prepare.py` | 固定r01开发Gold、80与原8题检查；输入准备与运行访问权限需分离 |
| 同目录 `run.py` | `load_queries`已有expected_count；run内split、80／320及进度仍固定；复用真实检索／forward核验算法 |
| 同目录 `blind.py` | 导入固定GOLD，需显式Gold／query／split及排名身份 |
| 同目录 `score.py`、`protocol.py` | 可复用结构、摘录、排名和公式验证；新原始运行绑定与r02修订模式分开 |
| 同目录 `analyze.py`、`verify.py` | 动态数量、分层、完成矩阵及oracle／封存核验；三项预设比较保持 |
| `experiments/pearl-retrieval-gold-revision-r02/revision.py` | 保留原修订行为；可借鉴全文选择／独立绑定，不能放宽其七字段、a3或继承全文SHA约束 |

### B1. 显式输入契约与合成测试

- [ ] 保存合成80／200 query、Gold、四类配额、child和排名；开发四类各20，评估四类各50；不加载真实封存内容。
- [ ] 明确split、expected_count、query-only、Gold／审查输入、输出目录、raw-run／revision-analysis两类身份。
- [ ] query-only运行端只接收intent_id/query；测试答案、requirement、atom、支持标签及跨split内容不能混入。
- [ ] 先写缺题／重复、错split／数量／配额、输出存在、失败／未运行、合法空／短候选、错hash等拒绝测试；执行失败不按质量0计。

**验收：** 两类合成输入和拒绝测试可运行；运行端与Gold保管端依赖明确分离，真实200内容仍未访问。

### B2. 运行、密封、盲审与动态评分

- [ ] 复用固定算法和模型输入验证；先以合成／stub运行验证动态矩阵及记录，不借真实评估做GPU冒烟。
- [ ] 合成200首遍应覆盖800个题×方法单元，三遍600个timed query；R4对数由实际候选数累加，仅全部100候选时为60,000对。预热另计。
- [ ] 验证首遍唯一评分、后两遍确定性／时延身份、同分规则、R3/R4候选正文一致、forward输入／截断、失败与重试记录。
- [ ] 支持首遍排名密封、去方法／排名／分数线索的中性包、显式唯一审查版本选择、原审查全文SHA绑定和共同映射。
- [ ] 动态输出全部K评分、分层矩阵、配对统计、来源分量敏感性、失败及未知深度；合成200oracle核验3,200前缀和48总体指标。
- [ ] 保留原dev80和r02复现行为，运行新实验测试及原相关回归；不为文档交付宣称全仓测试。

**验收：** 合成80/200全链和固定失败参考通过；旧两个入口可核验。保存实际命令、代码／输入SHA、合成输出、计数及限制；真实评估运行数为0。

### B3. 启动前release门禁与阶段交付

- [ ] 实现启动前核验所选frozen release manifest；合成release测试通过后，阶段C才登记真实release。
- [ ] 拒绝协议、split、预设统计、评分代码、方法配置、模型revision／SHA、索引／child／来源SHA和输入视图漂移；不能仅运行后记参数。
- [ ] 形成新README、适配分析、独立代码审查／验证、完整provenance与交付清单；同步导航并核验相对链接。
- [ ] 汇报B实际完成范围、测试证据、可运行命令、200继续封存的访问证明，以及C的剩余门槛。

**阶段 B 完成定义：** 入口确已实现并在合成80/200上验证，原入口保留，release拒绝门禁可执行，代码／报告／manifest齐全。没有满足时不得登记为完成。本交接不提供尚不存在的新CLI命令。

## 6. 阶段 C：完整发布与隔离query导出

- [ ] 绑定retrieval-v0.2、固定106篇／6,433 child、模型revision／SHA、方法冻结、开发Gold r02及审查／评分代码、阶段B入口／门禁代码、硬件、种子、输出目录及访问角色。
- [ ] 固定CEGR@10主指标、K=1/5/10/20；R2−R1、R3−R2、R4−R3，精确McNemar＋Holm；分层配对bootstrap10,000、seed=20260929；来源依赖单列。
- [ ] 显式登记替代完整组0、开发／评估出题来源互斥但106篇共同检索、Agent复核且非人工Gold、处理损失和深层未知等限制，不能暗写达标或未见文献测试。
- [ ] 验证完整真实release后，由独立隔离保管流程导出eval query-only；运行者不读Gold、答案、标签、作者／QC内容。保管者与child评审者分离；已有出题／旧判断不传给新评审者。
- [ ] 登记导出时点、封存与query身份、访问范围及实际已验证的新命令；仍不试跑评估题。

**交付：** 完整release manifest、通过的实际启动门禁、隔离query-only导出、正式命令与新输出位置；真实评估运行数仍为0。C完成后汇报，再进入D。

## 7. 阶段 D：正式200题评价

- [ ] 固定方法，5道开发query预热；200题固定随机顺序三遍，首遍800单元用于评分并密封；其余两遍核验确定性／时延，差异如实登记。
- [ ] 保存两通道Top-100、完整RRF union、R4输入输出、正文SHA、实际forward token输入、设备、gross与审计扣除估计、失败及重试；600timed query不是600独立题。
- [ ] 独立 `fork_turns=none` 子Agent只读中性实际child包，审单片段／联合路径；K≤20全审定后冻结200唯一选择与四方法共同映射，深层未知保留。
- [ ] 全部200×4×4=3,200前缀评分，输出矩阵、分层、预设配对／来源统计、失败、成本及独立oracle48总体指标验证。
- [ ] 完整核验原始运行／Gold／query／child／排名／审查全文／map／代码／release绑定后交付报告与manifest。

**完成定义：** 原始排名、共同实际支持映射、完整评分统计、独立复算、失败／成本报告及provenance全部齐备后，才可称正式Retrieval评价完成。开发与评估分表，不合并N=280，不把方法／三遍当额外题；若评估结果用于调参，后续分析改标探索性。

## 8. 可直接粘贴的新 Session 启动指令

```text
工作目录：E:\F_Workspace\F-Agent-Paper
请读取 docs/superpowers/plans/2026-10-03-pearl-retrieval-post-r02-next-session.md，先按仓库AGENTS要求核验现有资产，然后执行阶段B全部任务：使用独立合成80/200输入适配评估入口、动态矩阵/盲审/评分/独立验证及启动前frozen-release门禁，并交付适配分析、真实可运行命令、测试和完整provenance。
阶段A已完成，不重复Gold修订或重做语义审查；r02报告和59项交付位于 experiments/pearl-retrieval-gold-revision-r02/ 与 outputs/pearl-retrieval-dev80-gold-r02-20261003-01/。原dev80和r02入口、Gold、审查、排名、运行manifest及旧输出全部保留。导航文件的交接更新与评分源码身份分别核对，不改旧manifest追平。
200题Gold/答案/标签/作者日志/QC/混合材料继续封存，阶段B只核验字节hash和只读属性，不读取内容、不试跑真实200、不调参/换模型/重新解析切块。检索运行者只拿query-only；实际语义复核必须用独立fork_turns=none子Agent、继承配置无模型覆盖，不能传排名/方法/分数/旧判断或借PDF补child。
先盘点现有代码和测试，复用已验证算法；新接口先在合成输入上开发，不把原dev80/r02命令改数量冒充eval200。保持R1–R4、D100、K1/5/10/20、CEGR@10、seed20260929和预设统计；执行失败不能当质量0，深层未审保持未知。不要自动commit/push/清理/创建工作树，不更新个人记忆。完成阶段B全部验收后汇报，再按计划推进C/D；质量仍为agent_reviewed_preliminary、human_verified=false。
```
