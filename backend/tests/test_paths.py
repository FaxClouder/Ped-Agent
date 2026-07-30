from pathlib import Path

from ped_agent_server.paths import WorkspacePaths


def test_workspace_paths_keep_library_below_backend(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)

    assert paths.library_root == tmp_path / "backend" / "storage" / "library"
    assert paths.catalog_path == paths.library_root / "catalog" / "catalog.sqlite3"
    assert paths.index_path == paths.library_root / "indexes" / "fts.sqlite3"
    assert paths.inbox_dir == paths.library_root / "inbox"
    assert paths.literature_inbox_dir == paths.inbox_dir / "literature"
    assert paths.regulations_inbox_dir == paths.inbox_dir / "regulations"


def test_workspace_paths_create_separate_local_inboxes(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)

    paths.ensure_local_dirs()

    assert paths.literature_inbox_dir.is_dir()
    assert paths.regulations_inbox_dir.is_dir()
