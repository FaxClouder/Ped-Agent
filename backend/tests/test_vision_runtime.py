from pathlib import Path

from ped_agent_server.vision_runtime import build_vision_runtime


def test_build_vision_runtime_uses_local_storage_and_single_worker(tmp_path: Path) -> None:
    runtime = build_vision_runtime(tmp_path)

    module_root = tmp_path / "Video-Analysis"
    assert runtime.storage.paths.root == module_root / "runtime"
    assert runtime.repository.path == runtime.storage.paths.root / "vision.sqlite3"
    assert runtime.repository.list_tasks() == []
    assert runtime.service.worker is None
    assert runtime.model_registry.models_dir == module_root / "models"
    assert runtime.model_registry.trackers_dir == module_root / "trackers"
    assert runtime.model_registry.weights_dir is None
    assert runtime.scene_registry.root == runtime.storage.paths.scenes_dir
