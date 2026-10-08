# PedRAGent paper workspace

*Paper sources, build artifacts, and research preparation notes · status: current*

---

The paper workspace separates manuscript material from experiment preparation. `pearl-framework/`
is the current source of truth for the evaluation protocol; LaTeX and generated PDFs remain separate.

| Area | Location | Role |
| --- | --- | --- |
| RAG research survey | [RAG_Report/README.md](RAG_Report/README.md) | RAG 方法、前沿、流程与评价调研；103 篇去重题录及本地核心公开阅读资料（current，非复现实验） |
| Manuscript/build | `latex/`, `build/` | LaTeX sources and generated paper artifacts (**路径不存在** — 未进 Git) |
| **PEARL evaluation framework** | [`pearl-framework/README.md`](pearl-framework/README.md) | Evaluation protocol for the PedRAGent system；四层顺序链条 + 控制器 + 横切维度（target design） |
| ~~**Evaluation reports**~~ | ~~`evaluation-reports/`~~ | **已作废** — 目录从未纳入 Git；Gold v* 分数迁至 [`../failed/outputs-void-scores/`](../failed/outputs-void-scores/)；Stage 1 脚本迁至 [`../failed/stage1-analysis/`](../failed/stage1-analysis/) |
| Stage report | [`Stage-Report/`](Stage-Report/) | 阶段性整理与汇报材料 |
| PEARL 6B 外部裁判工作包 | [`pearl-6b-judge-workpackage/README.md`](pearl-6b-judge-workpackage/README.md) | E5 答案评审交给 ChatGPT 代理的盲化包、操作说明与格式校验；校准 cgpt-r01 未通过（behavior 字段定义歧义），r02 澄清后全部重做并通过；研究主审第 1 期已完成，引用部分因上下文间口径分化将重做（[重做准备 r03](pearl-6b-judge-workpackage/citation-redo-r03.md)，校准复核包已导出待评审）；第 2 期（行为、事实性）已导出待评审（[期次计划](pearl-6b-judge-workpackage/research-periods.md)、[工作安排](pearl-6b-judge-workpackage/6b-work-plan.md)）；失误与偏差见 [记录](pearl-6b-judge-workpackage/incidents-and-deviations.md)（current，包与回答不进 Git） |
| ~~Cross-domain related work~~ | ~~`llm-pedestrian-literature/README.md`~~ | **路径不存在** — 不能当作当前可查阅的 Related Work 文献集 |
| ~~System design summary~~ | ~~`memped-rag-design-summary.md`~~ | **路径不存在** — 未进 Git |
| ~~Metric methods and sources~~ | ~~`F-Report/metrics-formulas-and-sources.md`~~ | **路径不存在** — `F-Report/` 未进 Git |

Experiment outputs belong under `outputs/` during active development. Once an evaluation is finalized for paper submission, archive the essential artifacts (`summary.json`, `per_query.jsonl`, analysis scripts) in a separately versioned location and record its actual path here; `evaluation-reports/` does not currently exist. The paper documents should describe the protocol and summarize results; they should not contain large runtime databases, vector indexes, or downloaded source PDFs.

**口径差异警告**：Pre-PEARL 评分采用 Gold v2 语义（组间 AND、组内替代 OR）与 @5 截断，与 PEARL 的主报口径（组内 AND、组间 OR、@10）不同。这些分数已迁至 `../failed/outputs-void-scores/`。旧检索记录仅供历史探索分析；旧题集、标签、索引、排名和结果均不进入新的 PEARL 实验，也不能经映射或离线重算转成 PEARL 成绩。

---

## 📊 评测报告

### ~~Stage 1 离线重分析 (2026-09-26)~~ **已作废**

**原因**：
- 输入路径 `evaluation-reports/gold-v5-dev-20260924/` 从未进入版本控制，本地已缺失
- 脚本已迁至 [`../failed/stage1-analysis/`](../failed/stage1-analysis/)
- PEARL 协议已退出该评测口径（Gold v2 语义 + @5）

详见 [`../failed/README.md`](../failed/README.md)

---

### ~~Gold v5 开发集评测报告 (2026-09-24)~~ **已作废**

**原因**：
- 41 个评分目录已迁至 [`../failed/outputs-void-scores/`](../failed/outputs-void-scores/)
- [旧评分器](../Knowledge-Base/src/ped_knowledge/evaluation/gold_v2.py)采用组间 AND、组内替代 OR，与 [PEARL 指标协议](pearl-framework/layer-1-retrieval/metrics.md)的证据组语义不同
- PEARL 已重新规定研究问题、标注结构与命中定义；新语料、Gold 和评分器尚未构建

详见 [`../failed/README.md`](../failed/README.md)

---

## 📄 系统设计文档 (2026-09-17)

### ~~memPed 与 RAG 系统设计总结~~ **路径不存在**

**原因**：`memped-rag-design-summary.md` 从未纳入版本控制，本地已缺失

**替代资源**：
- 系统架构：查阅 [`../docs/project-architecture.md`](../docs/project-architecture.md)
- Knowledge-Base 模块：查阅 [`../Knowledge-Base/README.md`](../Knowledge-Base/README.md)
- PEARL 评价框架：查阅 [`pearl-framework/PEARL-framework.md`](pearl-framework/PEARL-framework.md)

---

## 🎯 快速导航

### 对于论文撰写
1. 阅读 [`../docs/project-architecture.md`](../docs/project-architecture.md) 了解系统架构
2. 查阅 [`pearl-framework/PEARL-framework.md`](pearl-framework/PEARL-framework.md) 的评价链条与报告口径
3. 参考 [`pearl-framework/PEARL-framework.md`](pearl-framework/PEARL-framework.md) §4 的实验设计总览

### 对于实验执行
1. 按照 [`pearl-framework/layer-1-retrieval/experiments.md`](pearl-framework/layer-1-retrieval/experiments.md) 执行 Layer 1
2. 新语料、Gold 和方法配置冻结并按协议实际运行后，再声明 PEARL 对照结果
3. 将结果保存到 `outputs/` 下独立命名目录

### 对于系统开发
1. 参考 [`../Knowledge-Base/README.md`](../Knowledge-Base/README.md) 的 Knowledge-Base 模块说明
2. 查看 `../Knowledge-Base/src/ped_knowledge/` 的实现代码
3. 运行 `../Knowledge-Base/tests/` 的单元测试
