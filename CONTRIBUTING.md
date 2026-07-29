# Contributing

Ped-Agent uses a small, conventional Git workflow:

1. Create a branch from `main`.
2. Keep changes focused on one feature or fix.
3. Run `pytest -q` before opening a pull request.
4. Include tests for new behavior where practical.
5. Use the pull request template to summarize the change and validation.

## Development Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
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
```

## Knowledge Asset Rules

- Commit policies, search logs, screening decisions, metric snapshots, manifests,
  Gold Questions, and summary evaluation reports under `research/`.
- Never commit PDFs, parsed full text, SQLite catalogs, retrieval indexes, API keys,
  cookies, or raw trajectory data.
- Official literature manifests must pass `ped-agent library validate-manifest`.
- Do not lower quality thresholds or add X-tier exceptions merely to fill a quota.

## Commit Style

Use concise imperative commit messages, for example:

```text
scaffold phase 1 project structure
add analysis pipeline smoke tests
```
