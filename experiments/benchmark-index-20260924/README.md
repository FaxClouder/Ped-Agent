# 104 篇知识语料索引构建

_独立构建 parent-child-v1 的 FTS5 与 BGE-M3 检索索引 · status: current_

本实验使用 [`core_manifest.jsonl`](../../memPed/knowledge/literature/records/core_manifest.jsonl) 中
`include=true` 的 104 篇,以及 Catalog 中对应的活动版本。入口在运行前核对资源 ID、
原文 SHA-256、`official` 状态、子块覆盖和 tokenizer 指纹；输出目录必须尚不存在。

在仓库根目录运行：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -u experiments/benchmark-index-20260924/run.py --output-dir outputs/knowledge-index-104-v1-20260924-01
```

输出包含 `fts.sqlite3`、`chroma/` 和 `build_report.json`。报告记录语料、模型、词法
分析器和代码版本的指纹及两个索引的条目数。若构建中断，保留该目录用于诊断；重新
运行应使用新的目录名，不覆盖已有研究输出。此实验不激活检索配置，也不产生 Gold
评测分数。当前 Gold v2 仍需冻结题集和实现证据组指标。

**⚠️ V1 索引目录已迁移：** `outputs/knowledge-index-104-v1-20260924-01/` 迁至 `../../failed/outputs-void-scores/`（PEARL 退出该评测口径；见 `../../failed/README.md`）。索引构建脚本仍然有效，可用于未来 PEARL 实验。

## 独立候选索引

`build_candidates.py` 提供两个互不覆盖的候选入口。`lexical-v1` 在冻结的 V1 child chunks 上使用固定领域词表与停用词，只建立独立 FTS；Dense 对照仍引用原 V1 BGE-M3 索引。`v2` 从 104 份已保存的 canonical document 只读重切块，在新目录建立 FTS、BGE-M3 Chroma，并保存 child chunks 与输入文档哈希；它不写 Catalog、不激活默认策略。入口在创建目录前核对 104 个活动版本、原始 V1 指纹、策略、tokenizer 和模型权重，失败后保留任何已生成目录以供诊断。

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -u experiments/benchmark-index-20260924/build_candidates.py --mode lexical-v1 --output-dir outputs/knowledge-index-104-v1-lexical-candidate-新编号
.\.venv\Scripts\python -u experiments/benchmark-index-20260924/build_candidates.py --mode v2 --output-dir outputs/knowledge-index-104-v2-candidate-新编号
```

**⚠️ 候选索引目录已迁移：** 词法候选 `outputs/knowledge-index-104-v1-lexical-candidate-20260926-01/` 和 V2 候选 `outputs/knowledge-index-104-v2-candidate-20260926-02/` 迁至 `../../failed/outputs-void-scores/`。V2 从保存的 canonical 文档生成 7,884 个 child chunks，FTS/Chroma 条目数相同，并记录 FTS 文件与 Chroma 向量内容哈希。首次 V2 目录 `-01` 保留为早期版本，不用于最终对照。~~索引构建成功本身不证明检索收益；开发集对照保存在 `outputs/gold-v5-dev-p1-synthesis-20260926-03/`，不作为已发布基线。~~
