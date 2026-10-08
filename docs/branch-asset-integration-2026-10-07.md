# Agent 与文献设计分支资产核定

*两份分支的提交、未提交源码和历史文档收回 · status: current · 2026-10-07*

## 范围与来源

主线基准：`6d6eed42eec621ca2f63a0e825c05677a0219bbf`。
Agent 来源：`agent/agentic-rag-prep` 的 `eeb994e`、`e4d9aab`，以及 C 盘原工作树的
2 个修改文件和 4 个新增源码文件。未提交抽取已独立提交为 `f87d0b6`。
文献设计来源：`codex/content-score-threshold` 的 `f886eef`、`b6369e3`，
通过合并提交 `8e73d09` 保留原历史。

## 收回资产

| 类别 | 资产与核定 |
| --- | --- |
| Agent 开发准备 | 模块 README、开发准备文档、docs 导航 |
| 行为基线 | 固定快照及快照测试；不设置更新快照开关 |
| 组件抽取 | graph 委托调用、答案链、证据打包、prompt、结构化输出，共 6 个原未提交文件 |
| 文献设计 | 54 行原设计净变更；原正文保留，新增 historical 标识和现行验收边界说明 |
| 本地配置 | 仅备份到项目外，不纳入 Git；缓存不作为研究成果 |

## 来源文件哈希

以下 SHA-256 是原工作树文件的原始字节哈希，含原 CRLF。
Git 按 `.gitattributes` 规范化为 LF；文档状态注释另外提交。
基线 JSON 的解析内容与 Git blob 不变，不将换行规范化误报为实验快照重生成。

| 来源文件 | 原始 SHA-256 |
| --- | --- |
| `Agent/README.md` | `80ca2ec7e724eff5cfcd24edefa47ee32d10c3b05d0153ae6dc60f28f78597b3` |
| `Agent/src/ped_research_agent/evidence_graph.py` | `ef21e003b188082bae29429d67c8a321bc5ee9da0a748bf957b89f596ad39c41` |
| `Agent/src/ped_research_agent/answer_chain.py` | `0cb26fed7ad4355942d1d411e36c0dc13a74cdb72d05f71686303ad281c42d5a` |
| `Agent/src/ped_research_agent/evidence_pack.py` | `420d9998e2be4df7e2bcc029223dde9076c0df34ceae6520ec365528d7ef6b29` |
| `Agent/src/ped_research_agent/prompts.py` | `15924861f4f3b7cf90346a0919b51df2be5ebc54d06f39db9b9ed9555c44f4e5` |
| `Agent/src/ped_research_agent/structured.py` | `18ee03bc6f5369e964a96b64db3b58b3ea743f028c28288bc0da6f065ff9a030` |
| `Agent/tests/test_evidence_graph_baseline.py` | `909a8cf5e091c30c7959bc7095ed236ec0785d2d9adc1c5e9adddbad52b8a4a6` |
| `Agent/tests/snapshots/evidence_graph_baseline.json` | `09c676b799147cfa128a3632483669bf073d6ddab061a07c20d2ab7a816ef1cb` |
| `Agent/docs/agentic-rag-dev-prep.md` | `b4b5d8ea890a1e6d37a027ef2f64cd514ea4878fa103a2345affc103cc9164cb` |

文献设计原文件 SHA-256：`47ce8eeee68809533b927a73d753d3fd189a02f14ac7bc21ffa31e29a0e05fb8`。

## 验证记录

| 检查 | 实际结果 |
| --- | --- |
| E 盘原 Agent 基线 | 33 passed |
| 加入冻结快照、抽取前 | 34 passed |
| 抽取后 Agent | 34 passed；快照不更新 |
| Agent ruff | All checks passed |
| 整合工作树四模块测试 | 144 passed、1 failed；知识库测试引用快照超过 90 天 |
| 未改动 main 独立复现 | 同一知识库测试失败；本次未改 Knowledge-Base、Contracts 或 Video-Analysis |
| E 盘整合前四模块测试 | 190 passed、1 failed；同一引用快照过期问题 |
| E 盘合并后四模块测试 | 191 passed、1 failed；同一已有失败，未新增失败 |
| 独立代码审查 | 无可操作问题；独立运行 34 项 Agent 测试，并用原 EvidenceGraph 复核 5 个快照场景 |

该已有失败不是本次抽取引入的回归；本报告不声称全套测试通过。
本次未执行真实模型、检索、生成、GPU 或视频推理。

## 保全与当前边界

合并前对 E 盘 12,908 个已跟踪及未跟踪文件生成哈希清单，并保存原 docs 导航、
工作区差异及 Agent 来源文件。备份在项目外
`E:/F_Workspace/worktree-cleanup-backups/integrate-agent-content-20261007-214647/`。

E 盘原有 PEARL、Knowledge-Base、Harness 和论文工作区改动不包含在本次提交中。
`codex/memped-knowledge-staging` 保留待审，不合入历史评价器、不修改冻结评分或实验输出。
动态控制器和检索适配器仍是后续任务；GitHub 不在本次推送范围。

[Agent 入口](../Agent/README.md)；
[历史文献设计](superpowers/specs/2026-09-23-literature-manifest-readiness-design.md)。

## 主线落地与清理结果

2026-10-07 已将整合提交快进至 E 盘 main；原 docs 导航改动保留并补入本次入口。
合并前的 12,908 个原文件中，只有 Agent README、graph 和 docs 导航属于本次合法变更；
其余 12,905 个文件在落地后核对无哈希漂移。期间另有 3 份 PEARL 工作安排文档更新，
已另存最新快照并保留；本次没有写入这些文档。

`agent/agentic-rag-prep`、`codex/content-score-threshold` 已删除。
C 盘 Agent 工作树及两份临时核验工作树已移除，临时整合分支也已删除。
目前只保留 main 和 knowledge staging 的本地分支及工作树。GitHub 未推送。
