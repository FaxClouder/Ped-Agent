from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "Knowledge-Base" / "src" / "ped_knowledge"


def test_knowledge_package_never_imports_server_package() -> None:
    offenders: list[str] = []
    for path in PACKAGE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            if any(
                name == "ped_agent_server" or name.startswith("ped_agent_server.") for name in names
            ):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_memped_remains_data_only() -> None:
    forbidden = {".py", ".js", ".ts", ".tsx", ".sh", ".ps1"}
    offenders = [
        str(path.relative_to(ROOT))
        for path in (ROOT / "memPed").rglob("*")
        if path.is_file() and path.suffix.lower() in forbidden
    ]
    assert offenders == []
