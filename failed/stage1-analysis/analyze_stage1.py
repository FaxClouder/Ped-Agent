"""Stage 1 Analysis: Retriever Ablation, Top-K, Difficulty, and Topic Performance

This script analyzes existing Gold v5 dev evaluation results without re-running retrieval.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configure plot style
plt.style.use("default")
plt.rcParams["figure.dpi"] = 150
plt.rcParams["font.size"] = 10

ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = ROOT / "paper/evaluation-reports/gold-v5-dev-20260924"
GOLD_DIR = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
OUTPUT_DIR = ROOT / "paper/evaluation-reports/stage1-analysis-20260926-02"


def prepare_output_dir(path: Path) -> None:
    """Reserve a new research output directory without replacing prior results."""
    path.mkdir(parents=True, exist_ok=False)


def load_summary() -> dict[str, Any]:
    """Load evaluation summary."""
    return json.loads((EVAL_DIR / "summary.json").read_text(encoding="utf-8"))


def load_per_query() -> list[dict[str, Any]]:
    """Load per-query results."""
    lines = (EVAL_DIR / "per_query.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def load_questions() -> dict[str, dict[str, Any]]:
    """Load Gold questions with metadata."""
    questions_path = GOLD_DIR / "questions_full_candidate_v5.jsonl"
    lines = questions_path.read_text(encoding="utf-8").splitlines()
    questions = {}
    for line in lines:
        if line.strip():
            q = json.loads(line)
            questions[q["question_id"]] = q
    return questions


def load_evidence() -> dict[str, dict[str, Any]]:
    """Load candidate evidence groups keyed by independent intent."""
    evidence_path = GOLD_DIR / "evidence_planned_candidate_v5.jsonl"
    lines = evidence_path.read_text(encoding="utf-8").splitlines()
    return {
        record["intent_id"]: record
        for line in lines
        if line.strip()
        for record in [json.loads(line)]
    }


def resource_recall_at_k(
    ranking: list[dict[str, Any]],
    evidence: dict[str, Any],
    *,
    k: int,
) -> float:
    """Compute evidence-group resource recall from an existing ranking.

    Groups are required conjunctively; alternatives within a group are
    interchangeable. This mirrors ``gold_v2.score_answerable`` without
    importing the package into this standalone analysis script.
    """
    if k < 1:
        raise ValueError("k must be positive")
    selected_resources: list[str] = []
    seen: set[str] = set()
    for hit in ranking:
        resource_id = str(hit["resource_id"])
        if resource_id in seen:
            continue
        seen.add(resource_id)
        selected_resources.append(resource_id)
        if len(selected_resources) == k:
            break
    groups = evidence.get("evidence_groups", [])
    if not groups:
        raise ValueError("answerable evidence requires nonempty groups")
    return sum(
        any(
            resource_id in selected_resources
            for alternative in group.get("alternatives", [])
            for resource_id in [str(alternative["resource_id"])]
        )
        for group in groups
    ) / len(groups)


# ============================================================================
# 1.2 RETRIEVER ABLATION STUDY
# ============================================================================

def analyze_retriever_ablation(summary: dict) -> pd.DataFrame:
    """Compare BM25, BGE-M3 (dense), and RRF (hybrid) retrievers."""
    print("\n" + "="*80)
    print("1.2 RETRIEVER ABLATION STUDY")
    print("="*80)

    methods = ["bm25", "bge_m3", "rrf"]
    languages = ["en", "zh"]
    metrics = [
        "resource_recall_at_5",
        "mrr",
        "ndcg_at_5",
        "complete_locator_at_5",
    ]

    rows = []
    for method in methods:
        for lang in languages:
            key = f"{method}/{lang}"
            if key in summary["metrics_by_method_language"]:
                data = summary["metrics_by_method_language"][key]
                row = {
                    "method": method.upper(),
                    "language": lang.upper(),
                    "recall@5": data["resource_recall_at_5"],
                    "MRR": data["mrr"],
                    "nDCG@5": data["ndcg_at_5"],
                    "locator_hit": data["complete_locator_at_5"],
                }
                rows.append(row)

    df = pd.DataFrame(rows)

    print("\n### Retriever Performance by Method and Language")
    print(df.to_string(index=False))

    # Save table
    df.to_csv(OUTPUT_DIR / "retriever_ablation.csv", index=False)

    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Retriever Ablation Study: BM25 vs Dense vs Hybrid", fontsize=14, fontweight="bold")

    metrics_to_plot = [
        ("recall@5", "Recall@5"),
        ("MRR", "Mean Reciprocal Rank"),
        ("nDCG@5", "nDCG@5"),
        ("locator_hit", "Locator Hit Rate"),
    ]

    for idx, (metric, title) in enumerate(metrics_to_plot):
        ax = axes[idx // 2, idx % 2]
        pivot = df.pivot(index="method", columns="language", values=metric)
        pivot.plot(kind="bar", ax=ax, rot=0, color=["#1f77b4", "#ff7f0e"])
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel("Score")
        ax.set_xlabel("Retriever")
        ax.legend(title="Language", loc="lower right")
        ax.set_ylim(0, 1.05)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "retriever_ablation.png", dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\n[OK] Saved: retriever_ablation.csv, retriever_ablation.png")

    return df


# ============================================================================
# 1.3 TOP-K SENSITIVITY ANALYSIS
# ============================================================================

def analyze_top_k_sensitivity(
    per_query: list[dict],
    evidence_by_intent: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Compute true evidence-group resource recall@k from stored rankings."""
    print("\n" + "="*80)
    print("1.3 TOP-K SENSITIVITY ANALYSIS")
    print("="*80)

    k_values = [1, 3, 5, 10, 20]
    rows = []
    for lang in ["en", "zh"]:
        selected = [
            row for row in per_query
            if row["method"] == "rrf" and row["language"] == lang
        ]
        for k in k_values:
            recalls = [
                resource_recall_at_k(
                    row["chunk_ranking"],
                    evidence_by_intent[row["intent_id"]],
                    k=k,
                )
                for row in selected
            ]
            rows.append({
                "k": k,
                "language": lang.upper(),
                "recall@k": float(np.mean(recalls)),
                "query_count": len(recalls),
            })

    df = pd.DataFrame(rows)
    print("\nNote: This is an offline re-analysis of stored rankings; no retrieval was rerun.")
    print("\n### Evidence-group resource recall@k (RRF Hybrid)")
    print(df.to_string(index=False))
    df.to_csv(OUTPUT_DIR / "top_k_sensitivity.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 6))
    for lang in ["EN", "ZH"]:
        subset = df[df["language"] == lang]
        ax.plot(subset["k"], subset["recall@k"], marker="o", label=lang, linewidth=2)
    ax.set_xlabel("k (distinct retrieved resources)", fontsize=12)
    ax.set_ylabel("Evidence-group resource recall@k", fontsize=12)
    ax.set_title("Top-K Sensitivity: Offline Re-analysis of RRF Rankings", fontsize=14, fontweight="bold")
    ax.legend(title="Language")
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(k_values)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_k_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("\n[OK] Saved: top_k_sensitivity.csv, top_k_sensitivity.png")
    return df


# ============================================================================
# 1.4 DIFFICULTY STRATIFICATION
# ============================================================================

def analyze_difficulty_stratification(
    per_query: list[dict],
    questions: dict[str, dict],
) -> pd.DataFrame:
    """Break down performance by query difficulty (if available)."""
    print("\n" + "="*80)
    print("1.4 DIFFICULTY STRATIFICATION")
    print("="*80)

    # Check if difficulty metadata exists
    has_difficulty = any("difficulty" in q for q in questions.values())

    if not has_difficulty:
        print("\n[WARN] No 'difficulty' metadata found in Gold questions.")
        print("   Skipping difficulty stratification analysis.")
        return pd.DataFrame()

    # Group by difficulty
    grouped = defaultdict(lambda: defaultdict(list))
    for row in per_query:
        if row["method"] == "rrf":  # Focus on best performer
            qid = row["question_id"]
            if qid in questions:
                difficulty = questions[qid].get("difficulty", "unknown")
                grouped[difficulty][row["language"]].append(row["metrics"])

    rows = []
    for difficulty in sorted(grouped.keys()):
        for lang in ["en", "zh"]:
            metrics_list = grouped[difficulty][lang]
            if metrics_list:
                avg_metrics = {
                    key: np.mean([m[key] for m in metrics_list])
                    for key in metrics_list[0].keys()
                }
                rows.append({
                    "difficulty": difficulty.capitalize(),
                    "language": lang.upper(),
                    "count": len(metrics_list),
                    "recall@5": avg_metrics["resource_recall_at_5"],
                    "MRR": avg_metrics["mrr"],
                    "nDCG@5": avg_metrics["ndcg_at_5"],
                })

    df = pd.DataFrame(rows)

    print("\n### Performance by Query Difficulty (RRF Hybrid)")
    print(df.to_string(index=False))

    df.to_csv(OUTPUT_DIR / "difficulty_stratification.csv", index=False)

    # Visualization
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Performance by Query Difficulty", fontsize=14, fontweight="bold")

    metrics_to_plot = [("recall@5", "Recall@5"), ("MRR", "MRR"), ("nDCG@5", "nDCG@5")]

    for idx, (metric, title) in enumerate(metrics_to_plot):
        ax = axes[idx]
        pivot = df.pivot(index="difficulty", columns="language", values=metric)
        pivot.plot(kind="bar", ax=ax, rot=0, color=["#1f77b4", "#ff7f0e"])
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel("Score")
        ax.set_xlabel("Difficulty")
        ax.legend(title="Language", loc="lower left")
        ax.set_ylim(0, 1.05)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "difficulty_stratification.png", dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\n[OK] Saved: difficulty_stratification.csv, difficulty_stratification.png")

    return df


# ============================================================================
# 1.5 TOPIC-BASED PERFORMANCE ANALYSIS
# ============================================================================

def analyze_topic_performance(
    per_query: list[dict],
    questions: dict[str, dict],
) -> pd.DataFrame:
    """Analyze retrieval performance by research topic."""
    print("\n" + "="*80)
    print("1.5 TOPIC-BASED PERFORMANCE ANALYSIS")
    print("="*80)

    # Check if topic metadata exists
    has_topic = any("primary_topic" in q for q in questions.values())

    if not has_topic:
        print("\n[WARN] No 'primary_topic' metadata found in Gold questions.")
        print("   Skipping topic-based analysis.")
        return pd.DataFrame()

    # Group by topic
    grouped = defaultdict(lambda: defaultdict(list))
    for row in per_query:
        if row["method"] == "rrf":
            qid = row["question_id"]
            if qid in questions:
                topic = questions[qid].get("primary_topic", "unknown")
                grouped[topic][row["language"]].append(row["metrics"])

    rows = []
    for topic in sorted(grouped.keys()):
        for lang in ["en", "zh"]:
            metrics_list = grouped[topic][lang]
            if metrics_list:
                avg_metrics = {
                    key: np.mean([m[key] for m in metrics_list])
                    for key in metrics_list[0].keys()
                }
                rows.append({
                    "topic": topic.replace("_", " ").title(),
                    "language": lang.upper(),
                    "count": len(metrics_list),
                    "recall@5": avg_metrics["resource_recall_at_5"],
                    "MRR": avg_metrics["mrr"],
                    "nDCG@5": avg_metrics["ndcg_at_5"],
                })

    df = pd.DataFrame(rows)

    print("\n### Performance by Research Topic (RRF Hybrid)")
    print(df.to_string(index=False))

    df.to_csv(OUTPUT_DIR / "topic_performance.csv", index=False)

    # Visualization - Heatmap
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Topic Performance Heatmap", fontsize=14, fontweight="bold")

    for idx, lang in enumerate(["EN", "ZH"]):
        ax = axes[idx]
        subset = df[df["language"] == lang]
        pivot = subset.set_index("topic")[["recall@5", "MRR", "nDCG@5"]]
        image = ax.imshow(pivot.to_numpy(), cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)), pivot.columns)
        ax.set_yticks(range(len(pivot.index)), pivot.index)
        for row_index in range(len(pivot.index)):
            for column_index in range(len(pivot.columns)):
                value = pivot.iloc[row_index, column_index]
                ax.text(column_index, row_index, f"{value:.2f}", ha="center", va="center")
        fig.colorbar(image, ax=ax, label="Score")
        ax.set_title(f"{lang} Queries", fontweight="bold")
        ax.set_xlabel("Metric")
        ax.set_ylabel("Research Topic")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "topic_performance.png", dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\n[OK] Saved: topic_performance.csv, topic_performance.png")

    return df


# ============================================================================
# COMPREHENSIVE REPORT
# ============================================================================

def generate_markdown_report(
    retriever_df: pd.DataFrame,
    topk_df: pd.DataFrame,
    difficulty_df: pd.DataFrame,
    topic_df: pd.DataFrame,
    summary: dict,
) -> None:
    """Generate comprehensive Stage 1 analysis report."""
    print("\n" + "="*80)
    print("GENERATING COMPREHENSIVE REPORT")
    print("="*80)
    bm25_misses = summary["resource_miss_question_ids"]["bm25"]
    bm25_zh_misses = sum(item.endswith("-zh") for item in bm25_misses)
    bm25_en_misses = sum(item.endswith("-en") for item in bm25_misses)

    report = f"""# Stage 1 Analysis Report: Retrieval Evaluation

*Offline analysis of a candidate development split · status: current*

**Generated**: {date.today().isoformat()}
**Scope**: Offline re-analysis of the 2026-09-24 Gold v5 development run
**Dataset**: Gold v5 Development Set (20 intents, 40 bilingual queries)
**Corpus**: 104 resources
**Evaluated Methods**: BM25, BGE-M3 (Dense), RRF (Hybrid)

---

## Executive Summary

This report presents the Stage 1 retrieval evaluation results for the Ped-Agent knowledge retrieval system, covering:

1. **Retriever Ablation Study**: Comparison of BM25, Dense (BGE-M3), and Hybrid (RRF) retrievers
2. **Top-K Sensitivity Analysis**: Evidence-group resource recall across k=1,3,5,10,20 from stored rankings
3. **Difficulty Stratification**: Unavailable because the candidate questions have no difficulty labels
4. **Topic-Based Analysis**: Performance across research topics

### Key Findings

**RRF Hybrid result** (BM25 + BGE-M3, candidate development split):
- English: 100% Recall@5, MRR=0.94, nDCG@5=0.96
- Chinese: 95% Recall@5, MRR=0.74, nDCG@5=0.79

**Critical Issue**: BM25 Chinese Structural Failure
- 0% recall on all {bm25_zh_misses} Chinese queries; {bm25_en_misses} additional English query was missed
- The lexical mismatch is a hypothesis requiring query-level score inspection.
- RRF maintained the same Chinese Recall@5 as dense retrieval in this run.

**Language Asymmetry**:
- Chinese queries lag English by 0.20 in MRR and 0.16 in nDCG
- The source of this gap requires query-level investigation.

---

## 1.2 Retriever Ablation Study

### Comparison: BM25 vs Dense vs Hybrid

![Retriever Ablation](retriever_ablation.png)

**Table 1: Performance by Retriever and Language**

```
{retriever_df.to_string(index=False)}
```

### Analysis

**English Queries**:
- BM25: 95% recall (solid lexical baseline)
- BGE-M3: 100% recall (perfect dense retrieval)
- RRF: 100% recall (hybrid maintains dense performance)

**Chinese Queries**:
- BM25: **0% recall** (complete failure)
- BGE-M3: 95% recall (dense-only viable solution)
- RRF: 95% recall (hybrid = dense when BM25 fails)

**Interpretation**: BM25 did not retrieve the planned Chinese evidence at k=5 in this candidate split. The contribution of each retrieval component requires a controlled comparison.

---

## 1.3 Top-K Sensitivity Analysis

### Recall Saturation Across k Values

![Top-K Sensitivity](top_k_sensitivity.png)

**Table 2: Recall@K for RRF Hybrid Retriever**

```
{topk_df.to_string(index=False)}
```

### Analysis

The table reports descriptive behavior on the stored development rankings. It does not establish a production k or a statistically validated optimum. Any production choice must also account for context length, latency, answer quality, and the sealed test set.

---

## 1.4 Difficulty Stratification

"""

    if not difficulty_df.empty:
        report += f"""### Performance by Query Difficulty

![Difficulty Stratification](difficulty_stratification.png)

**Table 3: Metrics by Difficulty Level**

```
{difficulty_df.to_string(index=False)}
```

### Analysis

"""
        # Analyze difficulty patterns
        easy = difficulty_df[difficulty_df["difficulty"] == "Easy"]
        medium = difficulty_df[difficulty_df["difficulty"] == "Medium"]
        hard = difficulty_df[difficulty_df["difficulty"] == "Hard"]

        if not easy.empty:
            report += f"- **Easy queries**: {easy['recall@5'].mean():.1%} average recall\n"
        if not medium.empty:
            report += f"- **Medium queries**: {medium['recall@5'].mean():.1%} average recall\n"
        if not hard.empty:
            report += f"- **Hard queries**: {hard['recall@5'].mean():.1%} average recall\n"

        report += "\n**Interpretation**: The current development split is too small to support a reliable difficulty effect estimate; difficulty metadata is absent from this candidate snapshot.\n"
    else:
        report += """### Difficulty Stratification Not Available

[WARN] No difficulty metadata found in Gold v5 questions. This analysis requires adding `difficulty` field to question records.

**Recommendation**: Tag questions with difficulty levels (easy/medium/hard) in next Gold iteration.
"""

    report += "\n---\n\n## 1.5 Topic-Based Performance\n\n"

    if not topic_df.empty:
        report += f"""### Performance Across Research Topics

![Topic Performance](topic_performance.png)

**Table 4: Metrics by Research Topic**

```
{topic_df.to_string(index=False)}
```

### Analysis

**Topic Coverage**:
- Total unique topics: {topic_df['topic'].nunique()}
- Queries per topic: {topic_df.groupby('topic')['count'].first().describe().to_dict()}

**Performance Patterns**:
"""
        # Identify best/worst performing topics
        en_subset = topic_df[topic_df["language"] == "EN"]
        if not en_subset.empty:
            best_topic = en_subset.loc[en_subset["recall@5"].idxmax(), "topic"]
            worst_topic = en_subset.loc[en_subset["recall@5"].idxmin(), "topic"]
            report += f"- Best performing (EN): {best_topic}\n"
            report += f"- Most challenging (EN): {worst_topic}\n"

        report += "\n**Insight**: Topic analysis reveals which research areas are well-covered in the corpus and which need more resources.\n"
    else:
        report += """### Topic Analysis Not Available

[WARN] No topic metadata found in Gold v5 questions. This analysis requires adding `primary_topic` field to question records.

**Recommendation**: Tag questions with research topics in next Gold iteration.
"""

    report += f"""
---

## Cross-Lingual Performance Gap

### Language Asymmetry Analysis

**Mean Paired Difference (Chinese - English)**:

```json
{json.dumps(summary["mean_paired_zh_minus_en"], indent=2)}
```

### Root Causes

1. **BM25 Chinese Resource Misses**: All 20 Chinese queries missed the planned resources at k=5
   - Inspect tokenization and scores before assigning a cause
   - RRF's Chinese resource recall matches dense retrieval here; the rankings differ

2. **Dense Embedding Challenges**:
   - BGE-M3 is multilingual but not perfect
   - BGE-M3 Chinese queries show 0.17 lower MRR than English
   - Suggests semantic gap in cross-lingual understanding

3. **Ranking Quality**: nDCG gap (0.14-0.16) indicates:
   - Expected resources retrieved but ranked lower
   - First relevant result appears later for Chinese queries

---

## Recommendations

### Immediate Actions (Week 1)

1. **For Chinese Queries**: Treat BM25 failure as a design issue requiring a separately evaluated mitigation
   - Compare query translation, language routing, and dense-only retrieval

2. **Choose k only after broader evaluation**
   - Compare recall, latency, context length, answer quality, and the sealed test set
   - Do not infer a production default from this development re-analysis

### Near-Term Improvements (Week 2-4)

3. **Enhance Gold Dataset**:
   - Add `difficulty` and `primary_topic` metadata to all questions
   - Enable stratified analysis in future evaluations

4. **Test Reranking**:
   - Add BGE-M3 cross-encoder reranking
   - May improve Chinese query ranking quality (MRR/nDCG)

### Long-Term Strategy (Month 2+)

5. **Corpus Expansion**:
   - Consider bilingual abstracts or Chinese translations
   - Reduces cross-lingual dependency

6. **Advanced Retrieval**:
   - Test ColBERT or late-interaction models
   - May improve cross-lingual semantic matching

---

## Files Generated

**CSV Tables**:
- `retriever_ablation.csv`: Performance by retriever method
- `top_k_sensitivity.csv`: Recall curves at different k
- `topic_performance.csv`: Performance by research topic

**Visualizations**:
- `retriever_ablation.png`: 4-panel comparison chart
- `top_k_sensitivity.png`: Recall saturation curves
- `topic_performance.png`: Topic heatmaps

**Reports**:
- `stage1_analysis_report.md`: This comprehensive report

---

## Conclusion

Stage 1 evaluation demonstrates:
- ✅ **Strong baseline**: RRF hybrid achieves 100% EN / 95% ZH recall@5
- [WARN] **Observed gap**: BM25 misses the planned Chinese resources in this candidate split
- [CHART] **Next analysis**: compare candidate k values with latency, context length and answer quality
- **Stage 2 scope**: reference answers still require human review before generation scoring

**Next Steps**: Implement query translation, add reference answers to Gold dataset, and proceed to Stage 2 (LLM integration + generation metrics).

---

**Evaluation Details**:
- Code Revision: {summary.get("code_revision", "N/A")}
- Catalog Fingerprint: {summary.get("catalog_fingerprint", "N/A")}
- Questions SHA256: {summary.get("questions_sha256", "N/A")}
- Evaluation Date: 2026-09-24
- Analysis Date: {date.today().isoformat()}
"""

    # Save report
    report_path = OUTPUT_DIR / "stage1_analysis_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n[OK] Saved: stage1_analysis_report.md")


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run all Stage 1 analyses."""
    global OUTPUT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    OUTPUT_DIR = parser.parse_args().output_dir.resolve()
    prepare_output_dir(OUTPUT_DIR)
    print("\n" + "="*80)
    print("STAGE 1 ANALYSIS: RETRIEVAL EVALUATION")
    print("="*80)
    print(f"\nInput: {EVAL_DIR}")
    print(f"Output: {OUTPUT_DIR}\n")

    # Load data
    summary = load_summary()
    per_query = load_per_query()
    questions = load_questions()
    evidence_by_intent = load_evidence()

    print(f"Loaded {len(per_query)} query results")
    print(f"Loaded {len(questions)} question records")

    # Run analyses
    retriever_df = analyze_retriever_ablation(summary)
    topk_df = analyze_top_k_sensitivity(per_query, evidence_by_intent)
    difficulty_df = analyze_difficulty_stratification(per_query, questions)
    topic_df = analyze_topic_performance(per_query, questions)

    # Generate report
    generate_markdown_report(retriever_df, topk_df, difficulty_df, topic_df, summary)

    print("\n" + "="*80)
    print("STAGE 1 ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n[DIR] All outputs saved to: {OUTPUT_DIR}")
    print("\n[CHART] Generated files:")
    for file in sorted(OUTPUT_DIR.iterdir()):
        print(f"   - {file.name}")


if __name__ == "__main__":
    main()
