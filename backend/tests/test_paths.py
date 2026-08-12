from pathlib import Path

from ped_agent_server.paths import WorkspacePaths


def test_workspace_paths_keep_memped_data_below_repository_root(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)

    assert paths.memped_root == tmp_path / "memPed"
    assert paths.knowledge_root == paths.memped_root / "knowledge"
    assert paths.catalog_path == paths.knowledge_root / "knowledge.sqlite3"
    assert paths.index_path == paths.knowledge_root / "fts.sqlite3"
    assert paths.literature_files_dir == paths.knowledge_root / "literature" / "files"
    assert paths.literature_reviews_dir == paths.knowledge_root / "literature" / "reviews"
    assert paths.regulations_files_dir == paths.knowledge_root / "regulations" / "files"
    assert paths.agent_db_path == paths.memped_root / "conversations" / "conversations.sqlite3"
    assert paths.vector_index_dir == paths.knowledge_root / "vectors"


def test_workspace_paths_create_three_component_data_directories(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)

    paths.ensure_local_dirs()

    assert paths.literature_files_dir.is_dir()
    assert paths.literature_reviews_dir.is_dir()
    assert paths.regulations_files_dir.is_dir()
    assert paths.conversation_files_dir.is_dir()
    assert paths.method_candidates_dir.is_dir()
    assert paths.method_approved_dir.is_dir()


def test_workspace_paths_separate_literature_from_regulations(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)

    assert paths.resource_files_dir("literature") == paths.literature_files_dir
    assert paths.resource_files_dir("regulation") == paths.regulations_files_dir
    assert paths.resource_files_dir("standard") == paths.regulations_files_dir
