"""Generate a data-driven Stage 1 diagnostic dashboard.

The dashboard reads the re-analysis CSVs and the original evaluation summary;
it does not encode target thresholds or duplicate metric values in source code.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "paper/evaluation-reports/stage1-analysis-20260926-02"
SUMMARY_PATH = ROOT / "paper/evaluation-reports/gold-v5-dev-20260924/summary.json"

plt.rcParams["figure.dpi"] = 150
plt.rcParams["font.size"] = 9
plt.rcParams["font.family"] = "sans-serif"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    retriever = pd.read_csv(REPORT_DIR / "retriever_ablation.csv")
    top_k = pd.read_csv(REPORT_DIR / "top_k_sensitivity.csv")
    topic = pd.read_csv(REPORT_DIR / "topic_performance.csv")
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    return retriever, top_k, topic, summary


def make_dashboard() -> None:
    output = REPORT_DIR / "stage1_dashboard.png"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite research output: {output}")
    retriever, top_k, topic, summary = load_data()
    fig = plt.figure(figsize=(14, 10))
    grid = fig.add_gridspec(3, 2, hspace=0.34, wspace=0.3)

    # Scope and status: descriptive, not an acceptance-target comparison.
    ax = fig.add_subplot(grid[0, 0])
    ax.axis("off")
    experiments = [
        ("1.1 Baseline run", "Existing run", "#2ecc71"),
        ("1.2 Retriever comparison", "Re-analysis", "#2ecc71"),
        ("1.3 Top-K recall curve", "Re-analysis", "#2ecc71"),
        ("1.4 Difficulty split", "Unavailable", "#95a5a6"),
        ("1.5 Topic comparison", "Re-analysis", "#2ecc71"),
    ]
    y = 0.88
    for name, status, color in experiments:
        ax.add_patch(Rectangle((0.04, y - 0.045), 0.22, 0.07, facecolor=color, edgecolor="black"))
        ax.text(0.15, y - 0.01, status, ha="center", va="center", fontsize=8, color="white", weight="bold")
        ax.text(0.31, y - 0.01, name, ha="left", va="center", fontsize=9)
        y -= 0.17
    ax.text(0.5, 1.05, "Stage 1 Analysis Status", ha="center", va="top", fontsize=11, weight="bold")
    ax.text(0.5, -0.04, "Existing retrieval run + offline re-analysis; no new retrieval", ha="center", va="top", fontsize=8, style="italic")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)

    # Existing @5 metrics, read from CSV.
    ax = fig.add_subplot(grid[0, 1])
    pivot = retriever.pivot(index="method", columns="language", values="recall@5")
    pivot.plot(kind="bar", ax=ax, rot=0, color=["#3498db", "#e74c3c"])
    ax.set_title("Existing Run: Recall@5", weight="bold")
    ax.set_ylabel("Score")
    ax.set_xlabel("Retriever")
    ax.set_ylim(0, 1.05)
    ax.legend(title="Language")
    ax.grid(axis="y", alpha=0.3)

    # Language gap, derived from CSV.
    ax = fig.add_subplot(grid[1, 0])
    recall_pivot = retriever.pivot(index="method", columns="language", values="recall@5")
    x = np.arange(len(recall_pivot.index))
    width = 0.25
    ax.bar(x - width, recall_pivot["EN"], width, label="English", color="#3498db")
    ax.bar(x, recall_pivot["ZH"], width, label="Chinese", color="#e74c3c")
    ax.bar(x + width, recall_pivot["EN"] - recall_pivot["ZH"], width, label="EN-ZH gap", color="#f39c12")
    ax.set_title("Language Asymmetry in Existing Run", weight="bold")
    ax.set_ylabel("Recall@5")
    ax.set_xticks(x)
    ax.set_xticklabels(recall_pivot.index)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    # True offline Top-K curve.
    ax = fig.add_subplot(grid[1, 1])
    for language, color, marker in [("EN", "#3498db", "o"), ("ZH", "#e74c3c", "s")]:
        subset = top_k[top_k["language"] == language]
        ax.plot(subset["k"], subset["recall@k"], marker=marker, linewidth=2, label=language, color=color)
    ax.set_title("Evidence-Group Resource Recall@k", weight="bold")
    ax.set_xlabel("k (distinct resources)")
    ax.set_ylabel("Recall@k")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(sorted(top_k["k"].unique()))
    ax.legend(title="Language")
    ax.grid(alpha=0.3)

    # Topic recall from CSV.
    ax = fig.add_subplot(grid[2, 0])
    topic_pivot = topic.pivot(index="topic", columns="language", values="recall@5")
    x = np.arange(len(topic_pivot.index))
    ax.bar(x - width / 2, topic_pivot["EN"], width, label="English", color="#3498db")
    ax.bar(x + width / 2, topic_pivot["ZH"], width, label="Chinese", color="#e74c3c")
    ax.set_title("Topic Recall@5", weight="bold")
    ax.set_ylabel("Recall@5")
    ax.set_xticks(x)
    ax.set_xticklabels([str(item).replace(" ", "\n") for item in topic_pivot.index], fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    # Dynamic findings from source data.
    ax = fig.add_subplot(grid[2, 1])
    ax.axis("off")
    bm25_zh_misses = sum(item.endswith("-zh") for item in summary["resource_miss_question_ids"]["bm25"])
    bm25_en_misses = sum(item.endswith("-en") for item in summary["resource_miss_question_ids"]["bm25"])
    rrf = retriever[(retriever["method"] == "RRF")]
    rrf_en = float(rrf.loc[rrf["language"] == "EN", "recall@5"].iloc[0])
    rrf_zh = float(rrf.loc[rrf["language"] == "ZH", "recall@5"].iloc[0])
    findings = [
        ("BM25 miss", f"{bm25_zh_misses} Chinese + {bm25_en_misses} English", "#e74c3c"),
        ("RRF recall", f"EN {rrf_en:.0%} / ZH {rrf_zh:.0%}", "#2ecc71"),
        ("Top-K scope", "k=1,3,5,10,20 from stored rankings", "#3498db"),
        ("Status", "Candidate labels; not formal Gold", "#f39c12"),
    ]
    y = 0.87
    for title, text, color in findings:
        ax.add_patch(Rectangle((0.02, y - 0.045), 0.28, 0.07, facecolor=color, edgecolor="black"))
        ax.text(0.16, y - 0.01, title, ha="center", va="center", fontsize=8, color="white", weight="bold")
        ax.text(0.34, y - 0.01, text, ha="left", va="center", fontsize=8)
        y -= 0.2
    ax.set_title("Data-Driven Findings", weight="bold", pad=12)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)

    fig.suptitle("Stage 1 Retrieval Evaluation: Diagnostic Dashboard", fontsize=14, weight="bold", y=0.98)
    fig.text(0.5, 0.01, "Gold v5 proposed development split | 20 intents / 40 variants | 104 resources | offline analysis of 2026-09-24 run", ha="center", fontsize=8, style="italic", color="gray")
    fig.savefig(output, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Dashboard saved: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    REPORT_DIR = parser.parse_args().report_dir.resolve()
    make_dashboard()
