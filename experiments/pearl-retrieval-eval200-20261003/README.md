# PEARL Retrieval：200 题发布与独立评价

*阶段 C 完整输入冻结与阶段 D 固定执行入口 · status: current · 2026-10-03*

本目录保存阶段 C 独立保管流程，复用[阶段 B 入口](../pearl-retrieval-eval-entry-20261003/README.md)。当前交付状态以[阶段 C completion](../../outputs/pearl-retrieval-eval200-release-20261003-03/stage-C-completion.json)为准。发布核验不代表已运行检索，不代表正式评价已完成。原 B、开发 Gold r02 和旧输出保持原样。

## 发布与访问

先做所有封存文件 byte hash／只读核验与实际源文献、CanonicalDocument、索引、模型、代码、协议、统计、依赖、硬件和角色范围核验，生成 `status=preexport_inputs_verified` 候选收据。另由独立核验者校验候选 SHA 和其文件绑定后，保管者才通过既有 `custody.export_queries` 导出200条 query-only。随后冻结含输入视图的最终 release，固定外部 SHA pin 并执行真实 `runtime.py --verify-release-only`；不能将最终门禁说成导出前已通过。

| 角色 | 实际范围 |
| --- | --- |
| 独立保管者 | 封存 Gold 只用于既有 custody 导出；作者／QC 文件只 byte hash，旧判断不提供给评审者 |
| 检索执行者 | query-only contract／queries、5条开发预热、最终 release 和独立 pin、冻结索引与模型；不得读取 Gold 内容、旧判断或执行 custody |
| 独立实际 child 评审者 | D 检索完成后逐题中性包；不提供排名、方法、分数、旧判断，不能借 PDF 补 child |

独立 Agent 上下文与 subprocess 输入契约承担流程隔离。当前共享 Windows 账号与 unrestricted filesystem，并无操作系统 ACL 安全隔离；现有封存只读属性保留。硬件、目标 output、角色、开发 r02 和封存只读属于外部发布核验，B 的 runtime 最小门禁并不替代这些核验。

完整发布位于 [release 目录](../../outputs/pearl-retrieval-eval200-release-20261003-03/release.json)，包含核心依赖实际非缓存文件、全部安装包版本／METADATA／RECORD／WHEEL 字节、全部实际模型文件和索引来源。CanonicalDocument 与 PDF 身份逐项核验。Gold／审查身份只作为不透明 SHA 绑定，不进入运行者的文件输入集合。

## 命令与状态

保管准备脚本 `prepare_release.py` 无参数只生成候选；候选独立通过后使用 `--approved-candidate-sha256 <audited-SHA>` 生成最终 release。脚本仅限保管者；已有输出一律拒绝覆盖。具体运行命令和预设统计见[预注册](preregistration.md)。实际 CLI 门禁命令、退出码与结果见[收据](../../outputs/pearl-retrieval-eval200-release-20261003-03/gate-command-receipt.json)。

阶段 D completion 必须同时具备800首遍题×方法单元、三遍600 timed query、首遍密封、200份实际 child 独立审查／唯一选择／共同映射、3,200前缀评分、48总体指标独立复算、统计、失败与成本报告；任何一个缺失都不能称正式评价完成。
