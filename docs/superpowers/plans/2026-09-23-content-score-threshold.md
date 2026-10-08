# 文献全文评分门槛调整实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将五批文献的内容分数通过线统一改为严格高于 65 分，并保留独立治理疑点。

**Architecture:** 人工标准、YAML 镜像和离线 `ResourceManifest` 使用同一门槛；`screening.csv` 仅重算门槛派生状态，不改变原评分。原始逐篇报告保留为历史快照，另写本次规则变更补充记录。

**Tech Stack:** Python/Pydantic、pytest、CSV、Markdown、PowerShell。

## Global Constraints

- `total_score > 65`，即 66–100 通过，65 及以下不通过；不重打分。
- DOI/PDF 身份、主题范围、完整性、期刊、引用、授权和 A/B/X 均不因分数调整自动通过。
- 不改 PDF，不生成正式技术 Manifest，不导入或发布索引。
- 既有工作树较脏；只编辑列出的文件，不纳入无关修改。仓库要求新文档有 H1、斜体上下文和状态，并在 `docs/README.md` 登记。

## 文件职责

- `Knowledge-Base/tests/test_governance_manifest.py`：65/66 边界及独立门槛回归。
- `Knowledge-Base/src/ped_knowledge/governance/contracts.py`：离线正式文献契约。
- `memPed/knowledge/collection_standard.md` 与 `memPed/knowledge/literature_quality_rules.yaml`：人工与机器可读标准。
- `memPed/knowledge/literature/records/screening.csv`：108 条原始分数和当前派生状态。
- `memPed/knowledge/reports/content-score-threshold-reclassification-2026-09-23.md`：新旧口径与逐批统计；五份原报告不修改。
- `docs/README.md`：设计与实施记录的导航链接。

---

### Task 1: 固定 65/66 离线契约边界

**Files:**
- Modify: `Knowledge-Base/tests/test_governance_manifest.py`
- Modify: `Knowledge-Base/src/ped_knowledge/governance/contracts.py:260-261`
- Modify: `memPed/knowledge/collection_standard.md:27`
- Modify: `memPed/knowledge/literature_quality_rules.yaml:35`

**Interfaces:** `ResourceManifest.model_validate(dict)`；仍返回合法模型或抛 `ValueError`。

- [ ] **Step 1: 添加失败测试。** 在 `test_governance_manifest.py` 使用现有工厂，追加：

  ```python
  def test_literature_content_score_65_is_rejected() -> None:
      with pytest.raises(ValueError, match="content_quality_score > 65"):
          ResourceManifest.model_validate(
              approved_literature_record(
                  Path("paper.pdf"), "0" * 64, content_quality_score=65
              )
          )

  def test_literature_content_score_66_is_accepted() -> None:
      record = ResourceManifest.model_validate(
          approved_literature_record(
              Path("paper.pdf"), "0" * 64, content_quality_score=66
          )
      )
      assert record.content_quality_score == 66

  def test_content_score_does_not_override_integrity_gate() -> None:
      with pytest.raises(ValueError, match="clear integrity_status"):
          ResourceManifest.model_validate(
              approved_literature_record(
                  Path("paper.pdf"), "0" * 64,
                  content_quality_score=66, integrity_status="retracted",
              )
          )
  ```
- [ ] **Step 2: 运行红灯。** `pytest` 命令如下，预期 66 分案例失败、65 分错误文案不符：

  ```powershell
  $env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
  .\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_governance_manifest.py -q
  ```

- [ ] **Step 3: 最小实现。** 将契约比较改为 `self.content_quality_score <= 65`，错误文字改为 `content_quality_score > 65`；人工标准写“全文质量评分高于 65（66–100 分）”；YAML 的 `minimum_content_quality_score` 改为 `66`，如需表达严格边界则添加注释 `# Equivalent to total_score > 65 for integer scores.`。
- [ ] **Step 4: 运行绿灯。** 重跑上述测试文件，预期 0 失败。检查 `git diff --check`，只提交本任务的精确路径，不纳入已有无关更改。

### Task 2: 按原分数重算五批筛选状态

**Files:**
- Modify: `memPed/knowledge/literature/records/screening.csv`
- Create: `memPed/knowledge/reports/content-score-threshold-reclassification-2026-09-23.md`
- Create: `Knowledge-Base/tests/test_literature_screening_threshold.py`

**Interfaces:** 输入为 `screening.csv` 中原有五项分数、`total_score`、`fulltext_screen`、`decision`；输出仍是同一 CSV 结构，无新列。

- [ ] **Step 1: 保存只读基线。** 用 `Import-Csv` 统计总数、唯一 DOI、总分分布和现有 `decision`；用 `git diff` 检查用户已有 CSV 改动，不覆盖。确认 108 条、104 条 `>65`、4 条 `<=65`，否则停止并调查。
- [ ] **Step 2: 写迁移验收检查。** 在 `Knowledge-Base/tests/test_literature_screening_threshold.py` 写下列测试并运行 `python -m pytest Knowledge-Base/tests/test_literature_screening_threshold.py -q`，预期旧状态使其失败：

  ```python
  import csv
  from pathlib import Path


  SCREENING = (
      Path(__file__).resolve().parents[2]
      / "memPed/knowledge/literature/records/screening.csv"
  )
  PARTS = (
      "relevance_score", "method_score", "rag_evidence_score",
      "coverage_score", "traceability_score",
  )


  def test_content_score_threshold_reclassification() -> None:
      with SCREENING.open(newline="", encoding="utf-8-sig") as stream:
          rows = list(csv.DictReader(stream))
      assert len(rows) == 108
      assert len({row["doi"].casefold() for row in rows}) == 108
      assert all(row["doi"] for row in rows)
      assert sum(int(row["total_score"]) > 65 for row in rows) == 104
      for row in rows:
          score = int(row["total_score"])
          assert sum(int(row[name]) for name in PARTS) == score
          assert row["fulltext_screen"] == ("pass" if score > 65 else "fail")
          assert "below_80" not in row["decision"]
          if score <= 65:
              assert row["decision"] == "candidate_only_content_at_most_65"
              assert not row["quality_tier"]
  ```
- [ ] **Step 3: 使用 `apply_patch` 仅更新派生字段。** 所有 `>65` 设 `fulltext_screen=pass`，`<=65` 设 `fail`。旧 `candidate_only_content_below_80` 中，`<=65` 改为 `candidate_only_content_at_most_65`；`>65` 一般改为 `pending_governance`，但 `10.1016/j.trc.2024.104617` 改为 `pending_scope_review`，`10.18564/jasss.5037` 改为 `pending_pdf_doi_identity_review`。旧 `pending_manual_content_review` 保留原决策以继续提示证据局限需人工复核，`fulltext_screen` 仍根据新分数设为 `pass`。逐项根据原报告核对其他独立疑点；`quality_tier` 继续为空，原分数及审阅日期不动。
- [ ] **Step 4: 新增补充报告。** 写明旧 80 分状态是历史判断、当前 `>65` 判定、每批新统计、四篇仍未通过 DOI、独立待核实清单和未执行正式入库声明；链接五份原报告与 CSV，不覆盖原报告。
- [ ] **Step 5: 运行迁移验收检查。** 预期全部通过；再用 `git diff --word-diff` 核对只有 `fulltext_screen` 与 `decision` 改动。若 CSV 在 Git 中有旧的用户修改，不对其做整体回退或覆盖。

### Task 3: 全量核验和文档导航

**Files:**
- Modify: `docs/README.md`
- Verify: `memPed/knowledge/reports/batch-{1..5}-fulltext-screening-2026-09-23.md`（只读）

**Interfaces:** 无新增运行时接口。

- [ ] **Step 1: 将实施补充报告加入 `docs/README.md`。** 保留该文件已有用户修改，新增仓库相对链接。
- [ ] **Step 2: 检查链接与状态。** 确认计划、报告、五份历史报告及 CSV 链接均存在，原报告内容未变；运行 `git diff --check`。
- [ ] **Step 3: 运行模块和全套测试。** 先运行 Task 1 的测试，再按仓库规定执行：

  ```powershell
  $env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
  .\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
  ```

- [ ] **Step 4: 逐项对照设计稿和最终差异。** 汇报准确的通过/未通过数、独立待核实项、测试结果及任何环境性失败；不声称正式入库已完成。
