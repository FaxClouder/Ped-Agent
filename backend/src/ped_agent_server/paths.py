from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspacePaths:
    repo_root: Path
    memped_root: Path
    knowledge_root: Path
    literature_root: Path
    regulations_root: Path
    literature_files_dir: Path
    regulations_files_dir: Path
    literature_records_dir: Path
    literature_reviews_dir: Path
    regulations_records_dir: Path
    derived_dir: Path
    reports_dir: Path
    conversations_root: Path
    conversation_files_dir: Path
    methods_root: Path
    method_candidates_dir: Path
    method_approved_dir: Path
    catalog_path: Path
    index_path: Path
    vector_index_dir: Path
    agent_db_path: Path

    @classmethod
    def from_repo_root(cls, repo_root: Path) -> WorkspacePaths:
        root = repo_root.resolve()
        memped_root = root / "memPed"
        knowledge_root = memped_root / "knowledge"
        literature_root = knowledge_root / "literature"
        regulations_root = knowledge_root / "regulations"
        conversations_root = memped_root / "conversations"
        methods_root = memped_root / "methods"
        return cls(
            repo_root=root,
            memped_root=memped_root,
            knowledge_root=knowledge_root,
            literature_root=literature_root,
            regulations_root=regulations_root,
            literature_files_dir=literature_root / "files",
            regulations_files_dir=regulations_root / "files",
            literature_records_dir=literature_root / "records",
            literature_reviews_dir=literature_root / "reviews",
            regulations_records_dir=regulations_root / "records",
            derived_dir=knowledge_root / "derived",
            reports_dir=knowledge_root / "reports",
            conversations_root=conversations_root,
            conversation_files_dir=conversations_root / "files",
            methods_root=methods_root,
            method_candidates_dir=methods_root / "candidates",
            method_approved_dir=methods_root / "approved",
            catalog_path=knowledge_root / "knowledge.sqlite3",
            index_path=knowledge_root / "fts.sqlite3",
            vector_index_dir=knowledge_root / "vectors",
            agent_db_path=conversations_root / "conversations.sqlite3",
        )

    def ensure_local_dirs(self) -> None:
        for directory in (
            self.literature_files_dir,
            self.literature_reviews_dir,
            self.regulations_files_dir,
            self.derived_dir,
            self.reports_dir,
            self.conversation_files_dir,
            self.method_candidates_dir,
            self.method_approved_dir,
            self.vector_index_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def resource_files_dir(self, resource_type: str) -> Path:
        if resource_type in {"regulation", "standard"}:
            return self.regulations_files_dir
        return self.literature_files_dir
