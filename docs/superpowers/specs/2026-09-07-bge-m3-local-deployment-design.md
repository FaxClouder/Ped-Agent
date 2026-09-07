# BGE-M3 本地部署配置设计

_面向 Knowledge-Base 的精简本地模型部署规格 · status: plan_

## 目标

在不引入常驻服务和额外审批机制的前提下，为 `Knowledge-Base` 配置一套独立、可定位的
BGE-M3 本地运行区域。该阶段只完成目录、依赖、模型权重和运行参数配置，并执行一次最小
CUDA 向量生成验证；不构建正式文献索引。

## 目录

```text
Knowledge-Base/config/embeddings/bge-m3/
├── model.yaml
└── README.md

memPed/knowledge/models/bge-m3/
└── 本地模型权重，不提交 Git

memPed/knowledge/indexes/bge-m3-1024/
└── 后续生成的 Chroma 索引，不在本阶段构建
```

配置文件与使用说明属于代码库；模型权重和向量索引属于本地研究数据。

## 模型配置

`model.yaml` 使用以下固定参数：

```yaml
model_id: BAAI/bge-m3
model_path: memPed/knowledge/models/bge-m3
index_path: memPed/knowledge/indexes/bge-m3-1024
device: cuda
use_fp16: true
dimensions: 1024
batch_size: 8
max_length: 1024
normalize_embeddings: true
```

路径以仓库根目录为基准。BGE-M3 的稠密向量维度固定为 1024；RTX 3080 默认使用 CUDA
和 FP16，批量大小从 8 开始。

## 执行范围

1. 创建配置、模型和索引目录。
2. 在现有 `.venv` 中安装 BGE-M3 所需的 PyTorch、Transformers 和 FlagEmbedding 依赖。
3. 将 `BAAI/bge-m3` 权重下载到指定本地模型目录。
4. 运行一次最小验证：加载 CUDA，编码一组中英文文本，确认输出形状为 `N × 1024`。
5. 在 `README.md` 中记录配置项和复现命令。

## 非目标

- 不增加服务进程、HTTP API 或 MCP 服务。
- 不实现质量审批、自动恢复、权限控制或额外安全测试。
- 不构建正式 Chroma 索引，不修改现有正式知识库数据。
- 不为 BGE-M3 增加完整测试套件；仅执行一次真实模型冒烟验证。

## 完成标准

- 模型权重存在于 `memPed/knowledge/models/bge-m3/`。
- BGE-M3 能在 RTX 3080 上以 CUDA/FP16 加载。
- 中英文样本文本均能生成 1024 维稠密向量。
- 配置与复现命令保存在独立配置目录中。
