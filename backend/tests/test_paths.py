from pathlib import Path

from ped_agent.paths import WorkspacePaths


def test_workspace_paths_keep_library_below_backend(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)

    assert paths.library_root == tmp_path / "backend" / "storage" / "library"
    assert paths.catalog_path == paths.library_root / "catalog" / "catalog.sqlite3"
    assert paths.index_path == paths.library_root / "indexes" / "fts.sqlite3"
    assert paths.inbox_dir == paths.library_root / "inbox"
