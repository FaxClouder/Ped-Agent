from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
SPEC = (
    ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-08-06-ped-agent-three-module-architecture-design.md"
)
MODULE_NAMES = (
    "知识与证据底座",
    "检测追踪与流动分析",
    "LLM 问答与会话",
)


def test_approved_three_module_spec_exists() -> None:
    assert SPEC.exists()
    spec_text = SPEC.read_text(encoding="utf-8")
    assert all(name in spec_text for name in MODULE_NAMES)


def test_readme_declares_three_module_architecture() -> None:
    readme_text = README.read_text(encoding="utf-8")
    assert all(name in readme_text for name in MODULE_NAMES)
    assert SPEC.name in readme_text
