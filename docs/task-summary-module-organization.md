# 项目整理与Agent-Harness模块创建总结

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

_2026-09-15_

---

## 🎯 任务目标

1. 整理当前项目的模块划分和功能设计
2. 创建独立的Agent-Harness模块用于工具调用和Agent编排
3. 在核心模块开发的同时并行设计高级能力

---

## ✅ 已完成内容

### 1. 项目模块划分文档

**创建**: `docs/module-division-and-design.md` (455行)

全面整理了项目的五大模块：

#### **Contracts** - 跨模块数据契约
- Evidence、QAPair、Trajectory等核心数据结构
- 运行状态与指标定义

#### **Knowledge-Base** - 知识与证据模块
- 9个子模块完整结构：ingestion → retrieval → evaluation
- BGE-M3本地部署配置
- BM25 + Dense + RRF检索能力清单
- 技术导入数据流

#### **Video-Analysis** - 检测追踪与流动分析
- 完整研究链路：检测→跟踪→标定→分析→可视化
- 密度、速度、流量、OD、基本图分析能力
- YOLO + ByteTrack + PedPy技术栈

#### **Agent** - 证据编排与问答
- LangGraph证据图流程
- 引用规则验证与语义审查
- 多轮修订机制
- 外部搜索集成

#### **experiments** - 可复现研究实验
- 实验记录要求（假设、版本、种子、结果）
- 资产边界管理

**特点**:
- ✅ 覆盖所有模块、子模块、数据流、能力清单
- ✅ 清晰的层次、表格、流程图
- ✅ 明确各模块职责范围与边界
- ✅ 包含验证命令、开发流程、扩展规则
- ✅ 基于代码和测试的真实实现状态

### 2. Agent-Harness模块创建

**位置**: `Agent-Harness/`

**模块结构**:
```
Agent-Harness/
├── src/ped_agent_harness/
│   ├── __init__.py              # 模块入口
│   ├── protocols.py             # 核心协议定义 ✅
│   ├── tools/                   # 工具注册与执行
│   ├── agents/                  # Agent抽象
│   ├── runtime/                 # 运行时框架
│   ├── orchestration/           # 多Agent编排
│   └── evaluation/              # 评测框架
├── tests/
│   └── test_protocols.py        # 协议测试 ✅ (8 passed)
├── examples/
│   └── tool_calling_demo.py     # 示例代码
├── docs/
│   └── design-notes.md          # 设计决策文档
├── pyproject.toml               # 项目配置
├── README.md                    # 模块文档
├── SETUP_SUMMARY.md             # 创建总结
└── .gitignore
```

**核心成果**:

#### protocols.py - 核心协议定义
```python
# Phase 1: Tool Calling基础
class Tool(BaseModel)              # 工具定义
class ToolCall(BaseModel)          # 工具调用请求
class ToolResult(BaseModel)        # 工具执行结果
class ToolRegistry(Protocol)       # 工具注册器接口

# Phase 2: Agent抽象 (规划)
class AgentInput(BaseModel)
class AgentOutput(BaseModel)
class Agent(Protocol)

# Phase 3: 运行时 (规划)
class ExecutionContext(BaseModel)
```

#### 测试验证
```bash
pytest Agent-Harness/tests/ -v
# ✅ 8 passed, 2 warnings in 0.12s
```

#### 文档
- ✅ `README.md`: 完整的模块说明、架构概览、开发计划
- ✅ `docs/design-notes.md`: 详细的设计决策、待决策问题、参考实现
- ✅ `SETUP_SUMMARY.md`: 创建过程总结

### 3. 项目文档更新

#### `docs/README.md`
- ✅ 添加Agent-Harness到模块导航

#### `docs/project-architecture.md`
- ✅ 更新架构图（添加harness节点）
- ✅ 更新模块职责表（添加Agent-Harness行）

---

## 🏗️ Agent-Harness设计原则

### 1. 渐进式设计
- **Phase 1**: Tool Calling基础（当前）
- **Phase 2**: Agent抽象（待Agent模块稳定后）
- **Phase 3**: 运行时与追踪（按需）
- **Phase 4**: 多Agent编排（仅在有明确需求时）

### 2. 职责分离
- **Agent模块**: 证据收集、问答生成、引用验证（领域逻辑）
- **Harness模块**: 工具调用、Agent运行时、编排框架（通用能力）

### 3. 协议优先
```python
@runtime_checkable
class ToolRegistry(Protocol):
    def register(...) -> None: ...
    async def execute(...) -> ToolResult: ...
```
- 接口与实现解耦
- 支持多种实现
- 便于测试

### 4. 异步优先
- 所有工具执行都是async
- 支持I/O密集型操作
- 支持并发执行

---

## 🔗 模块关系

### 当前架构

```
Contracts (数据契约)
   ↑
   ├─ Knowledge-Base (知识检索)
   ├─ Video-Analysis (轨迹分析)
   ├─ Agent (证据编排)
   └─ Agent-Harness (工具调用) [设计中]
      ↑
      └─ Agent (未来集成)
```

### 集成策略

**现在**:
- Agent模块直接调用LocalEvidenceRetriever和ExternalEvidenceSearcher
- 通过Protocol接口，已经实现了解耦

**未来（Phase 1完成后）**:
```python
# Agent模块集成Harness
class EvidenceGraph:
    def __init__(
        self,
        model_gateway: ModelGateway,
        tool_registry: ToolRegistry,  # 来自Harness
    ):
        # LocalEvidenceRetriever注册为工具
        # ExternalEvidenceSearcher注册为工具
```

### 与Contracts的关系
- Harness定义的Tool、ToolCall、ToolResult是临时契约
- 接口稳定后可能下沉到Contracts模块
- 时机：Phase 1完成，Agent模块集成验证后

---

## 📋 开发计划

### 现在（与核心模块并行）

**核心模块优先**:
1. ✅ Knowledge-Base 文献检索流程
2. ✅ Video-Analysis 轨迹分析验证
3. ✅ Agent 证据图端到端测试
4. ✅ 跨模块集成验证

**Agent-Harness并行设计**:
1. ✅ 模块结构创建
2. ✅ 核心Protocol定义
3. 🚧 ToolRegistry实现设计
4. 🚧 ToolExecutor实现设计
5. 🚧 参数验证策略

### 核心模块稳定后

**实施Tool Calling**:
1. ⏸️ 实现ToolRegistry和ToolExecutor
2. ⏸️ 在experiments/验证实际效果
3. ⏸️ 集成到Agent模块
4. ⏸️ 工具参数验证增强
5. ⏸️ 错误处理完善

### 按需扩展

**高级特性**:
1. ⏸️ Agent抽象（如有必要）
2. ⏸️ 运行时追踪（用于调试）
3. ⏸️ 多Agent编排（需求驱动）

---

## 💡 关键设计决策

### ✅ 已决策

1. **Protocol优先**: 使用Python Protocol定义接口，而不是继承
2. **Pydantic验证**: 所有数据结构使用Pydantic BaseModel
3. **异步优先**: 所有执行接口都是async
4. **渐进式实现**: 先Tool Calling，多Agent按需
5. **模块独立**: Agent-Harness作为独立模块，不与Agent模块耦合

### 🤔 待决策

记录在`Agent-Harness/docs/design-notes.md`:

1. **工具注册方式**: 装饰器 vs 显式调用？
2. **参数验证库**: JSON Schema + jsonschema vs Pydantic动态模型？
3. **工具超时机制**: 默认超时？可配置？
4. **重试策略**: 是否支持工具执行重试？
5. **并发控制**: 多个工具调用如何管理并发？
6. **ToolRegistry单例**: 单例 vs 非单例？
7. **工具执行隔离**: 需要沙箱吗？（科研环境可能不需要）
8. **错误处理策略**: 工具失败后Agent如何继续？

---

## 📚 相关文档

### 新创建的文档

1. **`docs/module-division-and-design.md`** - 立即有用
   - 项目模块划分与功能设计
   - 开发时查阅模块边界
   - 理解数据流和职责划分

2. **`docs/multi-agent-and-tool-integration-plan.md`** - 备用参考
   - Tool Calling和多Agent编排的详细方案
   - 技术调研结果
   - 不急于实施，等需要时参考

3. **`Agent-Harness/README.md`** - 模块说明
   - 模块定位、架构、开发计划
   - 与其他模块的关系
   - 使用示例

4. **`Agent-Harness/docs/design-notes.md`** - 设计细节
   - 阶段划分
   - 接口设计原则
   - 待决策问题
   - 参考实现

5. **`Agent-Harness/SETUP_SUMMARY.md`** - 创建总结
   - 已完成内容
   - 设计原则
   - 开发阶段
   - 关键设计亮点

### 更新的文档

1. **`docs/README.md`**: 添加Agent-Harness到导航
2. **`docs/project-architecture.md`**: 更新架构图和模块表

---

## 🎯 为什么这样设计？

### 问题：为什么不马上实现Tool Calling？

**答案**: 先把房子建好，再装修升级

1. **当前Agent已经可用**
   - 证据图流程已实现
   - 本地检索和外部搜索已接入
   - 只是通过Protocol而不是LLM Tool Calling

2. **避免过早优化**
   - 先验证核心研究流程是否跑得通
   - 再评估Tool Calling能否带来实质提升

3. **复杂度控制**
   - Tool Calling会增加调试难度
   - 多Agent会影响可复现性
   - 科研场景需要确定性强的流程

4. **文档已准备好**
   - 设计思路已记录
   - 当需要时可以直接参考实施
   - 不会因为延后而丢失设计

### 问题：为什么要单独创建Agent-Harness模块？

**答案**: 职责分离，通用能力独立

1. **Agent模块专注领域逻辑**
   - 证据收集
   - 问答生成
   - 引用验证

2. **Harness模块提供通用能力**
   - 工具调用
   - Agent运行时
   - 编排框架

3. **未来可复用**
   - 其他Agent也可以使用Harness
   - 工具可以独立测试
   - 编排逻辑与业务逻辑解耦

---

## 🚀 下一步建议

### 立即行动（核心模块优先）

1. **Knowledge-Base**
   - 完成文献导入流程
   - 验证BGE-M3本地检索
   - 建立检索评测基准
   - Gold Questions验证

2. **Video-Analysis**
   - 验证检测追踪流程
   - 实现轨迹分析指标
   - 完善可视化输出

3. **Agent**
   - 验证LangGraph证据图流程
   - 测试引用规则和语义审查
   - 端到端问答测试

4. **跨模块集成**
   - Knowledge-Base + Agent集成测试
   - Video-Analysis数据导出验证
   - 第一批科研问题完成闭环

### 并行设计（Agent-Harness）

在核心模块开发的同时：

1. **继续完善设计文档**
   - ToolRegistry实现细节
   - ToolExecutor实现细节
   - 参数验证策略

2. **讨论待决策问题**
   - 在team中讨论设计选择
   - 参考其他框架的最佳实践
   - 记录决策和理由

3. **准备测试用例**
   - 提前思考测试场景
   - 设计mock工具
   - 规划集成测试

### 未来实施（按需）

等核心模块稳定后：

1. **评估Tool Calling需求**
   - 当前Agent流程是否足够？
   - Tool Calling能带来什么提升？
   - 复杂度增加是否值得？

2. **在experiments/验证**
   - 实现ToolRegistry和ToolExecutor
   - 创建简单工具测试
   - 对比原有流程的效果

3. **集成到Agent模块**
   - 如果验证成功，再集成
   - 保持向后兼容
   - 逐步迁移

---

## 📊 项目当前状态

### 模块成熟度

| 模块 | 结构 | 核心功能 | 测试 | 文档 | 状态 |
|------|------|----------|------|------|------|
| Contracts | ✅ | ✅ | ✅ | ✅ | 稳定 |
| Knowledge-Base | ✅ | 🚧 | 🚧 | ✅ | 开发中 |
| Video-Analysis | ✅ | 🚧 | 🚧 | ✅ | 开发中 |
| Agent | ✅ | 🚧 | 🚧 | ✅ | 开发中 |
| Agent-Harness | ✅ | ⏸️ | ✅ | ✅ | 设计阶段 |
| experiments | ✅ | ⏸️ | N/A | ✅ | 待用 |

### 文档完备性

- ✅ 项目架构文档
- ✅ 模块划分与功能设计
- ✅ 各模块README
- ✅ Tool Calling和多Agent集成方案
- ✅ Agent-Harness设计文档
- ✅ 开发流程和验证命令

---

## ✨ 总结

### 已完成

1. ✅ 完整整理了项目的模块划分和功能设计
2. ✅ 创建了独立的Agent-Harness模块
3. ✅ 定义了核心协议和接口
4. ✅ 编写了测试并验证通过
5. ✅ 完善了设计文档
6. ✅ 更新了项目架构文档

### 关键成果

- **模块划分文档**: 455行全面的模块功能清单
- **Agent-Harness模块**: 完整的模块结构和核心协议
- **测试验证**: 8个测试全部通过
- **设计文档**: 详细的设计决策和待决策问题
- **集成策略**: 清晰的与现有模块的关系

### 设计理念

**渐进式 · 协议优先 · 职责分离 · 可测试 · 可复现**

### 下一步

**专注核心模块，并行设计Harness，等时机成熟再实施Tool Calling**

---

**创建时间**: 2026-09-15\
**状态**: ✅ 完成\
**版本**: v1.0
