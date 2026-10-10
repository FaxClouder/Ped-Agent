# PEARL calibration run notes

*仅校准阶段的盲化逐包评审记录；status: current。*

## 实际运行身份

- 实际产品：Codex 桌面应用中的当前助手会话，通过本地 PowerShell/Python 工具读写工作包；未调用外部模型 API，未联网。
- 基础模型说明：开发者指令将当前助手描述为基于 GPT-6 的 Codex。精确模型名/模型 ID 未向当前助手暴露，记为 null；不能确认具体为 sol6.1。
- 实际推理强度：运行时未暴露，记为 null。README 记载的 sol6.1、medium 属于指定配置说明，未将其冒充为已验证的实际运行配置。
- provider usage、费用和账单信息：未暴露，null。

## 时间与会话范围

- 开始记录时间：2026-10-07 00:04:58 MDT（America/Denver，UTC-06:00）；对应 2026-10-07 06:04:58 UTC。
- 结束时间：2026-10-07 00:13:31 MDT（America/Denver，UTC-06:00）；对应 2026-10-07 06:13:31 UTC。
- 全部在当前一个对话/线程中完成；未创建其他对话、线程或子代理。
- 当前线程按 manifest index 顺序处理：L3-calibration-001 至 L3-calibration-040；L4-answerability-cal-01 至 L4-answerability-cal-40；L4-grounding-cal-01 至 L4-grounding-cal-40；L4-factuality-cal-01 至 L4-factuality-cal-40；L4-behavior-cal-01 至 L4-behavior-cal-40。
- 没有子代理 fork，fork_turns 不适用；没有声称使用 fork_turns=none 的独立子代理。每个包的判断只采用本包材料和对应规则，未根据其他包内容或先前判断调整标签。

## 阅读边界

- 除本工作目录外实际打开/读取的文件：无。
- 未打开 outputs/、experiments/、memPed/、docs/ 或任何 expected、comparison、calibration-gate、score 文件；未进行仓库搜索或记忆文件检索。
- 会话启动时系统已自动提供仓库贡献说明和历史记忆摘要；未打开这些摘要所提及的任何文件，未使用这些会话背景补充评审证据。
- 本目录内阅读：README.md、calibration/manifest.json、200 个 calibration/packets/*.json、五个对应 calibration/system-prompts/*.md、validate_responses.py；最后重新读取响应进行结构、逐字引用及 ID 校验。

## 方法、错误及修正

- 完整阅读 README 后开始。五份对应规则均完整阅读，包括各自 Output format。按 manifest 的 index 顺序读取和判断；工具读取可一次显示若干连续包，标签均为逐包阅读后的语义判断。
- Python 仅用于文件读取、原文复制、已明确逐项判断的 JSON 序列化写入和校验；没有关键词匹配、正则、启发式标签生成或标签推断代码。
- 所有响应采用 UTF-8、无 BOM，每个文件仅一个 JSON 对象。identity_field/identity_value 从各自包原样写入。
- Layer 3 逐项记录全部 targets、conditions、claims、numeric；Layer 4 逐项保留原文事实片段、实际引用和证据。纯拒答与 context 缺口元声明不作为领域事实 claims。
- 首次控制台读取 L3-calibration-001 至 010 时，读到 005 输出因默认 GBK 无法编码 U+2011 而失败。随后将 Python stdout 配置为 UTF-8，重新完整读取 005 至 010；失败读取没有生成标签或响应。
- 较长 manifest 和 L3-calibration-021 至 030 的工具显示出现截断。manifest 随后按原顺序解析并完整显示全部 index 项；相关被截断包分段重新读取，其中 026 再次完整显示。均在判定/写入相关响应之前补齐阅读。
- 未覆盖开始前已有响应（responses 目录初始无文件）；新响应以独占创建方式写入。写入后无响应重做、无格式修改、无语义标签修改。

## 完成验证与停止点

- 在工作目录执行：python validate_responses.py calibration。
- 结果：phase=calibration，packets=200，valid=200，problems=0，first_problems=[]，退出码 0。
- 额外只读校验：responses JSON 文件数 200；Layer 3 全部规定 ID 与数值目标 ID 齐全；Grounding 的 text、other_occurrence_texts、citation_text、context_evidence.quote 均来自对应包原文，实际引用字符串完整；Factuality 的全部 claim_id 和原文 fact_evidence.quote 齐全。该检查无问题，不产生或修改任何标签。
- 完成文件：200 个 calibration/responses/<job_id>.json 与本 run-notes.md。
- 停止于校准评审交付。没有导入、比对、计算校准成绩、判断校准门槛或进入研究阶段。
