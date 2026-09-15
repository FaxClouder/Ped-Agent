# PyTorch CUDA 版本统一设计

_统一 Windows 研究环境中的 PyTorch CUDA 依赖与验证方式 · status: plan_

## 目标

将仓库及当前 `.venv` 的 PyTorch 运行时统一为 `torch 2.14.0+cu130`，使 RTX 3080
能够用于 BGE-M3 和视频推理，同时保留可复现的版本、索引与验证命令。

## 变更范围

- 根 `pyproject.toml` 使用 PyTorch 官方 `cu130` 索引，并将 Torch 与 TorchVision 固定为兼容版本。
- 重新生成 `uv.lock`，确保 Windows wheel 来自 `https://download.pytorch.org/whl/cu130`。
- 将当前 `.venv` 中的 CPU wheel 替换为同一组 CUDA wheel。
- 将仓库内仍指向 `cu121`、`cu124` 或 CPU 回退安装的有效安装脚本和当前环境说明统一为
  `cu130`；移除项目未使用且不存在对应 2.14.0 cu130 Windows wheel 的 TorchAudio；历史设计
  记录不追溯改写。
- 不修改模型权重、研究数据、算法代码或现有实验输出。

## 依赖选择

使用以下统一组合：

```text
torch==2.14.0+cu130
torchvision==0.29.0+cu130
```

该组合与当前 BGE-M3 本地配置一致。RTX 3080 的现有 NVIDIA 591.86 驱动报告支持
CUDA 13.1，可运行 CUDA 13.0 wheel；不要求单独安装系统 CUDA Toolkit。

## 锁定策略

Torch 与 TorchVision 应成为工作区根项目的显式依赖，使根级 `[tool.uv.sources]` 能决定解析来源。
仅声明 source 而不声明根依赖不足以约束由传递依赖引入的 Torch，这正是当前锁文件仍从
PyPI 选择 CPU wheel 的原因。

## 验证

1. 检查 `torch.__version__` 和 `torch.version.cuda`。
2. 断言 `torch.cuda.is_available()` 为真，并识别 `NVIDIA GeForce RTX 3080`。
3. 在 GPU 上执行矩阵乘法并同步，确认实际 CUDA kernel 可运行。
4. 先运行与 GPU 适配相关的窄测试，再按仓库标准运行完整测试套件。

## 完成标准

- 锁文件与虚拟环境均不再包含 CPU-only Torch wheel。
- Torch 报告 CUDA 13.0，并能在 RTX 3080 上完成张量计算。
- 所有当前安装入口使用同一组 cu130 版本，且不再安装未使用的 TorchAudio。
- 项目测试未因依赖切换产生回归；如测试存在与本变更无关的既有失败，需明确记录。
