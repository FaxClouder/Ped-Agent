from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ped_video_analysis.paths import VideoAnalysisPaths
from ped_video_analysis.registry import ModelManifestRegistry

from ped_agent_server.scene_registry import SceneProfileRegistry
from ped_agent_server.vision_processor import VisionPipelineProcessor
from ped_agent_server.vision_repository import VisionRepository
from ped_agent_server.vision_service import VisionTaskService
from ped_agent_server.vision_storage import VisionStorage


@dataclass
class VisionRuntime:
    storage: VisionStorage
    repository: VisionRepository
    model_registry: ModelManifestRegistry
    scene_registry: SceneProfileRegistry
    service: VisionTaskService

    async def close(self) -> None:
        await self.service.shutdown()


def build_vision_runtime(repo_root: Path) -> VisionRuntime:
    module_paths = VideoAnalysisPaths.from_root(repo_root.resolve() / "Video-Analysis")
    module_paths.ensure_local_dirs()
    storage = VisionStorage(
        module_paths.runtime,
        model_manifests_dir=module_paths.models,
        scenes_dir=module_paths.runtime / "scenes",
    )
    storage.ensure_dirs()
    repository = VisionRepository(storage.paths.root / "vision.sqlite3")
    repository.initialize()
    model_registry = ModelManifestRegistry(
        storage.paths.model_manifests_dir,
        trackers_dir=module_paths.trackers,
    )
    scene_registry = SceneProfileRegistry(storage.paths.scenes_dir)
    processor = VisionPipelineProcessor(
        storage=storage,
        model_registry=model_registry,
        scene_registry=scene_registry,
    )
    service = VisionTaskService(repository, processor)
    return VisionRuntime(
        storage=storage,
        repository=repository,
        model_registry=model_registry,
        scene_registry=scene_registry,
        service=service,
    )


__all__ = ["VisionRuntime", "build_vision_runtime"]
