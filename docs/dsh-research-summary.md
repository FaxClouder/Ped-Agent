# DeepSeek Harness (dsh) 调研总结

*历史设计快照 · status: historical · 2026-10-04 整理；不代表当前实现或当前上游版本*

本文件保留原始正文，当前替代入口：[2026-10-04 研究文档](../Agent-Harness/docs/deepseek-harness-design-study.md)。旧测试、完成状态与环境结论只适用于原记录时点。


## 🎯 核心发现

**DeepSeek Harness** 是一个成熟的 TypeScript Agent 运行时框架（2026年8月发布），但**不建议完全采用**。

### 为什么不建议完全采用？

1. **技术栈不匹配**: TypeScript 核心，Python 只是客户端
2. **过度设计**: UI、沙箱等对科研场景不必要
3. **集成复杂**: 需要维护 TypeScript + Python 双栈
4. **学习曲线**: Cordis 插件系统需要额外学习

### 推荐策略

✅ **借鉴设计，Python 实现**

- 研究 dsh 的工具注册、Profile、追踪机制
- 在 Agent-Harness 中用 Python 实现类似设计
- 保持与现有 Python 模块的无缝集成

## 📋 可借鉴的设计

### 1. 工具注册机制
```python
# 借鉴 dsh 的声明式注册
class ToolRegistry:
    def register(self, name, description, parameters, handler):
        # 类似 dsh 的 ctx.command()
        pass
```

### 2. Profile 系统
```python
# 配置组合与复用
RESEARCH_BASIC = Profile(
    name="research_basic",
    model_config={...},
    enabled_tools=[...],
    execution_policy={...},
)
```

### 3. 执行追踪
```python
# 记录、回放、分析
class ExecutionTracer:
    def record(self, tool_call, result, timing):
        # 类似 dsh-eval
        pass
```

## 🧪 行动计划

### 立即执行（本周）

1. **POC 实验**: `experiments/dsh-evaluation/`
   - 安装测试 dsh
   - 评估实际体验
   - 记录集成复杂度

2. **API 测试**: `experiments/deepseek-tool-calling/`
   - 直接测试 DeepSeek API 工具调用
   - 无需 dsh 框架
   - 评估 V3.2 vs R1-0528

### 核心模块稳定后

3. **借鉴实现**
   - ToolRegistry (Python)
   - Profile 系统 (Python)
   - ExecutionTracer (Python)

4. **集成 DeepSeek**
   - 在 ModelGateway 添加 DeepSeekAdapter
   - 通过 API 直接调用（无需 dsh）

## 📊 决策矩阵

| 方案 | 推荐度 | 理由 |
|------|--------|------|
| 完全替换为 dsh | ❌ | 技术栈不匹配，过度设计 |
| dsh 作为后端 | ⚠️ | 通信开销大，调试困难 |
| 借鉴设计，Python 实现 | ✅ | **推荐**：保持统一，借鉴经验 |
| POC 验证 | ✅ | **立即可行**：数据支持决策 |

## 🔗 参考资源

- [完整调研报告](../Agent-Harness/docs/dsh-research-and-integration.md)
- [DeepSeek Harness 官方](https://deepseek.com/harness/en/)
- [GitHub: deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
- [DeepSeek API 文档](https://api-docs.deepseek.com/guides/tool_calls/)

## ✅ 结论

> **借鉴 dsh 的优秀设计，用 Python 实现 Agent-Harness，直接通过 API 使用 DeepSeek 模型。**

保持技术栈统一，与现有模块无缝集成，避免过度复杂。

---

**调研时间**: 2026-09-15  
**状态**: ✅ 完成  
**下一步**: 创建 experiments/ 进行 POC 验证
