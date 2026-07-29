from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspacePaths:
    repo_root: Path
    library_root: Path
    inbox_dir: Path
    literature_inbox_dir: Path
    regulations_inbox_dir: Path
    objects_dir: Path
    derived_dir: Path
    reports_dir: Path
    catalog_path: Path
    index_path: Path

    @classmethod
    def from_repo_root(cls, repo_root: Path) -> WorkspacePaths:
        root = repo_root.resolve()
        library_root = root / "backend" / "storage" / "library"
        return cls(
            repo_root=root,
            library_root=library_root,
            inbox_dir=library_root / "inbox",
            literature_inbox_dir=library_root / "inbox" / "literature",
            regulations_inbox_dir=library_root / "inbox" / "regulations",
            objects_dir=library_root / "objects",
            derived_dir=library_root / "derived",
            reports_dir=library_root / "reports",
            catalog_path=library_root / "catalog" / "catalog.sqlite3",
            index_path=library_root / "indexes" / "fts.sqlite3",
        )

    def ensure_local_dirs(self) -> None:
        for directory in (
            self.inbox_dir,
            self.literature_inbox_dir,
            self.regulations_inbox_dir,
            self.objects_dir,
            self.derived_dir,
            self.reports_dir,
            self.catalog_path.parent,
            self.index_path.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)
