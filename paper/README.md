# Ped-Agent 论文与实验工作区

本目录用于在 `codex/paper-experiments` 分支中独立维护论文正文、实验配置、测试结果和可发表图表。它与项目运行时数据、知识库原始文件和模型产物分离，避免把尚未验证的结果写入论文结论。

## 目录结构

```text
paper/
├── latex/
│   ├── ieee/main.tex          # IEEE 入口
│   ├── elsevier/main.tex      # Elsevier 入口
│   ├── shared/                # 两套模板共享的正文
│   ├── references/            # BibTeX 文献库
│   └── figures/               # 论文定稿图
├── experiments/
│   ├── configs/               # 冻结后的实验配置
│   ├── data/                  # 原始数据说明与可复现处理结果
│   ├── results/               # 分次运行结果与汇总表
│   ├── figures/               # 从结果生成的图
│   └── templates/             # 新实验记录模板
├── scripts/
│   ├── build.ps1              # 编译 IEEE / Elsevier 文稿
│   └── new_run.ps1            # 创建标准实验记录目录
└── build/                     # 本地编译产物，不提交
```

## 编译论文

在仓库根目录执行：

```powershell
.\paper\scripts\build.ps1 -Template all
```

也可只编译一套模板：

```powershell
.\paper\scripts\build.ps1 -Template ieee
.\paper\scripts\build.ps1 -Template elsevier
```

生成的 PDF 位于 `paper/build/<template>/`。两套入口共享 `latex/shared/` 中的正文，避免 IEEE 与 Elsevier 版本内容漂移。

## 新建实验记录

```powershell
.\paper\scripts\new_run.ps1 -Name retrieval-baseline -RunType experiment
```

脚本会在 `paper/experiments/results/runs/` 下创建带时间戳的目录，包含：

- `metadata.yaml`：代码版本、数据版本、环境和复现命令；
- `metrics.csv`：结构化指标；
- `notes.md`：观察、异常和结论边界。

正式写入论文前，至少确认结果目录中同时存在冻结配置、Git 提交号、运行命令和指标文件。工程测试通过、真实模型连通、科研效果验证需要分别陈述。

## 版本控制边界

默认提交：

- LaTeX、BibTeX、实验配置和处理脚本；
- 小型 CSV / JSON / YAML 汇总结果；
- 论文使用的图表和必要的复现说明。

默认不提交：

- 原始论文全文、原始视频和受许可约束的数据集；
- 模型权重、缓存、检查点、完整日志和包含密钥的配置；
- LaTeX 中间文件与本地编译目录。
