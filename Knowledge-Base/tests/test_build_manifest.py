from __future__ import annotations

import pytest

from ped_knowledge.storage.builds import BuildManifest, BuildStatus


def test_build_manifest_starts_staged_and_completes_only_with_hashed_artifacts() -> None:
    manifest = BuildManifest(
        build_id="chunk-build-001",
        kind="chunk",
        inputs={"source_sha256": "a" * 64, "policy_version": "parent-child-v1"},
        artifacts={"chunks.jsonl": "b" * 64},
    )

    assert manifest.status is BuildStatus.STAGED
    completed = manifest.complete()
    assert completed.status is BuildStatus.COMPLETE
    assert completed.build_id == manifest.build_id


def test_build_manifest_rejects_empty_or_invalid_artifact_hashes() -> None:
    with pytest.raises(ValueError):
        BuildManifest(
            build_id="chunk-build-002",
            kind="chunk",
            inputs={"source_sha256": "a" * 64},
            artifacts={"chunks.jsonl": "missing"},
        )


def test_failed_build_cannot_be_completed() -> None:
    manifest = BuildManifest(
        build_id="chunk-build-003",
        kind="chunk",
        inputs={"source_sha256": "a" * 64},
        artifacts={"chunks.jsonl": "b" * 64},
    ).fail("writer interrupted")

    assert manifest.status is BuildStatus.FAILED
    with pytest.raises(ValueError, match="failed"):
        manifest.complete()
