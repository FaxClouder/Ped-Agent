# Retrieval 开发题试标

*四类题型的英文来源锚定试标 · status: current · 2026-09-29*

> 2026-10-07：新 8 题 Gold 已复制到规范位置 `memPed/knowledge/gold/pearl-adobe106/retrieval/pilot8/`（登记号 `qs-pilot8`，已并入 80 题开发集，状态 superseded），SHA-256 不变；本目录原件作为冻结出处保留。规则见 [评测规范](../../../../experiments/EVALUATION-STANDARD.md)。

本轮后续实验已调整为 [106 篇 Adobe-only 来源版本 -02](../retrieval-corpus/README.md)。[新 8 题 Gold](pearl-retrieval-dev-pilot-8-adobe106-gold.json) 已绑定这份清单，并保留 v4 的全部 intent、答案、必要事实、条件和证据组。文件 SHA-256 为 `768629fd65110e5dede9bb81e13a5ca5eb1de92e90baefaf12109d1b17ee9e7e`；修订号 1、日期、父 Gold 哈希、106 篇清单哈希、7 个实际引用来源的逐份哈希及冻结 child 快照哈希写在文件内。文件不能包含自身完整哈希，因此完整文件哈希记录在本页。实际 Adobe child 支持关系须按新排名盲化复核。

下述 v4 与 R1 仍属于旧 `-01` 的 108 篇全 PyMuPDF 临时切块试标；不作为新版语料成绩。

当前开发版本为 [Gold v4](pilot-intents-agent-reviewed-v4.json)，已完成[等价证据审查与原 R1 重算](equivalent-evidence-r1-v4-2026-09-29.md)：保留 v3 和原输出，补齐 Li 的 running 条件并统一使用新支持映射。@10 为 3/8、@20 为 5/8；仍是开发修订分析。下文 v3 和首次运行描述保留作版本沿革。

[pilot-intents.json](pilot-intents.json) 是 8 个新英文 intent 的**Agent 初标草案**，每类 2 个。它们依据 [固定原文快照](../retrieval-corpus/README.md) 形成，按 [标注规范](../../annotation/retrieval-guideline.md) 保存 query、答案、requirements、bundles、groups 和来源 atom。逐题语义复核事项见 [review-queue.md](review-queue.md)。

初稿已由两个子 Agent 逐题独立复核，并保留 [修订稿 v2](pilot-intents-agent-review-v2.json)、[复核记录](subagent-review-2026-09-29.md) 和 [初步 Gold v3](pilot-intents-agent-reviewed-v3.json)。v3 计入 80 题开发目标中的 8 个试标 intent，可用于流程测试和初步结果；不得标为人工 Gold 或正式 200 题评估集。`validate_pilot.py` 只检查结构和原文锚点能否回到指定 PDF；语义判断依据见复核记录。

[R1 初步流程结果](preliminary-r1-2026-09-29.md) 已生成；仅为 8 题试标在 108 篇原文上的 BM25 开发运行及子 Agent 支持核验，R2–R4 和正式评估尚未运行。

```powershell
.\.venv\Scripts\python paper/pearl-framework/datasets/retrieval-pilot/validate_pilot.py
.\.venv\Scripts\python paper/pearl-framework/datasets/retrieval-pilot/validate_pilot.py paper/pearl-framework/datasets/retrieval-pilot/pilot-intents-agent-reviewed-v3.json
```

本轮试标使用 7 份不同 PDF；两道跨论文题分别要求两个来源在同一完整组内共同出现。Shi 等人 Table 2 的老年组均龄及 ± 数值已对照原 PDF 第 4 页表格；任何复核修订都要保留初稿版本和理由。

106 篇 Adobe child 上的新 R1–R4 运行、盲化支持映射及 K=1/5/10/20 的初步开发成绩见[独立索引实验记录](../../../../experiments/pearl-index-106-adobe-20260929/README.md#8-题-adobe-only-开发对照)。R4 在本地 reranker 模型下载并核验后独立补跑；旧 108 篇全 PyMuPDF 的 R1 数值不与新结果合并比较。
