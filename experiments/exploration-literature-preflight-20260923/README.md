# 文献技术预检探索实验

_Batch-1 五篇试点及五批 104 篇集中技术 Manifest 的只读预检 · status: current_

## 目的与边界

检验从准备表生成的五篇实验用技术 Manifest 能否通过项目现有的只读
`preflight_manifest`。这不是正式文献准入或入库批准。本实验不调用
`ImportService.import_manifest`，不解析、切块、建索引或上传 PDF。

在五篇试点之后，另生成 `manifest_all_104_preflight_only.jsonl`，覆盖准备表的全部
104 篇（含试点五篇及其余 99 篇），不改写试点文件。两个 Manifest 均仅供技术预检。

`manifest_preflight_only.jsonl` 中仅列出本实验选定的五篇。`include=false` 表示候选
检索状态，**不会阻止导入程序处理该行**；因此绝不能以该字段替代不调用导入程序。
四篇标记“暂不使用”的文献均未列入任何实验 Manifest。

## 选样

从 [`manifest_readiness_2026-09-23.csv`](../../memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv)
中选取 batch-1 各一个受控主题。五篇均已记录引用数值、PDF 哈希匹配且可读取，
并且没有内容、范围或 PDF/DOI 身份专项待复核标记。正式版本、完整性、使用权限和
A/B/X 等级仍按原记录保持待核实；这些条件不由技术预检判定。

| 主题 | DOI |
| --- | --- |
| 疏散行为建模 | `10.1007/s11069-022-05208-y` |
| 安全风险干预 | `10.1038/s41598-020-79454-0` |
| 设施场景流动 | `10.1038/s41598-024-61007-4` |
| 行人流基础 | `10.1371/journal.pone.0117856` |
| 实验测量 | `10.1371/journal.pone.0240963` |

## 可复现输入与执行

- 准备表 SHA-256：`d18693b22a1ceae10e915b684d4b051b181b65b8bacf013a42255f8964d5a318`。
- 候选记录 SHA-256：`65c2cf99b19f506a61379b04649f421a39432b18f979a0053b5f8c17a1e5643f`。
- PDF SHA-256 逐篇写在 Manifest，路径相对本目录。无随机抽样；选样规则如上。
- 预检实现基于仓库 `Knowledge-Base/src/ped_knowledge/ingestion/__init__.py` 的当前工作树。
  Git HEAD 为 `b6369e38a64912b07fb67b733427924341756586`，但工作树含未提交改动，
  因此该提交不能单独重现所有当前代码。预检无需模型或解析器后端。

在仓库根目录运行：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -c "from pathlib import Path; from ped_knowledge.ingestion import preflight_manifest; p=Path('experiments/exploration-literature-preflight-20260923/manifest_preflight_only.jsonl'); r=preflight_manifest(p); print('passed', len(r.records), 'failed', len(r.failures)); [print(x.resource_id, x.reason) for x in r.failures]"
```

预检结果保存在独立的 [`outputs/literature-preflight-batch1-5-2026-09-23/`](../../outputs/literature-preflight-batch1-5-2026-09-23/)；该目录是本地实验产物，不覆盖现有研究输出。

## 五批集中 Manifest

`manifest_all_104_preflight_only.jsonl` 逐行从同一准备表复制身份、题名、语言、
DOI、来源 URL、受控主题和已核验的 PDF SHA-256；路径相对本实验目录。
批次分布为 12、10、18、13、51 篇。它保留所有准备表对象，包括仍有治理待核实
标记的文献；技术预检通过不消除这些标记。新文件 SHA-256 为
`c2d1d59ebca49804b7438ff11fca84d728da62cb1def8fa306e540bbd348558c`。

在仓库根目录运行只读预检：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -c "from pathlib import Path; from ped_knowledge.ingestion import preflight_manifest; p=Path('experiments/exploration-literature-preflight-20260923/manifest_all_104_preflight_only.jsonl'); r=preflight_manifest(p); print('passed', len(r.records), 'failed', len(r.failures)); [print(x.resource_id, x.reason) for x in r.failures]"
```

集中结果见独立的 [`outputs/literature-preflight-all104-2026-09-23/`](../../outputs/literature-preflight-all104-2026-09-23/)。
