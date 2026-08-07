from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
LEGACY_MAP = ROOT / "docs" / "legacy-scaffold.md"
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
CANONICAL_SPEC_FILENAME = "2026-08-06-ped-agent-three-module-architecture-design.md"
ACTIVE_RUNTIME_HEADING = "## 📋 Active runtime"
LEGACY_SCAFFOLD_HEADING = "## ⚠️ Legacy scaffold"
SHARED_CODE_HEADING = "## 🔗 Shared code that remains active"
ACTIVE_RUNTIME_ROWS = (
    "| CLI and server startup | `ped_agent_server.cli` |",
    ("| Verified answer graph | `ped_agent.agent.evidence_graph.EvidenceGraph` |"),
    (
        "| Knowledge program | `Knowledge-Base/src/ped_knowledge/` — ingestion, "
        "parsing, Chunking, storage, indexing, retrieval, Rerank, and evaluation |"
    ),
    (
        "| Server and cross-module adapters | `backend/src/ped_agent_server/` — "
        "API/SSE, CLI, settings, Run lifecycle, provider assembly, external search, "
        "and observability |"
    ),
    (
        "| memPed data root | `memPed/` — governed knowledge, conversation, "
        "and reviewed-method data assets |"
    ),
)
LEGACY_SCAFFOLD_ROWS = (
    (
        "| `src/ped_agent/main.py` | Early compatibility CLI; reads the root "
        "`.env`, but is not the server entrypoint |"
    ),
    "| `src/ped_agent/agent/graph.py` | Generic routing prototype |",
)
SHARED_CODE_ENTRIES = (
    "- `src/ped_agent/agent/contracts.py`",
    "- `src/ped_agent/agent/policy.py`",
)


def test_approved_three_module_spec_exists() -> None:
    assert SPEC.exists()
    spec_text = SPEC.read_text(encoding="utf-8")
    header = "\n".join(spec_text.splitlines()[:8])
    status_issues = []
    if "状态：已批准" not in header:
        status_issues.append("add `状态：已批准` within the first 8 lines")
    if "等待书面规格复核" in header:
        status_issues.append("remove the stale `等待书面规格复核` wording")
    assert not status_issues, "canonical architecture spec header must:\n- " + "\n- ".join(
        status_issues
    )
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
            f"{relative_path} header is missing canonical spec filename: {CANONICAL_SPEC_FILENAME}"
        )


def test_readme_links_an_explicit_legacy_code_map() -> None:
    assert LEGACY_MAP.is_file(), f"legacy code map is missing: {LEGACY_MAP}"
    legacy_map_text = LEGACY_MAP.read_text(encoding="utf-8")
    readme_text = README.read_text(encoding="utf-8")

    for heading in (
        ACTIVE_RUNTIME_HEADING,
        LEGACY_SCAFFOLD_HEADING,
        SHARED_CODE_HEADING,
    ):
        heading_count = legacy_map_text.count(heading)
        assert heading_count == 1, (
            f"legacy code map must contain exactly one {heading!r} heading; found {heading_count}"
        )

    active_tail = legacy_map_text.split(ACTIVE_RUNTIME_HEADING, maxsplit=1)[1]
    active_section, legacy_tail = active_tail.split(LEGACY_SCAFFOLD_HEADING, maxsplit=1)
    legacy_section, shared_section = legacy_tail.split(SHARED_CODE_HEADING, maxsplit=1)

    for expected_row in ACTIVE_RUNTIME_ROWS:
        assert expected_row in active_section, (
            f"active runtime section is missing exact row: {expected_row}"
        )
    for expected_row in LEGACY_SCAFFOLD_ROWS:
        assert expected_row in legacy_section, (
            f"legacy scaffold section is missing exact row: {expected_row}"
        )
    for expected_entry in SHARED_CODE_ENTRIES:
        assert expected_entry in shared_section, (
            f"shared active-code section is missing entry: {expected_entry}"
        )

    legacy_map_target = LEGACY_MAP.relative_to(ROOT).as_posix()
    assert f"]({legacy_map_target})" in readme_text, (
        f"README is missing legacy code map link target: {legacy_map_target}"
    )


def test_changelog_records_three_module_alignment() -> None:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased_heading = "## Unreleased"
    assert unreleased_heading in text, "CHANGELOG is missing an Unreleased section"
    unreleased_tail = text.split(unreleased_heading, maxsplit=1)[1]
    unreleased_section = unreleased_tail.split("\n## ", maxsplit=1)[0]

    for module_name in MODULE_NAMES:
        assert module_name in unreleased_section, (
            f"CHANGELOG Unreleased section is missing aligned module: {module_name}"
        )
    application_classification = "applications built from the foundation modules"
    assert application_classification in unreleased_section, (
        "CHANGELOG Unreleased section is missing the foundation-module application classification"
    )
