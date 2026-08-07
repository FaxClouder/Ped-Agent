from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredVideo:
    path: Path
    sha256: str


@dataclass(frozen=True)
class VisionStoragePaths:
    root: Path
    tasks_dir: Path
    artifacts_dir: Path
    exports_dir: Path
    model_manifests_dir: Path
    scenes_dir: Path


class VisionStorage:
    def __init__(
        self,
        root: Path,
        *,
        model_manifests_dir: Path | None = None,
        scenes_dir: Path | None = None,
    ):
        resolved = root.resolve()
        self.paths = VisionStoragePaths(
            root=resolved,
            tasks_dir=resolved / "tasks",
            artifacts_dir=resolved / "artifacts",
            exports_dir=resolved / "exports",
            model_manifests_dir=(model_manifests_dir or resolved / "models").resolve(),
            scenes_dir=(scenes_dir or resolved / "scenes").resolve(),
        )

    def ensure_dirs(self) -> None:
        for directory in (
            self.paths.tasks_dir,
            self.paths.artifacts_dir,
            self.paths.exports_dir,
            self.paths.model_manifests_dir,
            self.paths.scenes_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def ingest_video(self, task_id: str, source: Path) -> StoredVideo:
        if not source.is_file():
            raise FileNotFoundError(source)
        self.ensure_dirs()
        destination_dir = self.paths.tasks_dir / task_id / "source"
        destination = destination_dir / source.name
        if destination_dir.exists():
            raise FileExistsError(f"immutable task source already exists: {task_id}")
        destination_dir.mkdir(parents=True)
        shutil.copy2(source, destination)
        return StoredVideo(path=destination, sha256=_file_sha256(destination))

    def artifact_dir(self, task_id: str, artifact_id: str) -> Path:
        return self.paths.artifacts_dir / task_id / artifact_id

    def export_dir(self, task_id: str) -> Path:
        return self.paths.exports_dir / task_id


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = ["StoredVideo", "VisionStorage", "VisionStoragePaths"]
