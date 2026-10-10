# PEARL Layer 2 Evidence 开发评估

*固定 R4 Top-10 的上下文组装与实际文本充分性评价 · status: current · 2026-10-04*

本实验执行[阶段计划](../../docs/superpowers/plans/2026-10-04-pearl-evidence-next-session.md)，复用冻结开发排名与 Gold r02；不重复 Retrieval，不执行新的200题 Evidence 或 Layer 3/4。正式内容验收遵循[现行研究标准](../../docs/research-review-standard.md)，不要求人工审查；开发用途与正式 Agent 评估分别说明。

阶段A–D已完成，正式 Agent 开发评估和[完整中文分析](evidence-analysis-2026-10-04.md)已交付。完整80题的320份最终上下文、398份不同实际盲包及1,280个步骤绑定均完成审查与独立复算；没有人工审查门槛。分阶段事实见[执行记录](execution-ledger.md)，原始结果保存在[本轮独立输出目录](../../outputs/pearl-evidence-dev80-20261004-01/)，完整身份绑定见[交付清单](../../outputs/pearl-evidence-dev80-20261004-01/delivery-manifest-r01.json)。本轮完成于Evidence，不继续Layer 3/4。

## 入口与边界

| 文件 | 已实现职责 |
| --- | --- |
| [protocol.md](protocol.md) | C0/C1 × 4096/8192，完整序列化、固定tokenizer、三值评分与语义噪声口径 |
| [statistics-supplement.md](statistics-supplement.md) | 汇总结果计算前固定的分题型配对 bootstrap 描述性区间 |
| [assemble.py](assemble.py) | 原运行清单追溯、SHA核验、query-only组装、完整步骤正文及保存后预算核验 |
| [review.py](review.py) | 实际正文盲包导出、匿名来源关联、实际审查全文/引文/来源记录与唯一选择 |
| [score.py](score.py) | 三值 OR-of-AND、完整组覆盖、最佳组覆盖、分题型、配对统计和步骤增损 |
| [verify.py](verify.py) | 不调用评分核心的独立重算、保存产物/预算/分母/审查绑定核验 |

组装器仅以字节核验 Gold，不解析答案或评分标签。题型元数据由评估侧单独导出；原开发80题、四类各20，20题诊断按四类各5固定抽样。重复文本只有在查询、需求、来源关联与实际序列化正文完全绑定相同时复用同一次审查；不同正文分别审查。

## 已执行命令

以下从仓库根目录运行，所有新输出目标均须不存在；已有结果不可覆盖。

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python -m pytest experiments/pearl-evidence-dev80-20261004 -q
.\.venv\Scripts\python experiments/pearl-evidence-dev80-20261004/assemble.py --output outputs/pearl-evidence-dev80-20261004-01/stage20 --count 20 --query-types outputs/pearl-evidence-dev80-20261004-01/query-types.json
.\.venv\Scripts\python experiments/pearl-evidence-dev80-20261004/review.py export --contexts outputs/pearl-evidence-dev80-20261004-01/stage20/contexts.jsonl --gold outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-r02.json --output outputs/pearl-evidence-dev80-20261004-01/stage20/review
.\.venv\Scripts\python experiments/pearl-evidence-dev80-20261004/assemble.py --output outputs/pearl-evidence-dev80-20261004-01/stage80 --count 80 --query-types outputs/pearl-evidence-dev80-20261004-01/query-types.json
.\.venv\Scripts\python experiments/pearl-evidence-dev80-20261004/review.py export --contexts outputs/pearl-evidence-dev80-20261004-01/stage80/contexts.jsonl --gold outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-r02.json --output outputs/pearl-evidence-dev80-20261004-01/stage80/review
.\.venv\Scripts\python outputs/pearl-evidence-dev80-20261004-01/run_final_scoring.py
.\.venv\Scripts\python outputs/pearl-evidence-dev80-20261004-01/audit_stage.py outputs/pearl-evidence-dev80-20261004-01/stage20 r03
.\.venv\Scripts\python outputs/pearl-evidence-dev80-20261004-01/audit_stage.py outputs/pearl-evidence-dev80-20261004-01/stage80 r02
```

上述输出现已存在，命令记录用于追溯；复现时换用新的输出子目录。`gold-r02.json` 的身份从原 revision/delivery 清单的唯一SHA匹配核定，未根据文件名或最新时间选择。首次组装准备发现相对路径解析错误，在创建stage目录前失败；增加回归测试后修复，原错误与红绿过程保存在输出测试记录。

最终定向验证：**94 passed in 3.29s**；[实测记录](../../outputs/pearl-evidence-dev80-20261004-01/targeted-test-validation-r03.json)绑定测试与当前核心代码SHA。合成固定算例与[截断参考](fixtures/synthetic-truncation-reference.json)明确区分确定性构造标签和真实语义 Agent 审查；不将合成支持标签记为真实评估。此次仅新增实验代码，没有改变稳定跨模块契约，不据此宣称全仓测试或新的模型运行。

`run_final_scoring.py`仅在20个实际完整批次和精确复用记录到齐后进行机械收集、版本选择、评分和独立审计，不自动生成语义标签。各实际命令、返回码和stdout/stderr保存在stage80的`command-*-r01.json`；完整独立verify参数见各阶段`audit-command-*.json`。该辅助脚本及路径绑定属于本次本地结果，不是已集成业务模块CLI。复现真实语义评估还需独立Agent实际阅读新导出文本，不能靠评分脚本得到支持标签。

## 审查与成本的真实口径

独立语义角色使用 `fork_turns=none`，只接收查询、必要需求、允许组、匿名实际文本和冻结提示。逐份记录实际阅读、支持依据与未知；肯定支持的引文必须是相应文本的精确子串。来源标题保留解释所需语义，策略、排名、分数、旧支持、参考答案及未送入正文隐藏。

没有执行独立系统充分性预测，因此不报告 Sufficiency Accuracy。相关性与噪声为保存单元级的语义判断，mixed同时计入两者；不是token使用率，也不是token级噪声比例。token预算使用固定BGE-M3 tokenizer作本轮计量，不宣称与未执行生成器的计费口径一致。Agent具体模型ID与计费token若运行接口不暴露，明确记录不可获取，不编造API模型调用或费用。
