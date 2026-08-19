# Ped-Agent paper workspace

*Paper sources, build artifacts, and research preparation notes · status: current*

---

The paper workspace separates manuscript material from experiment preparation. The Markdown
documents under `research/` are the current source of truth for the planned knowledge-retrieval
experiments; LaTeX and generated PDFs remain separate.

| Area | Location | Role |
| --- | --- | --- |
| Manuscript/build | `latex/`, `build/` | LaTeX sources and generated paper artifacts |
| Literature evidence | [`research/knowledge-retrieval-ablation-literature.md`](research/knowledge-retrieval-ablation-literature.md) | External methods and reported comparison designs |
| Experiment protocol | [`research/knowledge-retrieval-ablation-plan.md`](research/knowledge-retrieval-ablation-plan.md) | Ped-Agent-specific protocol, parameters, metrics, and acceptance gates |
| Research index | [`research/README.md`](research/README.md) | Navigation for preparation notes |

Experiment outputs belong under `outputs/knowledge-ablation/`, not inside the paper source tree.
The paper documents should describe the protocol and summarize results; they should not contain
large runtime databases, vector indexes, or downloaded source PDFs.
