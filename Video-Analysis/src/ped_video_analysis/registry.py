from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from ped_video_analysis.schemas import DetectorManifest, ModelManifest, TrackerManifest


class ModelWeightsMismatchError(ValueError):
    pass


class ModelManifestRegistry:
    """Load detector resources and combine them with one selected tracker config."""

    def __init__(
        self,
        manifests_dir: Path,
        *,
        trackers_dir: Path | None = None,
        tracker_id: str = "bytetrack",
        weights_dir: Path | None = None,
    ):
        self.manifests_dir = manifests_dir.resolve()
        self.models_dir = self.manifests_dir
        self.trackers_dir = trackers_dir.resolve() if trackers_dir is not None else None
        self.tracker_id = tracker_id
        self.weights_dir = weights_dir.resolve() if weights_dir is not None else None

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
        paths: set[Path] = set()
        for suffix in ("json", "yaml", "yml"):
            paths.update(self.manifests_dir.glob(f"*.{suffix}"))
            paths.update(self.manifests_dir.glob(f"*/model.{suffix}"))
        return tuple(sorted(paths))

    def _load(self, path: Path) -> ModelManifest:
        payload = _read_mapping(path)
        if "tracker" in payload:
            manifest = ModelManifest.model_validate(payload)
        else:
            detector = DetectorManifest.model_validate(payload)
            tracker = self._load_tracker(self.tracker_id)
            manifest = ModelManifest.model_validate(
                {
                    **detector.model_dump(mode="python"),
                    "tracker": tracker.settings.model_dump(mode="python"),
                }
            )
        weights_path = manifest.weights_path
        if not weights_path.is_absolute():
            root = self.weights_dir or path.parent
            weights_path = (root / weights_path).resolve()
        return manifest.model_copy(update={"weights_path": weights_path})

    def _load_tracker(self, tracker_id: str) -> TrackerManifest:
        if self.trackers_dir is None:
            raise ValueError(
                f"model manifest does not embed tracker settings and no trackers directory "
                f"was configured: {tracker_id}"
            )
        for suffix in ("json", "yaml", "yml"):
            candidates = (
                self.trackers_dir / tracker_id / f"tracker.{suffix}",
                self.trackers_dir / f"{tracker_id}.{suffix}",
            )
            for path in candidates:
                if path.is_file():
                    return TrackerManifest.model_validate(_read_mapping(path))
        raise FileNotFoundError(self.trackers_dir / tracker_id / "tracker.yaml")

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


def _read_mapping(path: Path) -> dict[str, Any]:
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"configuration must contain a mapping: {path}")
    return payload


__all__ = ["ModelManifestRegistry", "ModelWeightsMismatchError"]
