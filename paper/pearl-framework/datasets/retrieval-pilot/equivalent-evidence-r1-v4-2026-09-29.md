# Retrieval 试标等价证据与 R1 v4 重算

*8 题开发试标的修订分析；子 Agent 审查，非人工 Gold · status: current · 2026-09-29*

本轮在原 9,491 个 child 和原 R1 排名上，生成 [Gold v4](pilot-intents-agent-reviewed-v4.json) 与新版支持映射。[v3](pilot-intents-agent-reviewed-v3.json)、[原始结果记录](preliminary-r1-2026-09-29.md) 和原 R1 目录均保留。没有重新检索、调参或改变 PEARL 指标，也没有运行 R2–R4。此结果仍是 8 题开发修订分析，不是正式四方法对照或 200 题封存评估成绩。

## 审查与登记

三个子 Agent 只读 v3、冻结 PDF 和隐藏方法／排名／分数的原 Top-20 池；分别核验来源与实际 child 支持，原文 SHA-256 均一致。提示要求核验事实、全部必要条件和最小联合路径，禁止阅读排名和成绩。模型具体 revision 未在审查产物中暴露，未发生人工审查。机器可读决策见 [决策记录](equivalent-evidence-decisions-v4.json)。

| intent | 审查者 | 新登记原文页／atom | 决定 |
| --- | --- | --- | --- |
| 002 | `/root/review_chraibi` | Chraibi p2 a3、p9 a4 | 两处各包含不稳定区域及后退／重叠结果，各为独立替代 bundle；p9 是本轮发现后继续审定的候选 |
| 004 | `/root/review_jin` | Jin p2 a2、p16 a3、p3 a4–a8 | p2/p16 为完整陈述；p3 Table 2 的四个单元格与单双向条件共同成 bundle，表格已由子 Agent 渲染视觉核对 |
| 005 | `/root/review_li` | Li p11 a3、p2 a4 | p11 是速度调整的等价结论；p2 提供 running 条件，旧 p12 和新 p11 路径均须联合该条件 |

v4 共 34 个 atom。query、reference answer、requirement 的 claim/scope/数量、evidence group、intent/family/split 均不变。其余五题的语义与映射继承 v3 审查。

**Li 包含遗漏条件修复，不只是等价支持扩充。**初审曾建议凭同源实验身份认定 running；经主 Agent 按 [指标 §2.3](../../layer-1-retrieval/metrics.md) 提出仲裁，子 Agent 撤回该判断。r2 从 `[a2]` 修订为 `[a2,a4] OR [a3,a4]`。第 11 页两个 child 可各自支持 a3，但不能单独满足 r2；第 12 页原路径采用同一规则。r1 两个原 child 均实际含 highly motivated 条件，无须补 atom。因 v3 漏编码已要求的条件，**原记录的数值不能继续解释为严格完整证据得分的保守下界**；原产物保留供追溯。

最小支持路径（前缀均为对应论文的 source ID）：

| intent / atom | child 后缀；分号表示 OR |
| --- | --- |
| 002 a3 | `p0002:w000280` |
| 002 a4 | `p0009:w000280` |
| 004 a2 | `p0002:w000700` |
| 004 a3 | `p0016:w000560` |
| 004 a4–a8 | 每个 atom 均由 `p0003:w000000` 支持 |
| 005 a3 | `p0011:w000140`；`p0011:w000280` |
| 005 a4 | `p0002:w000000` |

拒绝理由包括：Chraibi p2 前两块的前人研究背景不能拼成本研究结论；Jin p2 综述中的不同研究宽度不能拼成目标宽度；Li motion activation/time gap 不能替代 relaxation-time 比较，既往 running children / walking adults 不构成本研究同条件证据。已接受 singleton 的严格超集路径不重复登记。本次新发现的 p9/p3 候选均已继续核定；没有遗留本轮已识别的未决候选。未声称穷尽全语料替代支持，21–100 名未完成支持审定。

## 同一 R1 排名的 v4 分数

| K | 完整证据组命中 | BestGroupCov | CompleteMRR | AnySourceHit | AnyPageHit |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1/8 | 0.1250 | 0.1250 | 6/8 | 1/8 |
| 5 | 2/8 | 0.4375 | 0.1875 | 7/8 | 5/8 |
| 10 | 3/8 | 0.5000 | 0.203125 | 7/8 | 5/8 |
| 20 | 5/8 | 0.6875 | 0.219685 | 8/8 | 7/8 |

| intent | @10 | @20 | 首次完整排名（v3 → v4，限 Top-20） |
| --- | ---: | ---: | --- |
| 001 | 0 | 1 | 13 → 13 |
| 002 | 1 | 1 | 2 → 2 |
| 003 | 0 | 0 | 未完成 → 未完成 |
| 004 | 1 | 1 | 5 → 1 |
| 005 | 0 | 1 | 17 → 18 |
| 006 | 1 | 1 | 8 → 8 |
| 007 | 0 | 0 | 未完成 → 未完成 |
| 008 | 0 | 0 | 未完成 → 未完成 |

Jin 的 p2 完整支持在第 1 名。Li 的新结论在第 7、14 名，原结论在第 17 名，但 running 条件在第 18 名；这解释了为何加入等价结论仍未使 @10 命中。@10/@20 成功数未变，不代表支持结构或完成排名未变。

## 产物与复现

本地另存目录为 [R1 v4 重算](../../../../memPed/knowledge/pearl-retrieval-pilot-r1-v4-2026-09-29-01/rescore-manifest.json)，包含 [支持映射](../../../../memPed/knowledge/pearl-retrieval-pilot-r1-v4-2026-09-29-01/support-mapping-agent-reviewed-v4.json)、[逐题分数](../../../../memPed/knowledge/pearl-retrieval-pilot-r1-v4-2026-09-29-01/preliminary-scores-v4.json) 和哈希清单。清单记录 v3、原 R1 六个文件、v4、决策、映射、分数及生成／评分代码的 SHA-256。

[构建脚本](build_reviewed_v4.py) 校验原始输入，应用审定决策，逐条比对排名／盲池与 child 库的文本及哈希，运行来源锚点校验，再调用 [评分器](score_bm25_pilot.py)。评分公式未变；新增 CLI 参数仅用于显式选择 Gold、mapping 和独立输出，并阻止 query 改动及覆盖不同的已有分数。

在仓库根目录使用一个**尚不存在**的输出目录复现：

```powershell
.\.venv\Scripts\python paper/pearl-framework/datasets/retrieval-pilot/build_reviewed_v4.py memPed/knowledge/pearl-retrieval-pilot-r1-v4-reproduction-01
.\.venv\Scripts\python -m pytest paper/pearl-framework/datasets/retrieval-pilot/test_rescore_pilot.py -q
```

下一步 R2–R4 必须复用相同 child 文本与 v4 Gold，并将新返回的证据纳入统一盲化支持审查；本轮映射只覆盖 R1 Top-20，不能直接将其他组未审过的 child 视为无支持。若发现新支持或条件错误，统一另存版本并重算所有已运行组。80/200 题扩建仍待流程及初步对照结果确认。
