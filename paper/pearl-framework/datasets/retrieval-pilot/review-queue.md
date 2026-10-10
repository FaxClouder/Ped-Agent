# Retrieval 试标复核清单

*8 个开发候选 intent 的独立复核任务 · status: plan · 2026-09-29*

初稿的全部 8 题已由独立子 Agent 根据原文复核并留下[逐题结论](subagent-review-2026-09-29.md)；[v3](pilot-intents-agent-reviewed-v3.json) 状态为 `agent_reviewed_preliminary`。试标运行可报告明确标注为初步的召回结果，不作为正式 200 题评估成绩。

| intent | 主层 | 独立复核的具体判定 | 当前状态 |
| --- | --- | --- | --- |
| 001 | 单来源事实 | Helbing 的“社会力=内在行动动机”是否足以回答；“并非物理施力”是否必须写入答案和 requirement；两个 bundle 是否等价 | 子 Agent 接受 v3 |
| 002 | 单来源事实 | Chraibi 所述后退运动与重叠是否都属于所问的“investigated models”模拟结果 | 子 Agent 接受 v3 |
| 003 | 数值／表格 | Shi Table 2 老年组 × Mean age (years) 的 `66.80 ± 5.4` 是否准确；不得擅自把 ± 解释为标准差 | 子 Agent 接受 v3 |
| 004 | 数值／表格 | Jin 的四种 corridor width 与 uni-/bi-directional 实验是否同一研究范围，单位是否完整 | 子 Agent 接受 v3 |
| 005 | 单篇多证据 | Li 文中的 adults／students 比较组是否为本题同一群体；峰值密度位置和速度调整两个 claim 是否各自必要 | 子 Agent 接受 v3 |
| 006 | 单篇多证据 | Pouw 的 landing 速度与占地压缩是否被所列正文 atom 充分支持；p1 替代 bundle 与 p13 bundle 是否真能独立互换 | 子 Agent 接受 v3；替代 bundle 已删 |
| 007 | 跨论文 | Geoerg 的残障混合人群与 Shi 的年龄混合人群不能合并为同一条件；两个研究结论是否各自保留场景限定 | 子 Agent 接受 v3 |
| 008 | 跨论文 | Pouw 的车站观测与 Shi 的受控实验是否分别由完整 bundle 支持；标题、参与者、地点和研究方式是否足够 | 子 Agent 接受 v3 |

每题复核记录需包含子 Agent 身份、时间、原文页、接受／修改／争议状态、修改前后版本和理由。争议先交另一子 Agent 仲裁；没有复核的题不进入初步可计分 Gold。若语义 Gold 改动，更新试标版本并复跑锚点验证，不覆盖原始初稿。人工审查在初步流程和结果确认后另行进行。
