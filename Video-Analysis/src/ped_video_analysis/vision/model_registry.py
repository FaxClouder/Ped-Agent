"""Compatibility import for the public resource registry."""

from ped_video_analysis.registry import ModelManifestRegistry, ModelWeightsMismatchError

__all__ = ["ModelManifestRegistry", "ModelWeightsMismatchError"]
