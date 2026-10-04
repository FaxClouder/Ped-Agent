# DeepSeek Harness (dsh) 研究与集成分析

*历史设计快照 · status: historical · 2026-10-04 整理；不代表当前实现或当前上游版本*

本文件保留原始正文，当前替代入口：[2026-10-04 研究文档](deepseek-harness-design-study.md)。旧测试、完成状态与环境结论只适用于原记录时点。


_调研时间: 2026-09-15_

---

## 📋 执行摘要

**DeepSeek Harness (dsh)** 是 DeepSeek 于 2026年8月13日开源的 Agent 运行时框架，采用 MIT 许可证。核心设计理念是 **"Everything is a Plugin"**（万物皆插件），基于 Cordis 微内核系统构建。

**关键发现**：
- ✅ **成熟度**: 开发者预览版（v0.1），明确声明会有破坏性变更
- ✅ **架构**: TypeScript 编写，基于 Cordis 插件系统
- ✅ **Python支持**: 有 Python SDK，但主要通过 JSON-RPC stdio 通信
- ⚠️ **适配复杂度**: 需要理解 Cordis 插件系统和 TypeScript 生态
- ⚠️ **与现有架构的契合度**: 中等（需要评估改造成本）

**建议**: 先在 `experiments/` 进行概念验证，评估与现有 Agent-Harness 设计的集成路径。

---

## 🔍 DeepSeek Harness 概述

### 定位

> DeepSeek Harness (dsh) 是一个 Agent 运行时框架，定位为模型与机器之间的运行时层，处理工具调用、文件编辑、Shell命令执行和会话管理。

**公式**: `Agent = Model + Harness`

### 核心特性

1. **万物皆插件架构**
   - 模型适配器、工具、技能、会话、沙箱、存储、循环、调度、UI 全部作为插件实现
   - 基于 Cordis 框架的 "时空可组合性"（Spatiotemporal Composability）

2. **Profile 系统**
   - Profile 是有序的插件包堆栈
   - 支持用户覆盖配置
   - 示例: `dsh --profile sdk-minimal`

3. **多语言支持**
   - **核心**: TypeScript (框架本身)
   - **Python**: 通过 SDK + JSON-RPC stdio 通信
   - **其他**: 支持通过插件扩展

4. **开箱即用**
   ```bash
   npx @deepseek-ai/dsh web
   # 启动 Web UI: http://127.0.0.1:3080
   ```

---

## 🏗️ 架构分析

### Cordis 插件系统

DeepSeek Harness 基于 [Cordis](https://cordisjs.org/) 框架，这是一个 TypeScript 元框架，提供：

1. **服务与事件**
   - 插件贡献服务（Service）、类型化事件（Typed Events）
   - 可逆效果（Reversible Effects）

2. **动态挂载/卸载**
   - 插件可以在运行时动态挂载和卸载
   - 不破坏正在运行的应用

3. **依赖注入**
   - 提供强大的依赖注入机制

### 核心组件

根据 [架构文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md):

```
┌─────────────────────────────────────┐
│         dsh (CLI Entry)             │
└──────────────┬──────────────────────┘
               │
    ┌──────────▼──────────┐
    │   Profile Loader    │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────────────────────┐
    │      Cordis Plugin System           │
    ├─────────────────────────────────────┤
    │  - Model Adapters                   │
    │  - Tool Registry                    │
    │  - Agent Loop                       │
    │  - Session Management               │
    │  - Sandbox & Approval Policy        │
    │  - Storage & Persistence            │
    │  - UI (Web/CLI)                     │
    └─────────────────────────────────────┘
```

#### dsh-base 包
- 模型适配器 (OpenAI兼容、DeepSeek API等)
- 工具系统
- 持久化存储
- 沙箱与审批策略
- 设置与凭证管理
- 遥测

#### dsh-web-app 包
- 浏览器应用
- 启动: `dsh web`

#### dsh-headless 包
- 一次性运行器
- 无服务器模式

---

## 🐍 Python 集成方式

### Python SDK 架构

根据 [Python SDK 示例](https://github.com/deepseek-ai/deepseek-harness/blob/master/python/sdk/examples/README.md):

```python
# Python 客户端通过 JSON-RPC stdio 与 dsh 通信
dsh --profile sdk-minimal
```

**关键点**:
1. **Python 不是主运行时**: Python 作为客户端，通过 JSON-RPC 与 TypeScript 运行时通信
2. **Profile 控制**: Agent 组合、持久化、执行策略都在 Profile 中定义（TypeScript）
3. **工具注册**: 需要在 TypeScript 插件中注册工具

### 工具调用流程

```
┌──────────────┐        JSON-RPC        ┌─────────────────┐
│ Python Client│ <─────────stdio───────> │  dsh Runtime    │
│              │                         │  (TypeScript)   │
└──────────────┘                         └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  Tool Plugins   │
                                         │  (TypeScript)   │
                                         └─────────────────┘
```

### 示例资源

1. **官方示例**: `deepseek-ai/deepseek-harness/python/sdk/examples/`
2. **中文教程**: [hello-dsh](https://github.com/pingfanfan/hello-dsh) - 22个技能实例
3. **工具注册示例**: [dsh-repo-setup](https://github.com/gongyijie85/dsh-repo-setup)

---

## 🔄 与现有 Agent-Harness 的对比

### 设计哲学对比

| 维度 | Agent-Harness (我们的) | DeepSeek Harness (dsh) |
|------|------------------------|------------------------|
| **语言** | Python | TypeScript (核心) + Python SDK |
| **架构** | Protocol 优先 | Plugin 优先 (Cordis) |
| **定位** | 模块化科研工程的通用能力层 | 开箱即用的 Agent 运行时 |
| **扩展方式** | Python Protocol + 实现类 | TypeScript 插件 |
| **Agent 循环** | 自定义 (与 LangGraph 配合) | 内置 (dsh-agent-loop) |
| **工具注册** | Python ToolRegistry | TypeScript 插件 + Python 调用 |
| **会话管理** | 自定义 | 内置持久化 |
| **UI** | 无 (科研场景不需要) | Web UI / CLI |
| **沙箱** | 未实现 (科研环境不需要) | 内置沙箱 + 审批策略 |
| **成熟度** | 设计阶段 | 开发者预览 (v0.1) |

### 技术栈对比

| 维度 | Agent-Harness | dsh |
|------|---------------|-----|
| **核心语言** | Python 3.12+ | TypeScript (Node.js ≥22.19) |
| **数据验证** | Pydantic | Zod (TypeScript) |
| **插件系统** | Python Protocol | Cordis |
| **通信** | 直接调用 | JSON-RPC stdio |
| **测试** | pytest | Vitest / Jest |
| **异步** | asyncio | async/await (Node.js) |

---

## 🎯 集成可行性分析

### 方案 A: 完全替换 Agent-Harness ❌

**不推荐**

**原因**:
1. **语言栈切换**: 需要从 Python 切换到 TypeScript 主导
2. **学习曲线**: 团队需要学习 Cordis 插件系统
3. **科研场景不匹配**: dsh 的 UI、沙箱、审批策略对科研场景是过度设计
4. **与现有模块的耦合**: Knowledge-Base、Video-Analysis 都是 Python

**风险**: 高 | **收益**: 低 | **投入**: 大

---

### 方案 B: 将 dsh 作为 Tool Calling 后端 ⚠️

**可行但复杂**

**架构**:
```
Agent 模块 (Python)
    ↓
Agent-Harness (Python)
    ↓
ToolRegistry (Python) ──JSON-RPC──> dsh Runtime (TypeScript)
    ↓
Tool Plugins (TypeScript)
```

**优点**:
- ✅ 利用 dsh 成熟的工具系统
- ✅ 获得沙箱和审批策略（如果需要）

**缺点**:
- ❌ 增加通信层开销 (Python ↔ JSON-RPC ↔ TypeScript)
- ❌ 需要维护两套语言栈
- ❌ Python 工具需要包装成 TypeScript 插件
- ❌ 调试复杂度显著增加

**风险**: 中高 | **收益**: 中 | **投入**: 大

---

### 方案 C: 借鉴 dsh 设计，保持 Python 实现 ✅

**推荐**

**策略**:
1. **研究 dsh 的设计模式**
   - 工具注册机制
   - Agent 循环设计
   - 会话管理
   - 执行追踪

2. **保持我们的 Protocol 架构**
   - 继续使用 Python Protocol
   - Pydantic 数据验证
   - asyncio 异步

3. **选择性吸收**
   - ✅ Profile 系统概念（配置组合）
   - ✅ 工具分类与发现机制
   - ✅ 执行追踪设计
   - ❌ Cordis 插件系统（太重）
   - ❌ UI 和沙箱（不需要）

**优点**:
- ✅ 保持语言栈统一（Python）
- ✅ 借鉴成熟框架的设计经验
- ✅ 与现有模块无缝集成
- ✅ 调试和开发效率高

**缺点**:
- ⚠️ 需要自己实现（但我们本来就在做）

**风险**: 低 | **收益**: 高 | **投入**: 中

---

### 方案 D: 在 experiments/ 进行概念验证 ✅

**立即可行**

**步骤**:
1. 在 `experiments/dsh-poc/` 创建实验
2. 安装 dsh: `npx @deepseek-ai/dsh web`
3. 创建简单的 TypeScript 工具插件
4. 通过 Python SDK 调用
5. 评估实际体验和性能

**产出**:
- 实际的集成复杂度评估
- Python ↔ TypeScript 通信开销测量
- 工具注册流程的亲身体验
- 决策依据

**时间**: 1-2天
**风险**: 无（实验性质）
**收益**: 数据支持的决策

---

## 🔧 具体集成路径（如果选择方案 C）

### 1. 借鉴 dsh 的工具注册机制

#### dsh 的方式 (TypeScript 插件)
```typescript
// dsh plugin example
export function apply(ctx: Context) {
  ctx.command('my-tool')
    .action(async ({ session }, ...args) => {
      // Tool implementation
      return result;
    });
}
```

#### 我们的适配 (Python Protocol)
```python
# Agent-Harness/src/ped_agent_harness/tools/registry.py
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[[dict[str, Any]], Awaitable[Any]],
    ) -> None:
        """Register a tool with its handler."""
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
        )
        self._tools[name] = tool
        self._handlers[name] = handler
    
    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool and return the result."""
        if tool_call.tool_name not in self._handlers:
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                content=f"Tool {tool_call.tool_name} not found",
                is_error=True,
            )
        
        handler = self._handlers[tool_call.tool_name]
        try:
            result = await handler(tool_call.arguments)
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                content=str(result),
                is_error=False,
            )
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                content=str(e),
                is_error=True,
            )
```

### 2. 借鉴 dsh 的 Profile 系统

#### dsh 的 Profile 概念
```yaml
# dsh profile: ordered stack of plugin-bundle patch layers
profile: sdk-minimal
plugins:
  - @dshjs/plugin-common
  - @dshjs/plugin-tools-basic
  - @dshjs/plugin-adapter-deepseek
```

#### 我们的适配
```python
# Agent-Harness/src/ped_agent_harness/config.py
from dataclasses import dataclass
from typing import Any

@dataclass
class Profile:
    """Configuration profile for agent setup."""
    name: str
    model_config: dict[str, Any]
    enabled_tools: list[str]
    execution_policy: dict[str, Any]
    metadata: dict[str, Any] | None = None

# Agent-Harness/src/ped_agent_harness/profiles/
# research_basic.py
RESEARCH_BASIC = Profile(
    name="research_basic",
    model_config={
        "provider": "deepseek",
        "model": "deepseek-chat",
        "temperature": 0.0,
    },
    enabled_tools=[
        "local_evidence_retriever",
        "external_search",
    ],
    execution_policy={
        "max_tool_calls_per_turn": 5,
        "timeout_seconds": 30,
    },
)
```

### 3. 借鉴 dsh 的执行追踪

#### dsh 的追踪系统
- 每个工具调用都有完整的追踪
- 支持回放（replay）
- 支持A/B测试对比

#### 我们的适配
```python
# Agent-Harness/src/ped_agent_harness/tracing.py
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class ExecutionTrace:
    """Trace of a single tool execution."""
    trace_id: str
    tool_call: ToolCall
    tool_result: ToolResult
    started_at: datetime
    completed_at: datetime
    metadata: dict[str, Any] | None = None
    
    @property
    def duration_ms(self) -> float:
        delta = self.completed_at - self.started_at
        return delta.total_seconds() * 1000

class ExecutionTracer:
    """Record and replay tool executions."""
    
    def __init__(self):
        self._traces: list[ExecutionTrace] = []
    
    def record(
        self,
        tool_call: ToolCall,
        tool_result: ToolResult,
        started_at: datetime,
        completed_at: datetime,
    ) -> None:
        """Record an execution trace."""
        trace = ExecutionTrace(
            trace_id=f"trace_{len(self._traces)}",
            tool_call=tool_call,
            tool_result=tool_result,
            started_at=started_at,
            completed_at=completed_at,
        )
        self._traces.append(trace)
    
    def export(self) -> list[dict[str, Any]]:
        """Export traces for analysis."""
        return [
            {
                "trace_id": t.trace_id,
                "tool_name": t.tool_call.tool_name,
                "arguments": t.tool_call.arguments,
                "is_error": t.tool_result.is_error,
                "duration_ms": t.duration_ms,
                "started_at": t.started_at.isoformat(),
            }
            for t in self._traces
        ]
```

---

## 💡 从 dsh 借鉴的关键设计模式

### 1. 一切皆可配置
- dsh 通过 Profile 实现高度可配置性
- 我们可以在 Python 中实现类似的 Profile 系统

### 2. 清晰的分层
```
UI Layer (我们不需要)
    ↓
Agent Loop (核心)
    ↓
Tool Execution Layer (关键)
    ↓
Model Adapter Layer (已有 ModelGateway)
```

### 3. 执行追踪与可复现性
- 记录每次工具调用
- 支持实验回放
- 便于调试和评估

---

## 📊 决策矩阵

| 方案 | 技术风险 | 实现成本 | 维护成本 | 与现有架构契合 | 科研场景适配 | 推荐度 |
|------|---------|---------|---------|---------------|-------------|-------|
| A. 完全替换 | 高 | 极高 | 高 | 低 | 低 | ❌ 不推荐 |
| B. dsh 作为后端 | 中高 | 高 | 高 | 中 | 中 | ⚠️ 可行但不推荐 |
| C. 借鉴设计 | 低 | 中 | 低 | 高 | 高 | ✅ **强烈推荐** |
| D. 概念验证 | 无 | 低 | 无 | N/A | N/A | ✅ **立即可行** |

---

## 🎯 推荐行动方案

### 短期（1-2周）

**实验阶段** - 方案 D

1. **创建 POC 实验**
   ```bash
   mkdir -p experiments/dsh-evaluation
   cd experiments/dsh-evaluation
   ```

2. **安装和测试 dsh**
   ```bash
   # 安装 Node.js 22+ (如未安装)
   npx @deepseek-ai/dsh web
   ```

3. **评估关键特性**
   - 工具注册流程
   - Python SDK 调用体验
   - 执行性能
   - TypeScript 插件开发复杂度

4. **输出评估报告**
   - `experiments/dsh-evaluation/evaluation-report.md`
   - 包含实测数据和集成建议

### 中期（核心模块稳定后）

**设计借鉴** - 方案 C

1. **实现 ToolRegistry**
   - 借鉴 dsh 的注册机制
   - 保持 Python Protocol 接口
   - 添加工具分类与发现

2. **实现 Profile 系统**
   - 配置组合与复用
   - 环境特定设置
   - 实验预设

3. **实现 ExecutionTracer**
   - 记录工具执行
   - 支持回放与分析
   - 集成到 experiments/

4. **集成到 Agent 模块**
   - 作为可选后端
   - 与现有 LangGraph 流程兼容
   - 保持向后兼容

### 长期（按需）

**高级特性**

1. **多 Agent 编排**
   - 如果单 Agent 不够用
   - 参考 dsh-crew 和 dsh-agent-teams 的设计
   - 在 Python 中实现

2. **性能优化**
   - 工具并发执行
   - 结果缓存
   - 超时与重试

---

## 📚 参考资源

### 官方资源

1. **DeepSeek Harness 官方**
   - 主页: [deepseek.com/harness](https://deepseek.com/harness/en/)
   - GitHub: [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
   - 文档: [deepseek-harness.github.io](https://deepseek-harness.github.io/deepseek-harness/)

2. **Cordis 框架**
   - 官网: [cordisjs.org](https://cordisjs.org/)
   - GitHub: [cordiverse/cordis](https://github.com/cordiverse/cordis)

3. **DeepSeek API**
   - Tool Calling 文档: [api-docs.deepseek.com/guides/tool_calls](https://api-docs.deepseek.com/guides/tool_calls/)

### 社区资源

1. **教程与示例**
   - [hello-dsh](https://github.com/pingfanfan/hello-dsh) - 22个中文技能实例
   - [dsh-repo-setup](https://github.com/gongyijie85/dsh-repo-setup) - 工具注册示例

2. **生态项目**
   - [dsh-crew](https://github.com/ZSeven-W/dsh-crew) - 跨 Agent 编排
   - [dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams) - 多 Agent 协作
   - [dsh-eval](https://github.com/hccccc01333/dsh-eval) - 评估平台

3. **对比分析**
   - [Agent Frameworks, Runtimes, and Harnesses](https://www.langchain.com/blog/agent-frameworks-runtimes-and-harnesses-oh-my)
   - [AI Agent Harness Comparison 2026](https://winder.ai/ai-agent-harness-comparison/)

### 技术博客

1. [DeepSeek Harness: Everything is a Plugin](https://rits.shanghai.nyu.edu/ai/deepseek-harness-cordis-everything-is-a-plugin/)
2. [DeepSeek Open-Sources Harness](https://www.digitalapplied.com/blog/deepseek-harness-open-source-agent-framework-2026)
3. [When the Agent Runtime Becomes the Product](https://dev.to/pramod_sahu_d5bd2e6de82d1/deepseek-harness-what-happens-when-the-agent-runtime-becomes-the-product-1012)

---

## 🔬 DeepSeek 模型与工具调用

### DeepSeek R1 的工具调用支持

根据 [DeepSeek API 文档](https://api-docs.deepseek.com/guides/tool_calls/)和社区测试：

1. **官方支持**
   - ✅ DeepSeek V3.2: 支持 Function Calling
   - ✅ DeepSeek R1-0528: 支持深度推理 + Tool Calls
   - ⚠️ DeepSeek R1 (base): 不原生支持，需通过 Prompt Engineering

2. **实现框架**
   - [Reasonix](https://github.com/kabaka9527/reasonix): DeepSeek 原生 Agent 框架
     - Cache-First Loop
     - R1 Thought Harvesting
     - Tool-Call Repair
   - [IA-TOOL-DeepSeek-agent_tools](https://github.com/iosub/IA-TOOL-DeepSeek-agent_tools): Reasoner 模型 + CoT

3. **生产建议**
   - 通用任务: 使用 V3.2
   - 深度推理: 使用 R1-0528
   - 结构化输出: 虽然文档说不支持，但实测可用

### 与现有 ModelGateway 的集成

我们已有 `Agent/src/ped_agent/model_gateway.py`，可以：

```python
# 添加 DeepSeek 适配器
class DeepSeekAdapter:
    async def chat(
        self,
        messages: list[dict],
        tools: list[Tool] | None = None,
    ) -> AgentResponse:
        # 调用 DeepSeek API
        # 处理 tool_calls 响应
        pass
```

**优势**: 
- ✅ 无需依赖 dsh 就能使用 DeepSeek 模型
- ✅ 工具调用通过我们的 ToolRegistry
- ✅ 保持架构统一

---

## 💭 关键问题与解答

### Q1: dsh 是否值得完全采用？

**A**: ❌ 不推荐

**原因**:
1. 语言栈不匹配（TypeScript vs Python）
2. 过度设计（UI、沙箱对科研场景不必要）
3. 学习曲线陡峭（Cordis 插件系统）
4. 与现有模块解耦复杂

### Q2: 如何利用 dsh 的价值？

**A**: ✅ 借鉴设计，Python 实现

**具体做法**:
1. 研究 dsh 的工具注册、Profile、追踪机制
2. 在我们的 Agent-Harness 中用 Python 实现类似设计
3. 保持与现有架构的无缝集成

### Q3: Python SDK 是否可用？

**A**: ⚠️ 可用但受限

**限制**:
1. Python 只是客户端，核心逻辑在 TypeScript
2. 工具必须注册为 TypeScript 插件
3. 通信开销（JSON-RPC stdio）
4. 调试困难

**场景**: 如果已有 dsh 基础设施，Python SDK 可以调用；但从零开始不建议走这条路。

### Q4: 如何验证 DeepSeek 模型的工具调用能力？

**A**: ✅ 直接在 experiments/ 测试

**步骤**:
1. 在 `experiments/deepseek-tool-calling/` 创建实验
2. 使用 DeepSeek API 直接调用（无需 dsh）
3. 测试 V3.2 和 R1-0528 的工具调用
4. 评估响应质量和性能
5. 决定是否需要额外框架支持

### Q5: 现在应该做什么？

**A**: ✅ 两条并行路径

**路径 1: 核心模块优先**（主线）
- Knowledge-Base 文献检索
- Video-Analysis 轨迹分析
- Agent 证据图问答
- 跨模块集成

**路径 2: dsh 探索**（实验）
- `experiments/dsh-evaluation/` POC
- `experiments/deepseek-tool-calling/` API 测试
- 输出评估报告
- 为 Phase 2 提供决策依据

---

## ✅ 结论与建议

### 核心结论

1. **dsh 是一个成熟的 Agent 运行时**
   - 设计优秀，架构清晰
   - 但基于 TypeScript + Cordis

2. **与我们项目的契合度：中等**
   - ✅ 设计理念可以借鉴
   - ❌ 技术栈不匹配
   - ❌ 科研场景有过度设计

3. **DeepSeek 模型可直接使用**
   - 无需 dsh 框架
   - 通过 API 即可调用工具
   - 集成到现有 ModelGateway

### 行动建议

#### 立即执行（本周）

1. **创建 dsh 评估实验**
   ```bash
   mkdir -p experiments/dsh-evaluation
   # 安装测试 dsh
   # 记录评估结果
   ```

2. **创建 DeepSeek API 测试**
   ```bash
   mkdir -p experiments/deepseek-tool-calling
   # 测试 V3.2 和 R1 的工具调用
   # 无需 dsh，直接 API 调用
   ```

#### 短期执行（核心模块稳定后）

3. **借鉴 dsh 设计**
   - 实现 Python ToolRegistry（参考 dsh）
   - 实现 Profile 系统（参考 dsh）
   - 实现 ExecutionTracer（参考 dsh）

4. **集成 DeepSeek 模型**
   - 在 ModelGateway 添加 DeepSeekAdapter
   - 支持工具调用
   - 集成到 Agent 模块

#### 长期执行（按需）

5. **高级特性**
   - 多 Agent 编排（如有需求）
   - 性能优化
   - 更多工具类型

### 最终建议

**✅ 推荐路径**：

> **借鉴 dsh 的优秀设计，用 Python 实现我们的 Agent-Harness，直接通过 API 使用 DeepSeek 模型。**

**理由**：
1. 保持技术栈统一（Python）
2. 与现有模块无缝集成
3. 借鉴成熟框架经验
4. 避免过度复杂
5. 符合科研场景需求

---

## 📝 后续文档

基于本次调研，建议创建：

1. **`experiments/dsh-evaluation/README.md`**
   - dsh 实际测试记录
   - 性能数据
   - 集成复杂度评估

2. **`experiments/deepseek-tool-calling/README.md`**
   - DeepSeek API 工具调用测试
   - V3.2 vs R1-0528 对比
   - 响应质量评估

3. **`Agent-Harness/docs/tool-registry-design.md`**
   - 借鉴 dsh 的 ToolRegistry 设计
   - Python 实现方案
   - 与 Agent 模块的集成

4. **`Agent/docs/deepseek-integration.md`**
   - DeepSeek 模型集成指南
   - ModelGateway 扩展
   - 工具调用配置

---

**调研完成时间**: 2026-09-15  
**状态**: ✅ 完成  
**下一步**: 创建 experiments/ 进行 POC 验证  
**决策**: 借鉴设计，Python 实现，无需完全采用 dsh

---

## 🔗 Sources

- [DeepSeek Harness Official](https://deepseek.com/harness/en/)
- [deepseek-ai/deepseek-harness GitHub](https://github.com/deepseek-ai/deepseek-harness)
- [DeepSeek API Documentation](https://api-docs.deepseek.com/guides/tool_calls/)
- [Agent Frameworks Comparison](https://www.langchain.com/blog/agent-frameworks-runtimes-and-harnesses-oh-my)
- [AI Agent Harness Comparison 2026](https://winder.ai/ai-agent-harness-comparison/)
- [hello-dsh Tutorial](https://github.com/pingfanfan/hello-dsh)
- [dsh-crew GitHub](https://github.com/ZSeven-W/dsh-crew)
- [Reasonix Framework](https://github.com/kabaka9527/reasonix)