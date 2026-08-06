from pathlib import Path

from ped_agent_server.vision_runtime import build_vision_runtime


def test_build_vision_runtime_uses_local_storage_and_single_worker(tmp_path: Path) -> None:
    runtime = build_vision_runtime(tmp_path)

    assert runtime.storage.paths.root == tmp_path / "backend" / "storage" / "vision"
    assert runtime.repository.path == runtime.storage.paths.root / "vision.sqlite3"
    assert runtime.repository.list_tasks() == []
    assert runtime.service.worker is None
    assert runtime.model_registry.manifests_dir == runtime.storage.paths.model_manifests_dir
    assert runtime.scene_registry.root == runtime.storage.paths.scenes_dir
