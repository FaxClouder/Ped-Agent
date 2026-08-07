import ast
from pathlib import Path

import ped_agent
import ped_knowledge
import pytest

import ped_agent_server

ROOT = Path(__file__).resolve().parents[2]


def test_core_and_server_are_distinct_python_packages() -> None:
    core_path = Path(ped_agent.__file__).resolve()
    server_path = Path(ped_agent_server.__file__).resolve()

    assert core_path != server_path
    assert core_path.parent.name == "ped_agent"
    assert server_path.parent.name == "ped_agent_server"


def test_knowledge_package_is_distinct_and_server_independent() -> None:
    knowledge_path = Path(ped_knowledge.__file__).resolve()

    assert knowledge_path.parent.name == "ped_knowledge"
    assert "Knowledge-Base" in knowledge_path.parts
    for path in (ROOT / "Knowledge-Base" / "src" / "ped_knowledge").rglob("*.py"):
        module = ast.parse(path.read_text(encoding="utf-8"))
        imports = [
            node.module or "" for node in ast.walk(module) if isinstance(node, ast.ImportFrom)
        ]
        assert not any(name.startswith("ped_agent_server") for name in imports), path


@pytest.mark.parametrize(
    "relative_path",
    [
        Path("src/ped_agent/main.py"),
        Path("src/ped_agent/agent/graph.py"),
    ],
)
def test_legacy_modules_name_the_authoritative_runtime(relative_path: Path) -> None:
    source_path = ROOT / relative_path
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    docstring = ast.get_docstring(module) or ""

    for marker in ("Legacy", "ped_agent_server", "EvidenceGraph"):
        assert marker in docstring, f"{relative_path}: missing {marker!r} in module docstring"
