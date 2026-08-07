# Ped-Agent 配置系统

## 当前边界

项目只使用仓库根目录 `.env` 和进程环境作为持久运行配置来源。`.env.example` 是唯一配置
模板，实际 `.env` 被 Git 忽略，不得提交密钥、Cookie 或 Token；少数 CLI 参数仍可对单次
命令进行显式覆盖。

旧 `config/*.yaml` 分层配置、OmegaConf 加载器以及无命名空间的 API Key 别名已经移除。

## 加载路径

- 服务端：`backend/src/ped_agent_server/settings.py` 中的 `AgentSettings`
- 仓库脚本：`src/ped_agent/utils/config.py` 中的 `load_project_env()`
- 配置模板：仓库根目录 `.env.example`

服务端使用 `PED_AGENT_` 前缀和双下划线表达嵌套字段。例如：

```dotenv
PED_AGENT_ANSWER__MODEL=deepseek-v4-flash
PED_AGENT_ANSWER__API_KEY=
PED_AGENT_EMBEDDING__MODEL=text-embedding-3-small
PED_AGENT_EMBEDDING__API_KEY=
PED_AGENT_LANGSMITH__ENABLED=false
PED_AGENT_LANGSMITH__API_KEY=
```

回答模型、Embedding、外部搜索和 LangSmith 启用后所需的凭据都由 `AgentSettings` 在启动时
校验。LangSmith 默认关闭，且只允许 `redacted` 内容策略。

## 本地初始化

```powershell
Copy-Item .env.example .env
uv run --project backend ped-agent agent doctor
```

修改 `.env` 后需要重启服务；Embedding 模型、Base URL 或维度变化后还要执行：

```powershell
uv run --project backend ped-agent agent rebuild-vector-index
```

## 安全规则

- 不在 YAML、源码、测试夹具、日志或命令历史中写入真实密钥。
- 不再使用 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`LANGSMITH_API_KEY` 等旧别名。
- 使用 `PED_AGENT_ANSWER__API_KEY`、`PED_AGENT_EMBEDDING__API_KEY`、
  `PED_AGENT_LANGSMITH__API_KEY` 等明确作用域变量。
- `agent doctor` 可以展示配置状态，但必须持续隐藏密钥和带凭据 URL。
