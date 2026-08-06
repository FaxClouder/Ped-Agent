from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from ped_agent.vision.contracts import ModelManifest


class ModelWeightsMismatchError(ValueError):
    pass


class ModelManifestRegistry:
    def __init__(self, manifests_dir: Path):
        self.manifests_dir = manifests_dir.resolve()

    def list(self) -> tuple[ModelManifest, ...]:
        manifests = [self._load(path) for path in self._manifest_paths()]
        by_id: dict[str, ModelManifest] = {}
        for manifest in manifests:
            if manifest.model_id in by_id:
                raise ValueError(f"duplicate model manifest id: {manifest.model_id}")
            by_id[manifest.model_id] = manifest
        return tuple(by_id[key] for key in sorted(by_id))

    def get(self, model_id: str) -> ModelManifest:
        for manifest in self.list():
            if manifest.model_id == model_id:
                self._verify_weights(manifest)
                return manifest
        raise KeyError(model_id)

    def manifest_sha256(self, model_id: str) -> str:
        manifest = self.get(model_id)
        payload = manifest.model_dump_json(exclude={"weights_path"})
        return hashlib.sha256(payload.encode()).hexdigest()

    def _manifest_paths(self) -> tuple[Path, ...]:
        if not self.manifests_dir.exists():
            return ()
        paths = [
            path
            for pattern in ("*.json", "*.yaml", "*.yml")
            for path in self.manifests_dir.glob(pattern)
        ]
        return tuple(sorted(paths))

    def _load(self, path: Path) -> ModelManifest:
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        manifest = ModelManifest.model_validate(payload)
        weights_path = manifest.weights_path
        if not weights_path.is_absolute():
            weights_path = (path.parent / weights_path).resolve()
        return manifest.model_copy(update={"weights_path": weights_path})

    @staticmethod
    def _verify_weights(manifest: ModelManifest) -> None:
        if not manifest.weights_path.is_file():
            raise FileNotFoundError(manifest.weights_path)
        digest = hashlib.sha256()
        with manifest.weights_path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != manifest.sha256:
            raise ModelWeightsMismatchError(
                f"model weights SHA-256 does not match manifest: {manifest.model_id}"
            )


__all__ = ["ModelManifestRegistry", "ModelWeightsMismatchError"]
