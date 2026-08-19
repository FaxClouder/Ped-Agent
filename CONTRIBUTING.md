# Contributing

Ped-Agent 当前是科研工程。贡献应围绕一个明确的研究问题、算法模块或可复现实验展开，
不要同时引入产品后端、前端页面和运行平台。

## 开发原则

1. 每次改动只影响一个模块或一个稳定契约。
2. 保存实验输入、配置、模型版本、随机种子和结果说明。
3. 对数值算法提供一个固定样例或参考输出。
4. 不以测试覆盖率、服务高可用或 UI 完成度衡量科研进度。
5. 不提交 API Key、原始受限数据、本地模型权重和运行数据库。

## 本地环境

```powershell
py -3.12 -m venv .venv
uv sync
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
```

按需运行模块验证：

```powershell
.\.venv\Scripts\python -m pytest Knowledge-Base/tests -q
.\.venv\Scripts\python -m pytest Video-Analysis/tests -q
.\.venv\Scripts\python -m pytest Agent/tests Contracts/tests -q
```

## 数据规则

- `memPed/` 保存研究数据、记录、索引和实验报告。
- `paper/` 保存论文源文件和构建结果。
- 大文件、PDF、数据库、向量索引和模型缓存保持本地，不提交 Git。
- SHA-256 用于实验输入身份和复现，不代表产品级安全体系。
