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
HISTORICAL_DOCUMENTS = {
    "docs/rag-architecture.md": "historical reference",
    "docs/data-analysis-module-design.md": "target module design",
    "docs/experiment-evaluation-module-design.md": "derived application design",
    "docs/vision-module-design.md": "target module design",
}
CANONICAL_SPEC_FILENAME = (
    "2026-08-06-ped-agent-three-module-architecture-design.md"
)


def test_approved_three_module_spec_exists() -> None:
    assert SPEC.exists()
    spec_text = SPEC.read_text(encoding="utf-8")
    for module_name in MODULE_NAMES:
        assert module_name in spec_text, (
            f"approved architecture spec is missing module: {module_name}"
        )


def test_readme_declares_three_module_architecture() -> None:
    readme_text = README.read_text(encoding="utf-8")
    for module_name in MODULE_NAMES:
        assert module_name in readme_text, f"README is missing module: {module_name}"
    spec_target = SPEC.relative_to(ROOT).as_posix()
    assert f"]({spec_target})" in readme_text, (
        f"README is missing architecture spec link target: {spec_target}"
    )


def test_broad_design_documents_declare_their_current_status() -> None:
    for relative_path, expected_status in HISTORICAL_DOCUMENTS.items():
        document_text = (ROOT / relative_path).read_text(encoding="utf-8")
        header = "\n".join(document_text.splitlines()[:8]).lower()
        assert expected_status in header, (
            f"{relative_path} is missing status phrase: {expected_status}"
        )
        assert CANONICAL_SPEC_FILENAME in header, (
            f"{relative_path} header is missing canonical spec filename: "
            f"{CANONICAL_SPEC_FILENAME}"
        )
