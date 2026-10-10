# Layer 3 阶段 A 输入与参考冻结

*实际完成的输入盘点、参考/oracle及生成协议 · status: current · 2026-10-04*

阶段A完成，真实研究答案尚未生成。80个原开发intent、原20题诊断名单、320固定实际context及L2标签身份核验一致；734个Evidence交付文件733一致，仅历史docs/README导航快照差异披露，冻结科学文件及1154既有资产绑定一致。没有重跑Retrieval/Evidence。

两个fork_turns=none独立角色各构建40题并交叉复核40题，实际阅读来源及完整oracle正文。候选保存后，两种源标签序列化格式与特殊token计数统一为明确新版本，精确原文字节段不改；独立复核消费统一后的完整字符串。028合法离散数值、055阈值措辞、071缺机制正文三处修订均另存，并由与该修订作者不同的角色核验。最终80参考resolved、80oracle eligible，预算全不超过8192。结构脚本验证引文子串、源库/原始JSONL区间、UTF8正文段、预算、候选及复核SHA绑定；语义结论由实际独立阅读产生，不是结构脚本生成。

独立性的具体限制：角色在实施前知道通用实验协议、臂名称和仓库导航的历史总体信息，但未见逐题旧答案、策略成绩或被测研究答案。工具线程总量限制使角色在隔离任务内复用；基础参考交叉复核与后续修订核验链分别记录，不能声称所有环节均由全新身份完成。见实际provenance与执行记录。准备角色因看到一个旧答案，被排除在参考构建之外。

用户指定DeepSeek V4.1 Flash，依官方文档配置deepseek-flash、OpenAI兼容地址https://api.deepseek.com。真实非研究连接预检首次成功，input105/output8，finish stop；密钥只在本地忽略的.env。生成固定nonthinking、temperature0、2048输出上限、timeout120、SDK重试0，seed未获得支持依据故不发送。最长完整请求采用UTF8字节保守入窗界并保留2048输出，满足文档1M窗口，实际计费token保留API响应，BGE不等同provider token。

四个实际臂和Aref共400个逻辑输入。每臂80题；原20题是子集，不声称100题。完整请求SHA、上下文SHA、配置、参考及代码快照通过新清单绑定，生成包只消费query/context。研究请求须通过40锚点校准门禁，阶段C/D尚未启动。

## 保存证据

- [冻结参考与oracle](../../outputs/pearl-answer-dev80-20261004-01/reference-freeze-r01.json)
- [所选版本与复核来源](../../outputs/pearl-answer-dev80-20261004-01/reference-selection-r01.json)
- [输入清单](../../outputs/pearl-answer-dev80-20261004-01/input-manifest.json)
- [Evidence SHA核验](../../outputs/pearl-answer-dev80-20261004-01/evidence-sha-audit.json)
- [模型非秘密配置](../../outputs/pearl-answer-dev80-20261004-01/generator-config-r01.json)
- [预检原始响应](../../outputs/pearl-answer-dev80-20261004-01/preflight/preflight-connection-r01.json)

冻结CLI实际exit0，返回intent_n80/resolved_n80/oracle_eligible_n80。原科学产物未覆盖，不要求人工审批；报告后继续阶段B。
