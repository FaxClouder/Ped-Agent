# Experiments

*Reproducible cross-module research studies · status: current*

这里保存可复现的科研实验定义，不承载四个模块的核心实现。

> **评测实验先读 [EVALUATION-STANDARD.md](EVALUATION-STANDARD.md)**：问题集身份与存放、封存评估集访问规则、实验设置与报告规范、扩充计划。所有问题集与评测实验在 [EVALUATION-REGISTRY.yaml](EVALUATION-REGISTRY.yaml) 登记，先登记后运行。下文的通用模板若与之冲突，以规范为准。

每个实验建议使用独立子目录，并至少记录：

- 研究问题与假设；
- 输入数据引用或哈希；
- 模块版本、模型版本和参数配置；
- 随机种子与运行命令；
- 指标定义、结果摘要和论文图表去向。

大体积输入、模型和运行结果分别放在 `memPed/`、模块本地模型目录和 Git 忽略的
`outputs/` 中。跨模块组合代码先留在具体实验目录，只有接口稳定后才下沉到模块公共 API。

## 实验类型

[切片研究当前入口](pearl-chunking-dev80-20261005/README.md)、[E3 报告](pearl-chunking-dev80-20261005/session4-e3-2026-10-06.md)及 [E2 报告](pearl-chunking-dev80-20261005/session5-e2-2026-10-06.md)记录 E0、E1 候选冻结、E3 恢复/预算比较（共同恢复 P0）与 E2 重叠消融：C2-L384 重叠冻结为 O0，C3-L256 保持 pending_review；评分 r11 为 r10 的严格扩展。开发选择不等于显著优胜。[E4 报告](pearl-chunking-dev80-20261005/session5b-e4-2026-10-06.md)记录前缀消融（M0/M1 pending_review，M0 为现有身份）与最终三套配置（C2-L384-O0-M0、C3-L256-O0-M0、B0，P0、4K）及 E5 调用计划冻结。6A 已完成 720 次真实生成（[6A 交接](../outputs/pearl-chunking-dev80-20261006-14/handoff.md)）；6B 的 API 裁判校准未通过（[6B a2 交接](../outputs/pearl-chunking-dev80-20261006-15/handoff.md)），改由外部代理评审，进度与下一步以 [6B 工作安排](../paper/pearl-6b-judge-workpackage/6b-work-plan.md)为准（2026-10-07 同步）。原 [E4 交接](../outputs/pearl-chunking-dev80-20261006-13/handoff.md)、Session 1审计、协议及 E1/E2/E3 报告保留阶段身份。全部 RAG 实验目录与产物的分类见 [RAG 资产与一致性审计](../docs/rag-asset-audit-2026-10-07.md)。

[200题固定评价分析](pearl-retrieval-eval200-20261003/evaluation-analysis-2026-10-03.md)交付阶段D三遍固定检索、200题共同支持映射、800单元／3,200前缀评分、48总体指标独立复算、预设配对／来源统计、失败与实际成本。CEGR@10为116/118/126/139（N=200），状态仍为agent_reviewed_preliminary、human_verified=false。阶段C的[完整发布入口](pearl-retrieval-eval200-20261003/README.md)、[发布报告](pearl-retrieval-eval200-20261003/stage-C-public-report.md)与[固定预注册](pearl-retrieval-eval200-20261003/preregistration.md)保留C结束时零次正式运行的冻结快照。原封存文件与只读身份保留，检索执行者只访问query-only；完整交付清单见D分析所链输出目录。

当前 PEARL 检索资产构建见 [106 篇 Adobe-only 独立索引实验](pearl-index-106-adobe-20260929/README.md)；不复用旧索引、题集或排名。

全量问题身份见 [80／200 题集冻结记录](pearl-dataset-80-200-20261003/README.md)：原8题保留，80道开发与200道独立评价分开；冻结记录时200题尚未运行，后续D原始身份保持一致。[80题R1–R4开发实验](pearl-retrieval-dev80-20261003/README.md)及[开发分析](pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md)保留原开发入口与初步结果，不将开发80和评价200合并。

开发闭环之后的 [难例复核与方法配置冻结](pearl-dev-review-freeze-20261003/README.md)已登记现行 R1–R4 配置。[开发 Gold r02 修订实验](pearl-retrieval-gold-revision-r02/README.md)已完成阶段 A 的三处修订、独立实际 child 复核和四方法共同重算，原输入和首遍排名保留；[修订分析](pearl-retrieval-gold-revision-r02/development-gold-r02-analysis-2026-10-03.md)单独报告 47/49/51/58 的 CEGR@10。[阶段 B 独立评估入口](pearl-retrieval-eval-entry-20261003/README.md)使用合成 80/200 验证 query-only、动态矩阵／评分、审查身份及启动前 release 门禁；[适配分析](pearl-retrieval-eval-entry-20261003/adaptation-analysis-2026-10-03.md)记录阶段B实际验收与原资产保留，当时真实200题未运行。当前阶段C/D进展见本节最新入口。

### 探索性实验

用于验证新想法、新技术的可行性，失败成本低，不要求产物化：
- 多Agent协作模式探索
- Tool Calling能力验证
- 新检索策略测试

### 基准实验
用于建立性能基线、评测指标，需要可复现：
- 检索系统评测（Gold Questions）
- 轨迹分析精度基准
- 证据图端到端评测

### 组合实验
用于验证跨模块集成，需要明确版本和配置：
- 知识检索 + Agent问答
- 视频分析 + 证据关联
- 多模态数据融合

## 推荐实验命名

```
experiments/
├── <category>-<topic>-<date>/
│   ├── README.md              # 实验说明
│   ├── config.yaml           # 配置
│   ├── run.py                # 执行脚本
│   ├── requirements.txt      # 依赖（如特殊）
│   └── results/              # 本地结果（不提交Git）
│       ├── run_001.jsonl
│       └── metrics.csv
```

示例：
- `exploration-tool-calling-20260915/` - 探索性Tool Calling验证
- `benchmark-retrieval-pilot-20260910/` - 检索系统Pilot基准
- `integration-video-qa-20260920/` - 视频问答集成实验

## 实验生命周期

1. **创建**: 明确研究问题，记录假设
2. **执行**: 运行并保存结果到`results/`
3. **分析**: 提取指标，记录发现
4. **归档**: 如成功验证，考虑下沉到模块；如失败，记录原因后保留目录
5. **清理**: 大体积中间文件移至`outputs/`或删除，保留配置和摘要

## 数据管理

- **输入数据**: 引用`memPed/`路径或记录外部URL
- **中间结果**: 保存到实验目录的`results/`，添加到`.gitignore`
- **最终输出**: 重要结果移至`outputs/`并单独命名
- **模型权重**: 不要复制，引用模块本地路径

## 相关文档

- [项目架构](../docs/project-architecture.md)
- [模块划分与功能设计](../docs/module-division-and-design.md)
- [多Agent与Tool集成方案](../docs/multi-agent-and-tool-integration-plan.md)
