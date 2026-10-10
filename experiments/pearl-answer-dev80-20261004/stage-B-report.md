# Layer 3 阶段 B 校准报告

*固定规则下的 Agent 校准与实现验证 · status: current · 2026-10-04*

阶段 B 已完成。40 个源材料支持的锚点覆盖四个层各 10 个；独立预期标签先于实际 judge 冻结。实际 judge 的 AC 完全一致为 40/40，claim 标签一致为 93/93；缺条件、比较方向反转、单位错误、替代组拼接和缺整合五类哨兵均通过。独立复算得到相同结果，没有因校准成绩调整评分规则。

参考构建者、预期裁决者、实际 judge 使用不同的 fork_turns=none 角色。运行环境限制新线程数量，因此复用既有角色，其既往协议背景和参考构建经历已披露；不声称全新评审身份或独立人群性能。实际 judge 未接触锚点预期、哨兵身份或研究答案。

DeepSeek V4.1 Flash 使用官方 model ID `deepseek-flash`，OpenAI-compatible 接口，thinking disabled，temperature=0，输出上限 2048；官方未声明 seed 支持，故不发送。真实非研究连通测试首次成功。研究生成将绑定配置、参考、校准、代码和输入哈希，保留每次技术尝试及首次成功答案。

最新窄范围代码审查已清除两个入口门禁缺口：请求前验证完整唯一矩阵，以及 C→D 复用时验证同一单元身份。实际矩阵为 20题100单元和80题400单元，60项实验测试通过。未运行研究生成，未重复 Retrieval/Evidence。

证据：本地输出目录中的 `calibration/calibration-gate-r01.json`、`calibration/independent-calibration-audit-r01.json`、`code-review-r03.json` 和 `testing/code-review-fulltests-r03.json`。阶段 C 将先执行原始20题，完成盲评、评分、独立复算和中文诊断后进入阶段 D。
