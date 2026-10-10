# PEARL Layer 3 Answer 开发实验

*固定生成模型、独立答案参考与正确性评价 · status: current · 2026-10-04*

执行[阶段A–D计划](../../docs/superpowers/plans/2026-10-04-pearl-answer-next-session.md)，仅消费冻结的80题开发集和Layer 2保存正文。原20题是80题子集，不是新增样本；不重复Retrieval/Evidence，不继续Layer 4/5，不要求人工审查。

## 实际状态

阶段A–D已完成，正式Agent开发评价，human_verified=false。80题参考resolved、80个独立原文oracle eligible；40锚点实际校准AC40/40、claim93/93、五哨兵全通过。400逻辑单元全部真实首次成功：C100记录精确复用于D，D新请求300；语义unknown及技术失败0。

主要结果和局限见[中文分析](answer-analysis-2026-10-04.md)。四实际臂Strict为60/58/57/61（各N=80），oracle73/80；四项实际臂比较未显著，oracle−A1-8192为+15个百分点、Holm p=0.009155。80题是开发评价，不作为新的独立200题结果。原20题不是额外独立样本。

400单元413产物绑定独立复算通过；60项实验测试通过。科学输入12项与1154旧资产原SHA保持一致；Evidence734项仅docs/README维护导航允许差异另列。三个fork_turns=none角色因线程限制复用，真实背景与包级隔离局限已披露，不声称全新评审身份。C双审100、D二审固定抽检60/300，全部400有已校准主审实际阅读。保留全部原裁决与10项分歧独立裁决。

用户指定DeepSeek V4.1 Flash，依[官方说明](https://api-docs.deepseek.com/news/news260910/)使用model ID `deepseek-flash`。固定nonthinking、temperature0、2048输出上限、timeout120秒、SDK retries0；seed未声明支持，未发送。真实研究请求均通过参考冻结、校准、能力与连接门禁。连接预检另1次105输入/8输出；研究400次usage总计1,619,528 tokens、finish stop400。来源绑定研究生成费用估算USD0.270491，实际账单未返回，Agent评审费用不可获取且不纳入此数。

## 已实现入口

| 文件 | 职责 |
| --- | --- |
| [prepare.py](prepare.py) | 科学输入SHA保护、320query/context包与独立参考来源包、评估标签隔离 |
| [generate.py](generate.py) | 复用现有SDK直接适配、显式技术尝试、原始答案/响应元数据、真实前置门禁和精确复用 |
| [review.py](review.py) | 答案盲包及实际语义判断的显式版本选择 |
| [score.py](score.py) | 独立语义标签计分、AC/Strict/Coverage/Integration/数值/四态与五项配对统计 |
| [verify.py](verify.py) | 不调用score核心的保存产物独立复算 |
| [validate_references.py](validate_references.py) | 精确引文、原文字节段、oracle预算及实际独立复核身份门禁；结构验证不替代语义判断 |
| [protocol.md](protocol.md)、[rubrics.md](rubrics.md) | 冻结五臂、生成/评审与统计口径 |
| [generator-config-r01.json](generator-config-r01.json) | 无密钥固定模型配置；与请求前冻结的输出原件逐字节相同，收尾复制至Git可维护的实验目录 |
| [scoring-schema.md](scoring-schema.md) | 实验内评分与绑定schema |
| [execution-ledger.md](execution-ledger.md) | 实际阶段状态、限制作恢复入口 |
| [阶段A](stage-A-report.md)、[阶段B](stage-B-report.md)、[阶段C](stage-C-report.md) | 各阶段完成证据；D完整结果见中文分析 |
| [中文分析](answer-analysis-2026-10-04.md) | 正式80题开发结果、分层/配对/四态/数值/费用与局限 |

原始产物见[输出目录](../../outputs/pearl-answer-dev80-20261004-01/)，包括参考冻结、校准、真实生成、版本化盲评、评分、独立复算、精确复用与运行审计；最终[交付清单](../../outputs/pearl-answer-dev80-20261004-01/delivery-manifest-r01.json)绑定全部本轮文件和当前维护导航。事实审查与收尾机械审查采用各自r02通过结论；r01保存了审计方已纠正的舍入及哈希口径误报，不是结果修订。密钥仅保存在被Git忽略的本地.env，不加入配置快照或清单。既有Gold、排名、科学输出和旧计划未改；没有commit/push/merge或清理。

## 已执行验证命令

[输出目录当前交付入口](../../outputs/pearl-answer-dev80-20261004-01/DELIVERY.md)单列最终状态；输出目录旧README保留离线准备时的原始状态，不覆盖。

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python -m pytest experiments/pearl-answer-dev80-20261004 -q
.\.venv\Scripts\python outputs/pearl-answer-dev80-20261004-01/run_generation_stage_r02.py stage20
.\.venv\Scripts\python outputs/pearl-answer-dev80-20261004-01/run_generation_stage_r02.py stage80
.\.venv\Scripts\python outputs/pearl-answer-dev80-20261004-01/assemble_score_stage_r01.py stage20
.\.venv\Scripts\python outputs/pearl-answer-dev80-20261004-01/assemble_score_stage_r02.py stage80
```

上述是实际执行记录，返回码均0；研究入口及结果文件独占创建，不能覆盖原产物重跑。根角色最新验证为60 passed in 0.64s。复核保存结果可运行verify.py并指定新的验证输出文件；不需要再调用API。最终输出清单、命令和代码/config快照保存于输出目录。

工作已止于Layer 3，不继续Layer 4/5或新200题。阶段C诊断没有触发科学规则或生成条件调整。
