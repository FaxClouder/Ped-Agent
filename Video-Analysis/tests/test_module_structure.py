from __future__ import annotations

import ast
import importlib
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = MODULE_ROOT / "src" / "ped_video_analysis"


def test_three_business_blocks_are_importable() -> None:
    for package in ("extraction", "processing", "analysis"):
        imported = importlib.import_module(f"ped_video_analysis.{package}")
        assert imported.__name__ == f"ped_video_analysis.{package}"


def test_shared_support_packages_are_importable() -> None:
    for package in ("contracts", "infrastructure"):
        imported = importlib.import_module(f"ped_video_analysis.{package}")
        assert imported.__name__ == f"ped_video_analysis.{package}"


def test_business_blocks_do_not_import_each_other() -> None:
    business_blocks = {"extraction", "processing", "analysis"}
    for block in business_blocks:
        forbidden = business_blocks - {block}
        for source_path in (PACKAGE_ROOT / block).rglob("*.py"):
            tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
            imported_modules = {
                node.module or ""
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            }
            imported_modules.update(
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            )
            for sibling in forbidden:
                forbidden_prefix = f"ped_video_analysis.{sibling}"
                assert not any(
                    module == forbidden_prefix or module.startswith(f"{forbidden_prefix}.")
                    for module in imported_modules
                ), f"{source_path} must not import the {sibling} block directly"


def test_module_directory_documents_each_boundary() -> None:
    for directory in (
        PACKAGE_ROOT / "contracts",
        PACKAGE_ROOT / "extraction",
        PACKAGE_ROOT / "processing",
        PACKAGE_ROOT / "analysis",
        PACKAGE_ROOT / "infrastructure",
    ):
        assert (directory / "README.md").is_file()

    assert (MODULE_ROOT / "docs" / "directory-design.md").is_file()


def test_test_directories_follow_business_boundaries() -> None:
    for directory in ("contracts", "extraction", "processing", "analysis", "infrastructure"):
        assert (MODULE_ROOT / "tests" / directory / "README.md").is_file()
