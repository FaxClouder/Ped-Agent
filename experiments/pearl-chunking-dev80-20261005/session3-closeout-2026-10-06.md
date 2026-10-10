# PEARL 切片 E1 收尾与 E3 评分衔接

*r07 配对统计、实际差异案例与离线评分兼容 · status: current · 2026-10-06*

本次仅收尾 E1，并核验 E3 将使用的评分入口。新交付为
[`outputs/pearl-chunking-dev80-20261006-06`](../../outputs/pearl-chunking-dev80-20261006-06/handoff.md)。
候选仍为 `C2-L384-O0-M0`、`C3-L256-O0-M0`，基线仍为 `B0-regex320-overlap48-M0`。
原冻结规则、r07 支持图、索引、排名与 P0 上下文均保留原身份。
开发入选不等于显著优胜，也不等于独立验证。下一会话只从本次[唯一交接入口](../../outputs/pearl-chunking-dev80-20261006-06/handoff.md)开始。

## 交付链与支持口径

| 资产 | 当前用途 |
| --- | --- |
| [原 session 计划](../../docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md) / [公共协议](protocol.md) | 保留原冻结研究变量、候选规则、三值与统计规则 |
| [-05 E1](../../outputs/pearl-chunking-dev80-20261005-05/handoff.md) | 13 配置 × 80 意图的真实索引、R1–R4 排名与两预算 P0；r05 统计是历史结果 |
| [-06 阻塞交接](../../outputs/pearl-chunking-dev80-20261005-06/handoff.md) | 当时未冻结候选，E3 未执行；保留当时状态 |
| [-07 r06/r07](../../outputs/pearl-chunking-dev80-20261005-07/handoff.md) | 可见全集盲审、针对性裁定、统一重算与候选冻结 |
| [本次收尾 manifest](../../outputs/pearl-chunking-dev80-20261006-06/delivery-manifest.json) | r07 新统计、案例、评分一致性、命令日志与当前代码身份 |

r07 的证书判定优先；证书不完整时使用已审查的最短支持备选和裁定片段。
已审全集内没有完整支持备选才可判 no；未裁定片段、新可见内容超出全集时仍为 unknown。
不存在“同一文献”“关键词命中”或父图扩展即自动支持的规则。本次没有新增语义判断。
4K CGC 与 R4 CEGR@10 的 2,080 个选择单元均无 unknown；8K 的 1,040 个单元仍有 136 个 unknown，不能强行转为 no。

## r07 配对结果

| 配置 | 4K CGC yes/80 | R4 CEGR@10 yes/80 | 8K yes / unknown /80 |
| --- | --- | --- | --- |
| B0 | 50 | 60 | 63 / 10 |
| C2-L384 | 57 | 63 | 67 / 7 |
| C3-L256 | 56 | 56 | 59 / 20 |
| C2-L256（相邻未入选） | 55 | 55 | 60 / 19 |

统计单位为 80 个 intent，按题型分层、共享配对抽样，seed=20261005，10,000 次 bootstrap，95% percentile 区间（numpy linear）。
完整统计覆盖全部 13 配置和三个面板，见[配对统计](../../outputs/pearl-chunking-dev80-20261006-06/statistics-e1-r07-closeout-r01.json)。
Holm 家族定义为 12 个非基线配置 × 两个完全二值的选择面板，共 24 项对 B0 的精确双侧 McNemar 检验；候选间比较另列为探索性。
协议没有预先写明 Holm 家族大小，本次明确该联合家族，不能称为事先登记的 24 项检验。8K 有 unknown，不执行二值检验。

| 对 B0 比较 | 配对差值（百分点） | 95% 描述性区间 | 确定增益/损失 | 原始 p / Holm p |
| --- | --- | --- | --- | --- |
| C2-L384 4K | +8.75 | [3.75, 15.00] | 7 / 0 | 0.015625 / 0.375 |
| C3-L256 4K | +7.50 | [0.00, 15.00] | 8 / 2 | 0.109375 / 1.000 |
| C2-L384 CEGR@10 | +3.75 | [-3.75, 11.25] | 6 / 3 | 0.507813 / 1.000 |
| C3-L256 CEGR@10 | -5.00 | [-13.75, 2.50] | 4 / 8 | 0.387695 / 1.000 |

C2 的 4K 描述性区间虽在零以上，但经多重比较校正没有显著优势；同一 dev80 又用于选择，仍有选择偏差。
C3 是后续不同边界机制的对照，不是对 B0 各面板全面提升。
C3 对 C2-L256 的 4K 仅净增 1/80（2 增、1 损，精确 p=1）；不能将排序差距解释为机制已被确认。
8K 对 B0 的可能差值范围分别为 C2 [-7.50, 13.75]、C3 [-17.50, 20.00] 个百分点，包含 unknown；这些范围不是置信区间。

## 关键差异与限制

[完整差异清单](../../outputs/pearl-chunking-dev80-20261006-06/paired-difference-cases-r07-r01.jsonl)保存候选对 B0、C3 对 C2-L256 的全部三面板状态差异；
每条绑定需求、r07 map、评分明细、ranking/context hash。P0 案例另保存实际 final 可见单元、源区间、支持备选的可见性、reviewer 与 caveat。
这里分析现有判定与可见性，不新增独立盲审，也不把相关性写成已隔离的 chunker 因果。

- `pearl-dev-046`：4K 中 C3 yes，B0/C2-L384/C2-L256 no。r1 的最短备选描述非空间模型与各流行人数；r06 审查注明 temporal 仅隐含。保留该 caveat。若这一条改为 no，C3 与 C2-L256 的 4K 打平，仍按 CEGR@10 的 56 对 55 入选；不能据此声称无审查敏感性。
- `pearl-dev-057`：4K 中 C2-L256 yes，C3 no。两者 r2（速度随时间变化与同步率无直接关系）均由证书支持；差异在 r1 的上楼半圆/下楼直线轨迹，C3 已审可见内容没有完整备选。不能用 r2 已满足补齐 AND 整组。
- `pearl-dev-068`：4K 中 C3 yes，C2-L256 no。两者 r1（有限信息下选择性知觉）均由证书支持；C3 另完整保留 r2（缺少自身疏散信息而跟随他人线索的动机）的证书，C2-L256 的已审可见内容没有 r2 完整备选。仅列出 decision stage 不充分。
- `pearl-dev-018`、`pearl-dev-077`：C3 在 4K 对 B0 的两条确定损失。018 需要跨方法、群体、布局和情境的可迁移性仍待建立，B0 证书 yes、C3 已审可见内容无完整备选。077 需要逆行人数/总疏散时间与同流量比上下坡主流方向两项事实，B0 两项证书 yes、C3 两项均无可见完整备选。案例保留逐需求支持差异，不能将一项命中代替 AND 完整性。

预算转移见[expanded→final](../../outputs/pearl-chunking-dev80-20261006-06/budget-transitions-r07-r01.jsonl)，
只在同配置、意图、预算和主面板内比较；expanded yes→final no 才是确定可见支持损失，yes→unknown 单列为可能损失。
[r06→r07 转移](../../outputs/pearl-chunking-dev80-20261006-06/r06-r07-status-changes-r01.jsonl)保留裁定影响范围，未改任何 4K 单元的实际上下文。

## 评分适配与验证范围

[score.py](score.py)新增轻量分派：没有审查字段时沿用证书逻辑；有 `visible_universe_review` 时延迟导入并复用 `e1_visible_review.support_r06`（包括 r07 裁定）。
[evaluate.py](evaluate.py)的 Layer 1 同样复用该判断；失败保持显式 unknown，审查数量由实际 mapping 计算，输出 schema 为 `source-score-review-bridge-v2`。
每份 mapping/context/ranking 的 hash 在一次评分中只计算一次，判定输入不变。没有改公共 Contracts、检索、组装或 tokenizer。

[一致性回执](../../outputs/pearl-chunking-dev80-20261006-06/scoring-parity-r01.json)逐条比较 13 配置的 22,880 个旧入口评分与 r07 明细（支持、依据、完整性、覆盖与绑定），
另用独立区间实现复核已有 P0 raw/expanded/final 共 6,240 个阶段单元。只核验保存的 P0，不能冒充 P1/P2 或真实 E3 验证。
输入保全见[哈希回执](../../outputs/pearl-chunking-dev80-20261006-06/preservation-inputs-r01.json)：
r07 全部 489 产物、-05 全部 430 产物及 -06 所列输入重新 hash；两处 score/evaluate 当前代码变化单列，旧输出内容不变。
实际测试及命令退出码以交付 manifest 和日志为准。先前失败/中止尝试留档，不计为成功。

## 下一会话与剩余事项

唯一入口是本次 [handoff.md](../../outputs/pearl-chunking-dev80-20261006-06/handoff.md)。
E3 尚未开始；下会话先检查新 manifest、r07 冻结、评分代码与 tokenizer 身份。
仅用 B0/C2-L384/C3-L256 在 -05 的同一 R4 排名，比较 P0/P1/P2 × 4K/8K，分别保存 Top100 主面板和 Top10 诊断面板。
超出 r07 已审全集的新增可见内容保持 unknown，影响结论时按协议补审并新增版本。
E2 恢复策略尚未冻结；E3 完成该冻结后停止，不运行 E2/E4/E5、不生成答案、不触碰旧 200 题。
