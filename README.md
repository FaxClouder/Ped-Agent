# Ped-Agent

Ped-Agent 是面向行人流研究的模块化科研工程。当前目标是形成可独立实验、可组合、
可复现的知识检索、视频分析和证据问答能力，而不是建设 Web 产品或长期运行服务。

## 研究模块

| 目录 | 研究职责 | 主要输出 |
| --- | --- | --- |
| `Contracts/` | 稳定的跨模块数据契约 | Evidence、Answer、Trajectory |
| `Knowledge-Base/` | 文献解析、索引、检索、Rerank 与评测 | Evidence Item、检索报告 |
| `Video-Analysis/` | 检测、跟踪、标定、轨迹与流动分析 | 轨迹、指标、图表、Analysis Bundle |
| `Agent/` | 证据编排、引用约束和科研问答 | Answer Document |

科研资产按用途分开：`memPed/` 保存本地研究数据，`experiments/` 保存可复现实验定义，
`paper/` 保存论文工程，`outputs/` 保存本地实验产物，`docs/` 保存方法和设计记录。
当前文档入口见 [`docs/README.md`](docs/README.md)；贡献与 Agent 规则见 [`AGENTS.md`](AGENTS.md)。

## 当前阶段边界

- 各模块独立开发，通过 `Contracts/` 预留接口。
- 不维护 FastAPI、Vue、SSE、任务队列和会话数据库。
- 不追求产品级高可用、权限、加密、审计和高覆盖率测试。
- 保留科研所需的文件哈希、算法版本、配置、随机种子和结果 provenance。
- 测试只服务于算法正确性、契约稳定和实验结果不被无意改变。

## 本地验证

现有环境无需启动服务，可直接运行模块级检查：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
```

视频真实推理需要本地权重；知识 Dense 检索和 Rerank 需要对应本地模型或外部适配器。

## 研究开发顺序

1. 固定输入数据和实验问题。
2. 在单个模块内运行算法并保存中间产物。
3. 记录配置、代码版本、模型版本和输入哈希。
4. 生成指标、图表和实验报告。
5. 模块接口稳定后，再开展跨模块组合实验。

研究目标设计保存在 `docs/data-analysis-module-design.md` 和
`docs/vision-module-design.md` 中；是否已实现必须以代码和测试为准。
