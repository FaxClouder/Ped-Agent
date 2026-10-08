# DeepSeek Harness 本地源码分析笔记

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

**分析时间**: 2026-09-15\
**源码位置**: `E:\F_Workspace\Paper-Sum-Ped\deepseek-harness-master`

---

## 📁 项目结构

### 顶层目录
```
deepseek-harness-master/
├── apps/                    # 应用层
│   ├── cli/                # CLI 应用
│   ├── desktop/            # 桌面应用
│   ├── desktop-host/       # 桌面主机
│   └── web/                # Web UI
├── packages/               # 核心包
├── native/                 # 原生模块
├── benchmarks/             # 基准测试
├── docs/                   # 文档
├── .agents/                # Agent 配置
├── .claude/                # Claude 集成
└── python/                 # Python SDK (需确认)
```

### 技术栈识别

- **主语言**: TypeScript (通过 package.json 识别)
- **包管理**: pnpm (monorepo 结构)
- **构建工具**: 需要 `pnpm install` + `pnpm run build`
- **运行方式**: `npx @deepseek-ai/dsh web` 或 `pnpm dsh web`

---

## 🔍 关键发现

### 1. 官方确认开发者预览状态

> **"DeepSeek Harness is in developer preview and iterating rapidly. THERE WILL BE COMPATIBILITY-BREAKING CHANGES."**

**影响**:
- ✅ 证实了我们调研报告中的判断
- ⚠️ 不适合作为稳定基础设施
- ✅ 适合学习和借鉴设计

### 2. Monorepo 结构

项目使用 pnpm workspaces，包含：
- `apps/cli` - CLI 工具
- `apps/web` - Web UI（启动在 `http://127.0.0.1:3080`）
- `apps/desktop` - 桌面应用
- `packages/` - 核心包（需进一步探索）

### 3. 完整的工程设施

- `.oxlintrc.json` - 代码检查
- `.gitlab-ci.yml` - CI/CD
- `lefthook.yml` - Git hooks
- `AGENTS.md` / `CLAUDE.md` - Agent 集成文档

---

## 🧪 下一步探索计划

### 立即执行（实验性）

在 `experiments/dsh-evaluation/` 创建 POC 实验：

#### 1. 源码结构分析
```bash
# 查看核心包结构
ls -la deepseek-harness-master/packages/

# 查找工具注册实现
grep -r "tool" deepseek-harness-master/packages/ --include="*.ts" | head -20

# 查找 Cordis 插件示例
find deepseek-harness-master -name "*plugin*" -type f
```

#### 2. Python SDK 验证
```bash
# 查找 Python SDK
find deepseek-harness-master -name "*.py" -type f

# 如果存在 python/ 目录
ls -la deepseek-harness-master/python/
cat deepseek-harness-master/python/README.md
```

#### 3. 本地运行测试
```bash
cd E:/F_Workspace/Paper-Sum-Ped/deepseek-harness-master

# 安装依赖（需要 Node.js ≥22.19）
pnpm install

# 构建
pnpm run build

# 启动 Web UI
pnpm dsh web
```

#### 4. 工具调用流程追踪
- 启动后在 Web UI 中测试工具调用
- 观察控制台输出
- 分析网络请求（如果有 API）
- 记录用户体验

---

## 📝 待创建实验文档

### `experiments/dsh-evaluation/`

创建以下文件记录实验过程：

1. **`README.md`** - 实验目标与设置
2. **`installation-log.md`** - 安装过程记录
3. **`source-code-analysis.md`** - 源码结构分析
4. **`tool-calling-flow.md`** - 工具调用流程
5. **`python-sdk-test.md`** - Python SDK 测试
6. **`performance-metrics.md`** - 性能数据
7. **`evaluation-report.md`** - 最终评估

---

## 🎯 评估维度

### 技术维度

- [ ] 源码可读性
- [ ] 架构清晰度
- [ ] 工具注册机制实现
- [ ] Cordis 插件系统复杂度
- [ ] Python SDK 完整性

### 集成维度

- [ ] 与现有项目的兼容性
- [ ] Python ↔ TypeScript 通信开销
- [ ] 调试难度
- [ ] 文档完整性
- [ ] 学习曲线

### 实用维度

- [ ] 安装是否顺利
- [ ] 运行是否稳定
- [ ] UI 是否有用（对我们）
- [ ] 工具调用是否符合预期
- [ ] 错误处理是否健壮

---

## 🚧 当前状态

- ✅ 源码已下载并解压
- ✅ 顶层结构已识别
- 📋 等待详细探索
- 📋 等待本地运行测试
- 📋 等待评估报告输出

---

**下一步**: 创建 `experiments/dsh-evaluation/` 并开始 POC 实验

**预计时间**: 1-2天

**输出**: 数据支持的集成决策
