# DeepSeek Harness 研究与集成调研 - 完成总结

*历史设计快照 · status: historical · 2026-10-04 整理；不代表当前实现或当前上游版本*

本文件保留原始正文，当前替代入口：[2026-10-04 研究文档](../Agent-Harness/docs/deepseek-harness-design-study.md)。旧测试、完成状态与环境结论只适用于原记录时点。


**任务完成时间**: 2026-09-15  
**项目**: Ped-Agent Paper  
**初始需求**: "研究下 dsh，看能否嵌入和改造"

---

## ✅ 任务完成情况

### 完成的工作

#### 1. **文档调研阶段** (Phase 1) ✅

- ✅ 深入研究 DeepSeek Harness 官方文档
- ✅ 分析架构设计与技术栈
- ✅ 评估 4 种集成方案
- ✅ 提炼可借鉴的设计模式

**产出**:
- `Agent-Harness/docs/dsh-research-and-integration.md` (829行)
- `docs/dsh-research-summary.md` (104行)

#### 2. **源码分析阶段** (Phase 2) ✅

- ✅ 下载并解压 dsh 源码
- ✅ 分析项目结构（apps/packages/python/native）
- ✅ 审查 Python SDK 实现
- ✅ 验证 JSON-RPC 通信机制
- ✅ 识别核心组件（HarnessClient, Profile, Tool Registry）

**产出**:
- `docs/dsh-source-code-notes.md` (169行)
- 源码位置: `E:\F_Workspace\Paper-Sum-Ped\deepseek-harness-master\`

#### 3. **综合分析与建议** (Phase 3) ✅

- ✅ 整合文档与源码分析
- ✅ 更新集成可行性评估
- ✅ 明确技术决策路径
- ✅ 提供详细行动计划

**产出**:
- `docs/dsh-research-final-report.md` (570行)
- `docs/task-summary-dsh-research.md` (269行)

#### 4. **项目文档更新** ✅

- ✅ 更新 `Agent-Harness/README.md` 添加 dsh 参考
- ✅ 更新 `docs/README.md` 添加调研报告导航

---

## 📊 核心发现

### 关于 dsh 框架

#### 技术特点

**架构**:
- TypeScript 核心 + Cordis 微内核
- "Everything is a Plugin" 设计
- 完整的应用套件（CLI + Web UI + Desktop）

**Python SDK**:
- ✅ **真实存在且功能完整**
- 通过 JSON-RPC over stdio 与 TypeScript 运行时通信
- `deepseek-harness-sdk` + `deepseek-harness-runtime-bin` 双包结构
- 支持同步 API：`harness.run(prompt)`

**优势**:
- 成熟的插件系统
- 官方维护与社区支持
- 完整的工具链
- 活跃的生态

**劣势**:
- 开发者预览状态（官方警告破坏性变更）
- TypeScript 为主，Python 只是客户端
- 需要 Node.js ≥22.19 运行时
- 安装复杂（pnpm monorepo）
- 过度设计（UI/沙箱对科研场景非必需）

### 关于集成方案

#### 评估结果

| 方案 | 可行性 | 推荐度 | 理由 |
|------|--------|--------|------|
| A. 完全替换 Agent-Harness | 高 | ❌ | 技术栈不匹配，维护成本极高 |
| B. dsh 作为后端 | 中 | ⚠️ | 双栈复杂，黑盒调试困难 |
| C. 借鉴设计，Python 实现 | 高 | ✅✅ | 最佳平衡，推荐路径 |
| D. 实验对比 | 高 | ✅ | 验证决策，低风险 |

---

## 🎯 最终建议

### ✅ 推荐：方案 C + D 组合

#### 主路径：借鉴 dsh 设计，纯 Python 实现

**决策理由**:

1. **技术栈统一** - 保持纯 Python，与现有模块无缝集成
2. **可控性高** - 核心逻辑透明，易于调试和审计
3. **维护简单** - 无外部运行时依赖
4. **适合科研** - 可复现性、可追溯性强
5. **设计成熟** - 借鉴 dsh 已验证的模式

**从 dsh 借鉴**:
```python
# 1. Tool 注册机制
class ToolRegistry:
    def register(name, description, parameters, handler)
    def execute(tool_call) -> ToolResult

# 2. Profile 配置系统
@dataclass
class Profile:
    name: str
    model_config: ModelConfig
    enabled_tools: list[str]
    execution_policy: ExecutionPolicy

# 3. 执行追踪
class ExecutionTracer:
    def record(tool_call, result, timing)
    def replay(record_id) -> ToolResult

# 4. JSON-RPC 通信（未来扩展）
class JsonRpcClient:
    def send_request(method, params) -> JsonValue
```

#### 辅助路径：创建 POC 实验

**实验目标**:
- 验证 dsh 实际运行体验
- 测试 DeepSeek API 工具调用质量
- 对比性能（dsh vs 直接 API）
- 数据驱动最终决策

**实验设计**:
```bash
experiments/
├── dsh-evaluation/           # dsh 框架评估
│   ├── installation-log.md   # 安装过程
│   ├── tool-calling-test/    # 工具调用测试
│   └── evaluation-report.md  # 评估报告
└── deepseek-tool-calling/    # 直接 API 测试
    ├── api-test.py           # API 调用
    └── comparison.md         # 对比分析
```

### ❌ 不推荐：直接依赖 dsh 框架

**核心理由**:
1. **不稳定** - 官方警告破坏性变更
2. **过度复杂** - 科研场景不需要完整工具链
3. **双栈负担** - Python + TypeScript 维护成本
4. **黑盒风险** - 核心逻辑不可控
5. **安装障碍** - Node.js + pnpm 依赖链

---

## 📈 价值与成果

### 1. 清晰的技术决策

通过深度调研（文档 + 源码），明确了：

- ✅ **采用什么**: 借鉴 dsh 的设计模式
- ✅ **不采用什么**: dsh 作为运行时依赖
- ✅ **为什么**: 技术栈匹配度、可控性、维护成本

### 2. 完整的设计参考

提供了成熟框架的设计经验：

- Tool 注册机制（类似 Cordis `ctx.command()`）
- Profile 配置系统（模型、工具、策略组合）
- JSON-RPC 协议设计（请求/响应/通知）
- 执行追踪与回放（类似 dsh-eval）

### 3. 渐进式开发路径

明确了分阶段实施策略：

```
Phase 1: 核心模块稳定 ✅ 当前优先级
    ├── Knowledge-Base ✅
    ├── Video-Analysis ✅
    ├── Contracts ✅
    └── Agent 🔄

Phase 2: POC 实验验证 📋 核心稳定后
    ├── dsh 框架评估
    └── DeepSeek API 测试

Phase 3: Agent-Harness 实现 📋 实验后
    ├── ToolRegistry（借鉴 dsh）
    ├── Profile 系统（借鉴 dsh）
    └── ExecutionTracer（借鉴 dsh）

Phase 4: DeepSeek 集成 📋 未来
    └── 直接 API 调用（无需 dsh）
```

### 4. 风险管理

通过 POC 验证降低决策风险：

- 先实验，再决策
- 数据驱动，而非猜测
- 保持灵活调整空间

---

## 📚 文档产出总览

### 核心文档（1200+ 行）

| 文档 | 行数 | 内容 |
|------|------|------|
| `Agent-Harness/docs/dsh-research-and-integration.md` | 829 | 完整调研（架构、集成方案、设计模式） |
| `docs/dsh-research-final-report.md` | 570 | 综合报告（文档+源码分析+建议） |
| `docs/task-summary-dsh-research.md` | 269 | 任务总结（完成内容、价值、行动） |
| `docs/dsh-source-code-notes.md` | 169 | 源码分析笔记 |
| `docs/dsh-research-summary.md` | 104 | 快速参考 |
| **总计** | **1941** | **完整调研体系** |

### 更新的文档

- `Agent-Harness/README.md` - 添加 dsh 参考资源
- `docs/README.md` - 添加调研报告导航

---

## 🚀 下一步行动

### 立即执行（本周）

**继续核心模块开发** - P0 优先级

- 完成 Agent 模块证据编排功能
- 稳定 Knowledge-Base 检索能力
- 验证 Video-Analysis 分析流程

### 核心稳定后（1-2周内）

**创建 POC 实验** - P1 优先级

```bash
# 1. 创建实验目录
mkdir -p experiments/dsh-evaluation
mkdir -p experiments/deepseek-tool-calling

# 2. dsh 实际测试
cd E:/F_Workspace/Paper-Sum-Ped/deepseek-harness-master
pnpm install
pnpm run build
pnpm dsh web

# 3. DeepSeek API 测试
# 直接测试工具调用（无需 dsh）
python experiments/deepseek-tool-calling/test_api.py
```

### 实验完成后

**实施 Agent-Harness** - P1 优先级

基于实验结果，实现借鉴 dsh 的核心功能：

- ToolRegistry
- Profile 系统
- ExecutionTracer

---

## 📖 快速导航

### 立即有用

- **`docs/dsh-research-final-report.md`** - 📍 本文档（综合报告）
- **`docs/dsh-research-summary.md`** - 快速参考
- **`docs/task-summary-dsh-research.md`** - 任务总结

### 深度参考

- **`Agent-Harness/docs/dsh-research-and-integration.md`** - 完整调研（829行）
- **`docs/dsh-source-code-notes.md`** - 源码分析
- **`Agent-Harness/README.md`** - 模块入口

### 架构参考

- **`docs/module-division-and-design.md`** - 项目模块划分
- **`docs/project-architecture.md`** - 当前架构
- **`docs/multi-agent-and-tool-integration-plan.md`** - 集成策略

### 待创建（实验后）

- `experiments/dsh-evaluation/evaluation-report.md`
- `experiments/deepseek-tool-calling/comparison.md`
- `Agent-Harness/docs/tool-registry-design.md`
- `Agent/docs/deepseek-integration.md`

---

## 🎉 核心成就

✅ **全面调研** - 文档 + 源码双重验证  
✅ **清晰决策** - 知道采用什么、不采用什么、为什么  
✅ **设计参考** - 1900+ 行文档体系  
✅ **行动路径** - 分阶段实施计划  
✅ **风险可控** - POC 验证先行

**项目现在对 dsh 有了深入理解，可以自信地借鉴其设计，同时避免其复杂性！** 🚀

---

## 🔗 相关资源

### DeepSeek Harness

- [官方主页](https://deepseek.com/harness/en/)
- [GitHub 仓库](https://github.com/deepseek-ai/deepseek-harness)
- [Python SDK](https://github.com/deepseek-ai/deepseek-harness/tree/main/python/sdk)
- [文档站点](https://deepseek-harness.github.io/deepseek-harness/)

### DeepSeek API

- [工具调用文档](https://api-docs.deepseek.com/guides/tool_calls/)
- [快速开始](https://api-docs.deepseek.com/quick_start/pricing/)

### 社区资源

- [hello-dsh](https://github.com/pingfanfan/hello-dsh) - 22个技能实例
- [dsh-crew](https://github.com/ZSeven-W/dsh-crew) - Agent 编排
- [dsh-eval](https://github.com/hccccc01333/dsh-eval) - 评估平台

---

**任务状态**: ✅ **完成**  
**创建时间**: 2026-09-15  
**文档总量**: 1941 行  
**源码审查**: ✅ 完成  
**集成建议**: ✅ 明确  
**下一步**: POC 实验验证

---

**回答初始问题**:

> "研究下 dsh，看能否嵌入和改造"

**答案**: 

✅ **可以嵌入** - Python SDK 真实存在且功能完整  
⚠️ **不建议直接嵌入** - 双栈复杂度高、不稳定、过度设计  
✅ **推荐借鉴改造** - 学习其设计模式，用 Python 实现自有框架  
✅ **实验验证** - 创建 POC 对比，数据驱动决策

**最佳路径**: 借鉴 dsh 设计 + 纯 Python 实现 = 可控的高质量 Agent-Harness ✨
