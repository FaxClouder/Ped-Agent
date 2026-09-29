# PedRAGent paper workspace

*Paper sources, build artifacts, and research preparation notes · status: current*

---

The paper workspace separates manuscript material from experiment preparation. `pearl-framework/`
is the current source of truth for the evaluation protocol; LaTeX and generated PDFs remain separate.

| Area | Location | Role |
| --- | --- | --- |
| Manuscript/build | `latex/`, `build/` | LaTeX sources and generated paper artifacts (**路径不存在** — 未进 Git) |
| **PEARL evaluation framework** | [`pearl-framework/README.md`](pearl-framework/README.md) | Evaluation protocol for the PedRAGent system；四层顺序链条 + 控制器 + 横切维度（target design） |
| ~~**Evaluation reports**~~ | ~~[`evaluation-reports/`](evaluation-reports/)~~ | **已作废** — 目录从未纳入 Git；Gold v* 分数迁至 [`../failed/outputs-void-scores/`](../failed/outputs-void-scores/)；Stage 1 脚本迁至 [`../failed/stage1-analysis/`](../failed/stage1-analysis/) |
| Stage report | [`Stage-Report/`](Stage-Report/) | 阶段性整理与汇报材料 |
| Cross-domain related work | [`llm-pedestrian-literature/README.md`](llm-pedestrian-literature/README.md) | 行人流 × LLM/RAG 交叉文献 collection，用于 Related Work 定位；含 PedAgent 撞名记录；按设计不进入 memPed 语料 |
| ~~System design summary~~ | ~~[`memped-rag-design-summary.md`](memped-rag-design-summary.md)~~ | **路径不存在** — 未进 Git |
| ~~Metric methods and sources~~ | ~~[`F-Report/metrics-formulas-and-sources.md`](F-Report/metrics-formulas-and-sources.md)~~ | **路径不存在** — `F-Report/` 未进 Git |

Experiment outputs belong under `outputs/` during active development. Once an evaluation is finalized for paper submission, copy the essential artifacts (`summary.json`, `per_query.jsonl`, analysis scripts) into `evaluation-reports/` for long-term archival and reproducibility. The paper documents should describe the protocol and summarize results; they should not contain large runtime databases, vector indexes, or downloaded source PDFs.

**口径差异警告**：Pre-PEARL 评分采用 Gold v2 语义（组间 AND、组内替代 OR）与 @5 截断，与 PEARL 的主报口径（组内 AND、组间 OR、@10）不同。这些分数已迁至 `../failed/outputs-void-scores/`；原始检索记录可重新评分，但已生成的汇总分数不能用于 PEARL 表格。

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
- 评分器语义与 PEARL 相反（见 memory `gold-v2-scorer-and-or-inverted.md`）
- PEARL 将重新定义研究问题、语料、证据标注、命中定义

详见 [`../failed/README.md`](../failed/README.md)

---

## 📄 系统设计文档 (2026-09-17)

### ~~[memPed 与 RAG 系统设计总结](./memped-rag-design-summary.md)~~ **路径不存在**

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
2. 口径固定后再声明为 PEARL 对照结果
3. 将结果保存到 `outputs/` 下独立命名目录

### 对于系统开发
1. 参考 [`../Knowledge-Base/README.md`](../Knowledge-Base/README.md) 的 Knowledge-Base 模块说明
2. 查看 `../Knowledge-Base/src/ped_knowledge/` 的实现代码
3. 运行 `../Knowledge-Base/tests/` 的单元测试
