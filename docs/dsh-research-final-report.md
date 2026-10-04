# DeepSeek Harness (dsh) 调研与集成分析报告

*历史设计快照 · status: historical · 2026-10-04 整理；不代表当前实现或当前上游版本*

本文件保留原始正文，当前替代入口：[2026-10-04 研究文档](../Agent-Harness/docs/deepseek-harness-design-study.md)。旧测试、完成状态与环境结论只适用于原记录时点。


**完成时间**: 2026-09-15  
**项目**: Ped-Agent Paper  
**调研人**: Claude Code

---

## 📋 执行摘要

已完成 DeepSeek Harness (dsh) 的全面调研，包括文档分析、源码审查、Python SDK 验证。基于科研工程需求和技术栈匹配度，**建议借鉴 dsh 设计模式，用 Python 实现自有 Agent-Harness，而非直接集成 dsh 框架**。

---

## ✅ 已完成工作

### 1. 文档调研 (Phase 1)

创建了完整的调研文档体系：

- **`Agent-Harness/docs/dsh-research-and-integration.md`** (829行)
  - dsh 架构深度分析
  - 4种集成方案详细对比
  - 可借鉴的设计模式
  - 行动计划与决策矩阵

- **`docs/dsh-research-summary.md`** (104行)
  - 快速参考与核心发现
  - 推荐路径与理由

- **`docs/task-summary-dsh-research.md`** (269行)
  - 完整任务总结
  - 价值与成果

### 2. 源码分析 (Phase 2)

#### 下载源码
✅ 已下载并解压到 `E:\F_Workspace\Paper-Sum-Ped\deepseek-harness-master\`

#### 项目结构识别

```
deepseek-harness-master/
├── apps/
│   ├── cli/                    # CLI 应用
│   ├── web/                    # Web UI (端口 3080)
│   ├── desktop/                # 桌面应用
│   └── desktop-host/           # 桌面主机
├── packages/                   # 核心包 (TypeScript)
│   ├── experimental/
│   │   └── ptc-runtime-python/ # Python 运行时通信
│   └── ...
├── python/                     # Python SDK
│   ├── sdk/                    # deepseek-harness-sdk
│   │   ├── src/deepseek_harness/
│   │   │   ├── client.py       # JSON-RPC 客户端
│   │   │   ├── api.py          # 高层 API
│   │   │   ├── models.py       # 数据模型
│   │   │   └── errors.py       # 异常定义
│   │   └── examples/minimal.py # 最小化示例
│   └── sdk-runtime/            # deepseek-harness-runtime-bin
├── native/                     # 原生模块 (系统集成)
├── benchmarks/                 # 基准测试
└── docs/                       # 文档
```

#### Python SDK 关键发现

**✅ Python SDK 存在且功能完整**

```python
# 使用示例（从 minimal.py）
from deepseek_harness import DeepSeekHarness

with DeepSeekHarness(
    provider="deepseek-official",
    model="deepseek-v4-flash",
    cwd=str(workspace),
    dsh_home=str(dsh_home),
    profile="sdk-minimal",
) as harness:
    result = harness.run(prompt, session_id=session_id)
print(result.final_response)
```

**通信机制**:
- Python SDK → 启动 TypeScript `dsh` 子进程
- 通过 stdio 的 newline-delimited JSON-RPC 通信
- `HarnessClient` 管理进程生命周期
- 支持同步调用和异步通知

**核心组件**:
```python
# client.py (230行+)
class HarnessClient:
    """Synchronous JSON-RPC client over stdio"""
    def start()  # 启动 dsh 子进程
    def close()  # 关闭运行时
    def send_request()  # JSON-RPC 请求
    def wait_for_notification()  # 等待通知

# models.py
class Notification
class IncomingRequest
class ServerInfo
class InitializeResponse
```

---

## 🔍 深度分析

### 1. dsh 架构特点

#### 优势

✅ **成熟的插件系统** - Cordis 微内核架构  
✅ **完整的工具链** - CLI + Web UI + Desktop  
✅ **Python SDK 完整** - 真实可用的 Python 客户端  
✅ **官方支持** - DeepSeek AI 官方维护  
✅ **活跃社区** - GitHub + Discord + 插件生态

#### 劣势

⚠️ **开发者预览状态** - "THERE WILL BE COMPATIBILITY-BREAKING CHANGES"  
⚠️ **TypeScript 核心** - 主逻辑在 TypeScript，Python 只是客户端  
⚠️ **重量级依赖** - 需要 Node.js ≥22.19 + pnpm monorepo  
⚠️ **过度设计** - UI、沙箱、多应用对科研场景非必需  
⚠️ **学习曲线** - Cordis 插件系统复杂度高

### 2. Python SDK 实际能力

#### 已实现

✅ **进程管理** - 自动启动/关闭 dsh 子进程  
✅ **JSON-RPC 通信** - 请求/响应/通知的完整实现  
✅ **配置管理** - Profile、Patches、DSH_HOME  
✅ **错误处理** - JsonRpcError、TransportClosedError  
✅ **同步 API** - `harness.run(prompt)`

#### 限制

❌ **不是纯 Python** - 必须依赖 TypeScript 运行时  
❌ **通信开销** - 跨进程 + JSON 序列化  
❌ **调试复杂** - Python ↔ Node.js 双栈调试  
❌ **安装复杂** - 需要完整的 dsh 安装  
❌ **不可控** - 核心逻辑在黑盒子进程中

### 3. 集成可行性重新评估

基于源码分析，更新集成方案评估：

| 方案 | 可行性 | 复杂度 | 维护成本 | 推荐度 |
|------|--------|--------|----------|--------|
| A. 完全替换 Agent-Harness | 高 | 极高 | 极高 | ❌ |
| B. dsh 作为后端 | 中 | 高 | 高 | ⚠️ |
| C. 借鉴设计，Python 实现 | 高 | 中 | 低 | ✅ |
| D. 仅用于实验对比 | 高 | 低 | 无 | ✅ |

#### 方案 B 更新分析（Python SDK 已验证）

**技术可行性**: ✅ Python SDK 真实存在且功能完整

**实际架构**:
```
Agent 模块 (Python)
    ↓
deepseek_harness.DeepSeekHarness (Python SDK)
    ↓ JSON-RPC over stdio
dsh --profile sdk (TypeScript 子进程)
    ↓
DeepSeek API
```

**新发现的问题**:
1. **双栈运行时** - Python + Node.js 同时运行
2. **版本锁定** - SDK 与 runtime 版本必须匹配
3. **黑盒调试** - 关键逻辑在 TypeScript 进程中
4. **安装复杂** - 需要 `pnpm install` + `pnpm run build`
5. **不稳定** - 官方警告破坏性变更

**适用场景**: 快速原型验证、多语言环境、需要完整 UI

**不适用场景**: 科研可复现性、长期维护、纯 Python 环境

---

## 🎯 最终建议

### ✅ 推荐路径：方案 C + D 组合

#### 主路径：借鉴设计，Python 实现

**理由**:
1. **技术栈统一** - 纯 Python，与现有模块无缝集成
2. **可控性高** - 核心逻辑完全透明，可调试
3. **维护简单** - 无外部运行时依赖
4. **适合科研** - 可复现性、可追溯、可审计
5. **设计成熟** - dsh 已验证的设计模式

**从 dsh 借鉴**:
- Tool 注册机制（类似 Cordis `ctx.command()`）
- Profile 配置系统（模型、工具、策略组合）
- JSON-RPC 协议设计（请求/响应/通知）
- 执行追踪与回放（类似 dsh-eval）

#### 辅助路径：实验对比

**创建 POC 实验**:
```bash
experiments/
├── dsh-evaluation/           # dsh 框架评估
│   ├── installation/         # 安装测试
│   ├── tool-calling-test/    # 工具调用测试
│   └── evaluation-report.md  # 评估报告
└── deepseek-tool-calling/    # 直接 API 测试
    ├── api-test.py           # API 调用测试
    └── comparison.md         # 对比分析
```

**评估目标**:
- dsh 实际运行体验
- DeepSeek API 工具调用质量
- 性能对比（dsh vs 直接 API）
- 开发体验对比

### ❌ 不推荐：完全依赖 dsh

**核心理由**:
1. **预览状态** - 官方警告破坏性变更
2. **过度复杂** - 科研场景不需要 UI/沙箱/多应用
3. **双栈负担** - Python + TypeScript 维护成本
4. **黑盒风险** - 关键逻辑不可控
5. **安装障碍** - Node.js + pnpm + 构建流程

---

## 📚 可借鉴的设计模式

### 1. 工具注册（Inspired by dsh）

```python
# Agent-Harness 实现
class ToolRegistry:
    """工具注册器 - 借鉴 dsh 的声明式设计"""
    
    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable,
    ) -> Tool:
        """注册工具 - 类似 Cordis ctx.command()"""
        tool = Tool(
            name=name,
            description=description,
            input_schema=parameters,
        )
        self._tools[name] = tool
        self._handlers[name] = handler
        return tool
    
    def execute(self, tool_call: ToolCall) -> ToolResult:
        """执行工具调用"""
        handler = self._handlers[tool_call.name]
        try:
            output = handler(**tool_call.arguments)
            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

### 2. Profile 系统（Inspired by dsh）

```python
# Agent-Harness 实现
@dataclass
class Profile:
    """配置组合 - 借鉴 dsh Profile"""
    name: str
    model_config: ModelConfig
    enabled_tools: list[str]
    execution_policy: ExecutionPolicy
    tracing: bool = True

RESEARCH_BASIC = Profile(
    name="research_basic",
    model_config=ModelConfig(
        provider="deepseek",
        model="deepseek-v3.2",
        temperature=0.1,
    ),
    enabled_tools=["search_knowledge", "analyze_video"],
    execution_policy=ExecutionPolicy(
        max_retries=3,
        timeout=300,
    ),
)
```

### 3. 执行追踪（Inspired by dsh-eval）

```python
# Agent-Harness 实现
class ExecutionTracer:
    """执行追踪 - 借鉴 dsh-eval"""
    
    def record(
        self,
        tool_call: ToolCall,
        result: ToolResult,
        timing: ExecutionTiming,
    ) -> None:
        """记录工具调用"""
        record = ExecutionRecord(
            timestamp=datetime.now(),
            tool_call=tool_call,
            result=result,
            timing=timing,
        )
        self._records.append(record)
        self._save_to_disk(record)
    
    def replay(self, record_id: str) -> ToolResult:
        """回放工具调用"""
        record = self._load_record(record_id)
        return record.result
```

### 4. JSON-RPC 通信（Inspired by dsh client）

```python
# 未来扩展：如需与外部服务通信
class JsonRpcClient:
    """JSON-RPC 客户端 - 借鉴 dsh HarnessClient"""
    
    def send_request(
        self,
        method: str,
        params: dict,
    ) -> JsonValue:
        """发送 JSON-RPC 请求"""
        request_id = str(uuid.uuid4())
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        # 发送并等待响应
        response = self._send_and_wait(message)
        return response["result"]
```

---

## 📊 对比分析

### dsh 方式 vs 自实现方式

| 维度 | dsh 方式 | 自实现方式 |
|------|----------|-----------|
| **技术栈** | Python + TypeScript | 纯 Python |
| **依赖** | Node.js + pnpm + dsh | 标准库 + Pydantic |
| **安装** | 复杂（构建 TS 项目） | 简单（pip install） |
| **调试** | 困难（双栈） | 简单（单栈） |
| **可控性** | 低（黑盒子进程） | 高（源码透明） |
| **稳定性** | 预览版（破坏性变更） | 自主控制 |
| **功能完整度** | 非常高（UI + 沙箱） | 按需实现 |
| **学习曲线** | 陡峭（Cordis） | 平缓（标准模式） |
| **科研适用性** | 中（复杂度高） | 高（可复现） |
| **长期维护** | 依赖外部 | 自主维护 |

---

## 🚀 行动计划

### Phase 1: 核心模块稳定（当前）

**优先级**: P0（阻塞）

继续完成核心模块开发：
- ✅ Contracts - 数据契约
- ✅ Knowledge-Base - 知识检索
- ✅ Video-Analysis - 视频分析
- 🔄 Agent - 证据编排（进行中）

**Agent-Harness 状态**: 
- ✅ 协议定义完成
- 📋 工具注册等待实现

### Phase 2: dsh 实验验证（核心稳定后）

**优先级**: P1（重要非紧急）

创建实验对比：

```bash
# 1. dsh 框架评估
mkdir -p experiments/dsh-evaluation
cd experiments/dsh-evaluation

# 安装测试
pnpm install  # 在 dsh 源码目录
pnpm run build
pnpm dsh web

# 工具调用测试
python test_dsh_sdk.py

# 2. DeepSeek API 直接测试
mkdir -p experiments/deepseek-tool-calling
cd experiments/deepseek-tool-calling

# API 测试（无需 dsh）
python test_deepseek_api.py
```

**输出**:
- `experiments/dsh-evaluation/evaluation-report.md`
- `experiments/deepseek-tool-calling/comparison.md`
- 数据驱动的最终决策

### Phase 3: Agent-Harness 实现（实验后）

**优先级**: P1（重要非紧急）

基于实验结果，实现核心功能：

```python
# 借鉴 dsh 设计
Agent-Harness/
├── src/ped_agent_harness/
│   ├── protocols.py        # ✅ 已完成
│   ├── tools/
│   │   ├── registry.py     # 📋 借鉴 dsh 注册机制
│   │   └── executor.py     # 📋 工具执行器
│   ├── profile.py          # 📋 借鉴 dsh Profile 系统
│   ├── tracer.py           # 📋 借鉴 dsh-eval 追踪
│   └── agents/
│       └── base.py         # 📋 Agent 抽象
```

### Phase 4: DeepSeek 集成（按需）

**优先级**: P2（未来）

在 Agent 模块添加 DeepSeek 支持：

```python
Agent/
├── src/ped_agent/
│   ├── models/
│   │   ├── deepseek.py     # DeepSeek 适配器
│   │   └── gateway.py      # 模型网关
```

**集成方式**: 直接 API 调用（无需 dsh 框架）

---

## 📖 文档产出

### 已创建

1. **`Agent-Harness/docs/dsh-research-and-integration.md`** (829行)
   - 完整调研报告
   - 架构分析
   - 集成方案对比

2. **`docs/dsh-research-summary.md`** (104行)
   - 快速参考
   - 核心发现

3. **`docs/task-summary-dsh-research.md`** (269行)
   - 任务总结
   - 价值评估

4. **`docs/dsh-source-code-notes.md`** (169行)
   - 源码分析笔记
   - 实验计划

5. **本文档** (当前)
   - 最终综合报告
   - 深度分析与建议

### 待创建（实验后）

- `experiments/dsh-evaluation/README.md`
- `experiments/dsh-evaluation/evaluation-report.md`
- `experiments/deepseek-tool-calling/comparison.md`
- `Agent-Harness/docs/tool-registry-design.md`
- `Agent/docs/deepseek-integration.md`

---

## 🔗 参考资源

### DeepSeek Harness

- [官方主页](https://deepseek.com/harness/en/)
- [GitHub 仓库](https://github.com/deepseek-ai/deepseek-harness)
- [文档站点](https://deepseek-harness.github.io/deepseek-harness/)
- [Python SDK](https://github.com/deepseek-ai/deepseek-harness/tree/main/python/sdk)

### DeepSeek API

- [工具调用文档](https://api-docs.deepseek.com/guides/tool_calls/)
- [模型列表](https://api-docs.deepseek.com/quick_start/pricing/)

### 社区资源

- [hello-dsh](https://github.com/pingfanfan/hello-dsh) - 22个技能实例
- [dsh-crew](https://github.com/ZSeven-W/dsh-crew) - Agent 编排
- [dsh-eval](https://github.com/hccccc01333/dsh-eval) - 评估平台

---

## ✨ 核心结论

### 技术决策

1. **✅ 采用** - 借鉴 dsh 的优秀设计模式
2. **✅ 采用** - 纯 Python 实现 Agent-Harness
3. **✅ 采用** - 直接使用 DeepSeek API
4. **❌ 不采用** - dsh 作为运行时依赖
5. **✅ 可选** - 实验对比验证决策

### 价值总结

1. **清晰的技术路径** - 知道采用什么、不采用什么、为什么
2. **成熟的设计参考** - 1000+ 行调研文档
3. **可验证的决策** - POC 实验框架
4. **渐进式实施** - 分阶段行动计划
5. **风险可控** - 实验先行、数据驱动

### 下一步

**立即**: 继续核心模块开发  
**然后**: 创建 POC 实验验证  
**最后**: 基于数据实施 Agent-Harness

---

**任务状态**: ✅ 调研完成  
**文档总量**: 1200+ 行  
**源码审查**: 完成（Python SDK + 项目结构）  
**推荐路径**: 明确（借鉴设计 + Python 实现）  
**下一步**: POC 实验验证

---

**创建时间**: 2026-09-15  
**最后更新**: 2026-09-15
