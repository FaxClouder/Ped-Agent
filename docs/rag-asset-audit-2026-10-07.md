# RAG 资产与一致性审计

*RAG/PEARL 文档、实验目录与 `outputs/` 产物的逐项分类和一致性核验 · status: current · 2026-10-07*

本审计没有运行检索、生成或评分。第一轮只读盘点并修正入口文档；第二轮按用户批准执行整理（第 6 节），
只删除了一个重复目录和一个空目录，没有移动或改动任何被交付清单绑定的产物。正在进行的 6B 评审（`outputs/pearl-chunking-dev80-20261007-16/`、
[`paper/pearl-6b-judge-workpackage/`](../paper/pearl-6b-judge-workpackage/README.md)）不在任何整理动作范围内。

## 1. 结论

| 项 | 结论 |
| --- | --- |
| 实验结果与文档数字 | 抽查的 6 组核心数字与冻结产物一致（见第 2 节） |
| 文档状态 | 入口文档、PEARL 分层协议和 31 个未登记文档的状态已修正（第 3 节） |
| 产物规模 | `outputs/` 约 31G、64 个目录、32 个散落文件（盘点时；整理后为 63 个目录、33 个文件）；另有 `failed/outputs-void-scores/` 164M、`memPed/knowledge/derived/` 1.7G |
| 已清理 | 删除 1 个逐字节重复目录（`Claude outputs/`）和 1 个空目录；3 个空 run 目录因被记录引用而保留（第 6 节） |
| 主要风险 | 正式内容大量未进 Git；PEARL 80/200 冻结 Gold 只存在于 Git 忽略的 `outputs/`；`outputs/` 无登记表 |

## 2. 关键数字复核

| 文档中的数字 | 冻结来源 | 结果 |
| --- | --- | --- |
| 200 题 CEGR@10 = 116/118/126/139 | `outputs/pearl-retrieval-eval200-20261003-01/statistics.json`（R2−R1 +1.0、R3−R1 +5.0、R4−R3 +6.5 pp） | 一致 |
| R4 相对 R3 +6.5 pp，Holm p = 0.044 | 同上，`comparisons.R4-R3.Holm_adjusted_p = 0.0439` | 一致 |
| Layer 2 CGC = 63/64/62/71 | `outputs/pearl-answer-dev80-20261004-01/stage80/analysis-tables-r01.md`（充分 N 列） | 一致 |
| Layer 3 Strict = 60/58/57/61，oracle 73 | 同上，总体表 | 一致 |
| E1 C2-L384 4K CGC = 57/80 | `outputs/pearl-chunking-dev80-20261005-07/candidate-selection-e1-r07.json` | 一致（C3-L256 = 56，次优非重复候选） |
| E4 M1 55＋2 unknown vs M0 57 | `experiments/pearl-chunking-dev80-20261005/session5b-e4-2026-10-06.md` 与 06-13 交接 | 报告与交接一致；未单独复算 |

Layer 4 的有据性与拒答数字未在本次复核范围内。

## 3. 文档一致性

### 3.1 已修正

| 文档 | 问题 | 修正 |
| --- | --- | --- |
| [`docs/README.md`](README.md) | 切片入口写“E5 尚未启动”，“下一会话唯一交接”指向 06-13 | 改为 6A 已完成、6B 以工作安排为准；06-13 保留阶段身份 |
| [`experiments/README.md`](../experiments/README.md) | 同上，“下一会话进入 6A” | 同上 |
| [`Knowledge-Base/README.md`](../Knowledge-Base/README.md) | 两处路径指向已迁走的 `outputs/gold-v5-*`；“仅有 Adobe 示例冒烟”与 106 篇实际解析矛盾；未链接 200 题评价和切片研究 | 改为 `failed/outputs-void-scores/` 路径；链接 106 篇索引与解析器对照实验；补入口 |
| [`memPed/README.md`](../memPed/README.md) | 把 Gold v5 写成“当前活跃”；索引位置只写旧 104-v1 | v5 标为 historical，指向 PEARL 80/200；补 PEARL 冻结索引 |
| [`docs/project-architecture.md`](project-architecture.md) | RAG 状态只写到 V1/V2 与 Gold v5 | 补一段 PEARL 现状说明，标明 V1/V2 对照为 historical |

### 3.2 第二轮已修正（用户批准 C 项）

| 位置 | 问题 | 处理 |
| --- | --- | --- |
| `paper/pearl-framework/layer-2-evidence/README.md` | `status: plan`，但 Layer 2 开发评价已完成 | 状态改为 `current`，页首加执行状态说明并链接实验入口；协议正文不改 |
| `paper/pearl-framework/layer-3-answer/`、`layer-4-grounding/`、`layer-4-reliability/` | `status: 待设计`（不在规定的四种状态内） | 同上；Layer 3 的“当前尚未执行本层校准实验”改为指向页首说明 |
| `paper/pearl-framework/layer-5-agentic/`、`layer-6-efficiency/` | `status: 待设计` | 改为 `plan` |
| `paper/pearl-framework/datasets/README.md` | “完整 80 题检索尚未运行”；200 题“未运行” | 改为已运行并链接实验 |
| [`experiments/benchmark-gold-20260923/README.md`](../experiments/benchmark-gold-20260923/README.md)、[`benchmark-index-20260924`](../experiments/benchmark-index-20260924/README.md) | 状态与导航页矛盾 | 改为 `historical`，注明原状态 |
| [`failed/README.md`](../failed/README.md) | “outputs 保留 19 个目录”过期 | 加注快照日期并指向本审计，原表保留 |
| `docs/` 根下 31 个未登记文档 | 无状态、未登记 | 29 个加 `historical` 标注；坐标变换设计改为规范的 `target`；全部登记到[导航页](README.md)“2026-10-07 审计补登记” |

### 3.3 仍未处理

| 位置 | 问题 | 原因 |
| --- | --- | --- |
| `outputs/RAG改进与实验计划汇总.md` | 引用仓库外路径 `/mnt/project-files/pearl/…` | 个人汇总笔记，是否转为维护文档由用户决定；已在 `outputs/README.md` 注明 |
| `paper/pearl-6b-judge-workpackage/README.md` | 日期写 2026-10-08，晚于本地日期 | 6B 进行中，不改动其工作包 |

## 4. `outputs/` 产物分类

分类口径：**现行交付**＝当前文档入口引用的阶段交付；**谱系输入**＝没有被文档直接引用，但被后续交付清单按 SHA
绑定，删除会破坏复现；**历史**＝PEARL 之前的资产，结论作废但资产可复用；**失败/中止**＝有失败记录或被
更新尝试取代；**空/重复**＝无内容或与他处逐字节相同。

### 4.1 PEARL Layer 1–4（2026-09-29 至 10-05）

| 目录 | 大小 | 分类 | 说明 |
| --- | ---: | --- | --- |
| `pearl-l1-readiness-20260929-01` | 34M | 谱系输入 | 106 篇语料准备脚本与 Catalog 备份；脚本不在 Git |
| `pearl-index-106-adobe-20260929-01` | 187M | 现行交付 | PEARL 冻结索引（106 篇、6,433 child） |
| `pearl-retrieval-dev-pilot-8-adobe106-20260929-01`、`-r4-` | 14M / 6M | 现行交付 | 8 题 R1–R4 试点 |
| `pearl-dataset-80-200-authoring-20261003-01` | 30M | 谱系输入 | 题集编写与复核中间件 |
| `pearl-retrieval-dev80-eval200-adobe106-20261003-01` | 820K | **现行交付（关键）** | 80/200 冻结 Gold 与封存清单，全仓唯一一份 |
| `pearl-retrieval-dev80-20261003-01` | 405M | 现行交付 | 80 题 R1–R4 开发 |
| `pearl-dev-review-freeze-20261003-01` | 15M | 现行交付 | 难例复核与配置冻结 |
| `pearl-retrieval-dev80-gold-r02-20261003-01` | 27M | 现行交付 | Gold r02 修订与重算 |
| `pearl-retrieval-eval-entry-synthetic-20261003-01`、`pearl-retrieval-stage-b-audit-20261003-01` | 214M / 99M | 现行交付 | 阶段 B 合成验证与审计 |
| `pearl-retrieval-eval200-release-20261003-01`、`-02` | 17K / 41K | 失败/中止 | 01 准备失败、02 预热违规被拒；文档已记录，03 取代 |
| `pearl-retrieval-eval200-release-20261003-03` | 9.3M | 现行交付 | 阶段 C 发布 |
| `pearl-retrieval-eval200-20261003-01`、`-audit-` | 2.4G / 7.4M | 现行交付 | 阶段 D 200 题评价与审计 |
| `pearl-evidence-dev80-20261004-01` | 124M | 现行交付 | Layer 2 |
| `pearl-answer-dev80-20261004-01` | 109M | 现行交付 | Layer 3 |
| `pearl-layer4-dev80-20261004-01` | 395M | 现行交付 | Layer 4 |
| `pearl-layer1-4-summary-check-20261005-01` | 18K | 现行交付 | 汇总核对 |

### 4.2 切片研究（2026-10-05 至今）

```mermaid
flowchart LR
    S1["05-02 Session1"] --> S2["05-03 E0"] --> E1["05-04 尝试 → 05-05 E1"]
    E1 --> G["05-06 E3 门禁 blocked"] --> R["05-07 补审冻结"]
    R --> C["06-01…05 收尾尝试 → 06-06 收尾"]
    C --> E3["06-07…10 E3 分片 → 06-11 E3"]
    E3 --> E2["06-12 E2"] --> E4["06-13 E4＋冻结"] --> A6["06-14 6A"] --> B6["06-15 6B blocked"] --> X["07-16 外部评审（进行中）"]
```

| 目录 | 大小 | 分类 | 说明 |
| --- | ---: | --- | --- |
| `pearl-chunking-dev80-20261005-01` | 1K | 失败/中止 | Session 1 审计失败记录，`-02` 取代；已在实验 README 说明 |
| `…-20261005-02`、`-03` | 7.2M / 892M | 现行交付 | Session 1、E0 |
| `…-20261005-04` | 1.2G | 谱系输入 | E1 首次尝试，被 05-05 交接与 06-04 保全记录引用 |
| `…-20261005-05` | 11G | 现行交付 | E1 全矩阵，13 套独立索引占主要空间 |
| `…-20261005-06` | 8K | 现行交付 | E3 门禁 blocked 记录 |
| `…-20261005-07` | 167M | 现行交付 | E1 补审与候选冻结 |
| `…-20261006-01`、`-02`、`-03` | 0 | 空（保留） | 无任何文件；E1 收尾记录登记为失败尝试，保留以免编号重用 |
| `…-20261006-04`、`-05` | 148K 各 | 失败/中止 | 收尾尝试，仅有输入保全快照；对应根目录 `pearl-chunking-closeout-20261006-0[3-6]-command.log` |
| `…-20261006-06` | 8.8M | 现行交付 | E1 收尾 |
| `…-20261006-07`…`-10` | 0.3–1.7G | 谱系输入 | E3 组装分片，被 06-11 交付清单引用 46 处 |
| `…-20261006-11` | 5.2G | 现行交付 | E3 |
| `…-20261006-12` | 3.0G | 现行交付 | E2（O10/O20 索引） |
| `…-20261006-13` | 793M | 现行交付 | E4＋最终冻结 |
| `…-20261006-14` | 29M | 现行交付 | 6A 生成 |
| `…-20261006-15` | 3.3M | 现行交付 | 6B API 裁判 blocked |
| `…-20261007-16` | 66M | **进行中** | 外部评审导入目标，不得改动 |
| `pearl-chunking-chain-20261006` | 4.4M | 现行交付 | 无人值守链调度记录，链已停止 |

`outputs/` 根下的 `e3-*.json/.log`（22 个）和 `pearl-chunking-closeout-*.log`（8 个）属于上述 E3 与收尾尝试的命令记录；`pearl-retrieval-dev80-20261003-01-run.log` 属于 80 题开发运行。三者应随对应目录归位。

### 4.3 PEARL 之前（historical）

| 目录 | 大小 | 说明 |
| --- | ---: | --- |
| `knowledge-index-104-v1-20260924-01` | 113M | 旧 V1 索引，文档引用 7 处 |
| `knowledge-index-104-v1-lexical-candidate-20260926-01` | 16M | 旧词法候选 |
| `knowledge-index-104-v2-candidate-20260926-01`、`-02` | 145M 各 | 旧 V2 候选；`-01` 未被任何文档引用 |
| `parser-sensitivity-p2-*-20260927-01`（3 个） | 503M | 解析器对照；结论作废，配对资产可复用 |
| `stage2-*`（6 个） | 556K | Stage 2 复核；其中 3 个未被引用 |
| `literature-preflight-*`（2 个） | 8K | 预检记录 |
| `adobe-comparison-sample-2026-09-23` | 157K | Adobe 对照样例，未被引用 |
| `chunk-cleanup-backup-20260921-151830`、`metadata-batch-1-backup-20260921` | 27M / 1.1M | 回滚备份，未被引用 |
| `rag-example-extract-20261007` | 340K | 今日样例抽取，未被引用 |

## 5. 结构性风险

1. **正式内容未进 Git。** `experiments/` 下除 `README.md` 与两个旧实验各一个文件外全部 untracked，包括所有
   PEARL 实验 README、报告和评分脚本；`docs/research-review-standard.md`（`AGENTS.md` 直接引用）和
   `docs/module-division-and-design.md` 也未跟踪。
2. **冻结 Gold 只有一份。** 80/200 题 Gold 与 `seal_manifest.json` 位于 Git 忽略的
   `outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/`，`memPed/` 中没有对应副本。
   **2026-10-07 已处理**：见第 8 节，现有规范副本，但两份都在同一块本地磁盘上。
3. **数据根目录混入运行结果。** `memPed/knowledge/pearl-retrieval-pilot-r1-*`（14M）是 8 题试点的排名与
   评分，按 `memPed/README.md` 应位于 `outputs/`；被 `paper/pearl-framework/datasets/retrieval-pilot/` 两份文档引用。
4. **脚本只存在于 `outputs/`。** `outputs/` 下约 600 个 `.py`，多数是有意冻结的代码快照，但
   `pearl-l1-readiness-20260929-01/` 等目录的准备脚本没有其他副本。
5. **`outputs/` 无登记表。** 64 个目录中 20 个没有被任何文档引用，只能靠交付清单反查。

## 6. 整理执行记录（2026-10-07，用户批准 A–D）

| 编号 | 批准内容 | 实际执行 | 偏离原因 |
| --- | --- | --- | --- |
| A | 删除空目录与重复目录 | 删除根目录 `Claude outputs/`（逐字节比对与 `outputs/pearl-chunking-dev80-20261005-06/` 相同后删除）和空目录 `outputs/figures/` | `pearl-chunking-dev80-20261006-01`…`-03` **保留**：E1 收尾记录 `commands-and-checks-r01.json` 将其登记为失败尝试，删除后运行编号可能被重用 |
| B | 根目录日志归位 | **未移动**任何日志；新增 [`outputs/README.md`](../outputs/README.md) 说明绑定关系 | 22 个 `e3-*` 文件被 06-11 交付清单按 `outputs/<文件名>` 绑定 SHA；8 个收尾日志被 06-06 记录和冻结代码快照按根路径引用。移动会让核验失败 |
| C | 修正其余文档状态 | 见第 3.2 节 | 无 |
| D | 准备 Git 提交范围 | 见第 7 节；用户随后决定暂不提交，只在本地保存 | 无 |

E 项（释放约 16G 可重建索引）未获批准，未执行。所有动作未涉及 `__pycache__`。

## 7. Git 提交范围建议（已暂缓）

> **用户决定（2026-10-07）**：以下内容暂不提交 Git，只在本地保存。本节保留为日后提交时的参考清单；在此之前，第 5 节所列“只有本地一份”的风险继续存在。

### 7.1 建议提交：516 个未跟踪文本文件，约 6 MB

| 范围 | 文件数 | 内容 |
| --- | ---: | --- |
| `experiments/`（16 个实验目录） | 405 | 实验 README、分析报告、协议、评分与运行脚本、测试、小体积配置；最大单文件 `source_registry.json` 0.78 MB |
| `docs/` | 62 | 根目录 44 个（含本审计、`research-review-standard.md`、`module-division-and-design.md`）、`superpowers/` 16 个、`assets/` 2 个 |
| `paper/pearl-framework/` | 32 | 分层设计、8 题试点数据与脚本、语料审计清单、Layer 1–4 汇总报告 |
| `paper/RAG_Report/` | 17 | RAG 调研资料包的文本与目录（PDF 已由其 `.gitignore` 排除） |

核查：没有发现 API 密钥（含 `api_key` 的匹配均为读取环境配置或测试占位字符串）；实验目录内没有封存 200 题的题目内容。
另有用户此前已修改的已跟踪文件（`git status` 中的 ` M`，包括本次编辑过的入口文档），本次编辑与此前的未提交修改混在同一文件中，提交时需要用户确认是否一并提交。

### 7.2 需要用户决定

| 项 | 说明 |
| --- | --- |
| PEARL 80/200 冻结 Gold | 现在只有 Git 忽略的 `outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/` 一份（820K）。可复制到 `memPed/knowledge/gold/` 下新的版本目录后提交（按 `memPed/README.md`，评测输入 `*.json/jsonl` 可提交）；提交封存集不影响“未参与调参”的约束，但会让仓库所有读者都能看到题目 |
| `paper/Fig-Sum/` | 5 个文件 10 MB，含图片与 drawio 源 |
| `paper/pearl-6b-judge-workpackage/` | 4,725 个文件 56 MB，6B 进行中，建议完成后再提交 |

### 7.3 不提交

| 项 | 原因 |
| --- | --- |
| `memPed/knowledge/batch-*-incoming/` 等 PDF | 受限原文，`AGENTS.md` 禁止提交 |
| `memPed/knowledge/pearl-retrieval-pilot-r1-*` | 运行结果，应属于 `outputs/` |
| `paper/Stage-Report/`（8,557 个文件，380 MB） | 主要是 `.codex-build/node_modules`；建议把 `paper/Stage-Report/.codex-build/` 加入 `.gitignore` |
| `.tmp-organize/`、`.pearl_audit*_tmp.py`、`.orca/`、`.learnings/` | 临时文件 |
| `Agent-Harness/`、`Knowledge-Base/src`、`tests` 下的未跟踪代码 | 属于进行中的 Agentic 开发，不在本次 RAG 整理范围内 |

不建议把 PEARL 之前的 `outputs/` 目录再迁入 `failed/`：它们被 10 余份文档按路径引用，迁移收益小于改链成本，
本审计的分类表已能区分现行与历史。

## 8. Gold 规范副本与评测规范（2026-10-07）

用户决定把问题集迁到 `memPed/`，并选择“复制为规范副本”：25 个已完成实验与 6B 的脚本按原路径读取 Gold，
交付清单也按原路径绑定脚本和 Gold 的 SHA，物理移动或改脚本都会破坏复现核验。

| 动作 | 结果 |
| --- | --- |
| 复制 | 9 个文件逐字节复制到 [`memPed/knowledge/gold/pearl-adobe106/`](../memPed/knowledge/gold/pearl-adobe106/README.md)，SHA-256 与原件一致，副本只读；记录见该目录 `copy-manifest.json` |
| 新规范 | [`experiments/EVALUATION-STANDARD.md`](../experiments/EVALUATION-STANDARD.md) 与 [`EVALUATION-REGISTRY.yaml`](../experiments/EVALUATION-REGISTRY.yaml)；登记表中全部路径与 SHA 已逐项校验 |
| 同步的维护文档 | `AGENTS.md`（阅读顺序第 6 项）、根 `README.md`、`docs/README.md`、`experiments/README.md`、`memPed/README.md`、`Knowledge-Base/README.md`、`docs/project-architecture.md`、`paper/pearl-framework/datasets/README.md`、`retrieval-pilot/README.md`、80/200 题集记录与 Gold r02 实验 README（后两者只加注，不改原路径） |
| 未改动 | 25 个实验脚本、`resolved_manifest.yaml`、6B 工作包（含 `scoring-pipeline-spec.md`）、历史计划与阶段报告中的命令和路径——它们是冻结出处或进行中的方案 |
