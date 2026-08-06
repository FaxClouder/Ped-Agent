from __future__ import annotations

from pathlib import Path

from ped_agent.vision.contracts import SceneProfile


class SceneProfileRegistry:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def save(self, scene: SceneProfile) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"{scene.scene_id}.v{scene.version}.json"
        if path.exists():
            raise FileExistsError(f"immutable scene version already exists: {path.name}")
        path.write_text(scene.model_dump_json(indent=2), encoding="utf-8")
        return path

    def get(self, scene_id: str, version: int | None = None) -> SceneProfile:
        matches = self._versions(scene_id)
        if version is not None:
            matches = [item for item in matches if item[0] == version]
        if not matches:
            raise KeyError(scene_id if version is None else f"{scene_id}@{version}")
        return SceneProfile.model_validate_json(matches[-1][1].read_text(encoding="utf-8"))

    def list(self) -> tuple[SceneProfile, ...]:
        latest: dict[str, tuple[int, Path]] = {}
        if not self.root.exists():
            return ()
        for path in self.root.glob("*.v*.json"):
            try:
                scene = SceneProfile.model_validate_json(path.read_text(encoding="utf-8"))
            except ValueError:
                continue
            current = latest.get(scene.scene_id)
            if current is None or scene.version > current[0]:
                latest[scene.scene_id] = (scene.version, path)
        return tuple(
            SceneProfile.model_validate_json(latest[key][1].read_text(encoding="utf-8"))
            for key in sorted(latest)
        )

    def _versions(self, scene_id: str) -> list[tuple[int, Path]]:
        matches = []
        if not self.root.exists():
            return matches
        for path in self.root.glob(f"{scene_id}.v*.json"):
            scene = SceneProfile.model_validate_json(path.read_text(encoding="utf-8"))
            if scene.scene_id == scene_id:
                matches.append((scene.version, path))
        return sorted(matches)


__all__ = ["SceneProfileRegistry"]
