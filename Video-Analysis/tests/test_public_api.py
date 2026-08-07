from __future__ import annotations

from ped_agent.analysis.vision_pipeline import AnalysisProfile as LegacyAnalysisProfile
from ped_agent.vision.contracts import ModelManifest as LegacyModelManifest

from ped_video_analysis import (
    DEFAULT_PATHS,
    AnalysisProfile,
    create_model_registry,
    load_analysis_profile,
    load_postprocess_profile,
)
from ped_video_analysis.vision.contracts import ModelManifest


def test_module_owns_configs_weights_and_runtime_paths() -> None:
    assert DEFAULT_PATHS.root.name == "Video-Analysis"
    assert DEFAULT_PATHS.models.is_dir()
    assert DEFAULT_PATHS.trackers.is_dir()
    assert DEFAULT_PATHS.runtime == DEFAULT_PATHS.root / "runtime"
    assert list((DEFAULT_PATHS.root / "src" / "ped_video_analysis" / "tools").glob("*.py")) == []


def test_public_api_loads_module_profiles() -> None:
    analysis = load_analysis_profile()
    postprocess = load_postprocess_profile()

    assert analysis.time_window_seconds == 1.0
    assert analysis.interaction_radius_metres == 5.0
    assert postprocess.max_interpolation_gap_seconds == 0.4
    assert postprocess.hampel_window_points == 5


def test_default_registry_resolves_weights_from_module_directory() -> None:
    registry = create_model_registry()
    manifests = registry.list()

    assert len(manifests) == 1
    assert manifests[0].weights_path == DEFAULT_PATHS.models / "yolo26x" / "weights" / "yolo26x.pt"
    assert manifests[0].tracker.backend == "bytetrack"


def test_legacy_imports_alias_the_extracted_public_types() -> None:
    assert LegacyAnalysisProfile is AnalysisProfile
    assert LegacyModelManifest is ModelManifest
