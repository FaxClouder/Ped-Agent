# Contributing

Ped-Agent uses a small, conventional Git workflow:

1. Create a branch from `main`.
2. Keep changes focused on one feature or fix.
3. Run the core, backend and frontend verification commands before opening a pull request.
4. Include tests for new behavior where practical.
5. Use the pull request template to summarize the change and validation.

## Development Setup

```powershell
py -3.12 -m venv .venv
uv sync --project backend
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m pytest tests -q
```

Optional module dependencies are installed separately:

```bash
pip install -e ".[rag]"
pip install -e ".[vision]"
```

The local knowledge backend has its own dependency environment and tests:

```powershell
cd backend
uv run --group dev python -m pytest -q --basetemp .pytest-tmp
uv run --group dev ruff check src tests

cd ..\frontend
npm ci
npm test
npm run build
```

## Knowledge Asset Rules

- Commit policies, search logs, screening decisions, metric snapshots, manifests,
  Gold Questions, and approved methods under `memPed/`.
- Never commit PDFs, parsed full text, SQLite catalogs, retrieval indexes, API keys,
  conversations, candidate methods, cookies, or raw trajectory data.
- Official literature manifests must pass `ped-agent library validate-manifest`.
- Do not lower quality thresholds or add X-tier exceptions merely to fill a quota.

## Commit Style

Use concise imperative commit messages, for example:

```text
scaffold phase 1 project structure
add analysis pipeline smoke tests
```
