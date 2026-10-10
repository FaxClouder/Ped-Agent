# Retrieval 试标子 Agent 复核记录

*8 个英文开发候选题的来源语义复核 · status: current · 2026-09-29*

复核对象为 [初稿](pilot-intents.json)，修订保存在 [v2](pilot-intents-agent-review-v2.json)，用于流程测试的子 Agent 复核版本为 [v3](pilot-intents-agent-reviewed-v3.json)。复核由 `pilot_semantic_review_a`（001–004）和 `pilot_semantic_review_b`（005–008）只读检查原始 PDF 完成；这是 **Agent 复核，不是人工审查**。`validate_pilot.py` 另行检查结构、哈希及锚点，但不替代语义判断。

| intent | 子 Agent | 原文 PDF 页 | 初稿问题与处置 | v3 状态 |
| --- | --- | --- | --- | --- |
| 001 | pilot_semantic_review_a | Helbing 1–2 | 第 2 页替代证据原子缺少语境；改为“非环境身体施力”与“具体行动动机”共同构成 bundle，未增设题目未问的必要项 | 接受 |
| 002 | pilot_semantic_review_a | Chraibi 1 | 后退和重叠仅在不稳定区间有原文限定；查询、答案、requirement 和证据 bundle 均加该条件 | 接受 |
| 003 | pilot_semantic_review_a | Shi 4 | Table 2 的老年组 Mean age (years) 为 66.80 ± 5.4；未解释 ± 的统计含义 | 接受 |
| 004 | pilot_semantic_review_a | Jin 1–2 | 四种走廊宽度及米单位与单／双向实验一致 | 接受 |
| 005 | pilot_semantic_review_b | Li 1、11–12 | 峰值密度比较对象为 adults，速度调整比较对象写为 students；删去“students/adults”为同一群体的暗示 | 接受 |
| 006 | pilot_semantic_review_b | Pouw 10–13 | 删除错误的第 1 页替代 bundle；区分式 (12) 的几何上界 `min{f1(N), f2(N)}` 与式 (14) 压缩比的分母 `f1(N)`；按后者重写题目和答案 | 接受 |
| 007 | pilot_semantic_review_b | Geoerg 1；Shi 1、4 | Shi 年龄混合情形限定为中学生与老年人，并加入第 4 页原文证据 | 接受 |
| 008 | pilot_semantic_review_b | Pouw 1；Shi 1、4 | 补入 Shi 实验地点，并把锚点扩至完整学校、城市、省份和国家 | 接受 |

v3 的 `agent_reviewed_preliminary` 只表示这 8 题可用于开发阶段的流程测试和初步计分。后续人工审查用于开发集难例与调优，须另存版本；如改变 Gold，所有方法在同一新版下重算。200 题独立评估集尚不存在，本记录不提供正式评估资格。
