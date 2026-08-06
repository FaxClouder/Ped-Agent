from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from ped_agent.vision.adapters import (
    BoxMotByteTrackAdapter,
    OpenCVFrameSequence,
    UltralyticsDetector,
)
from ped_agent.vision.contracts import ModelManifest, SemanticClass
from ped_agent.vision.runner import DecodedDetection


def manifest(tmp_path: Path) -> ModelManifest:
    return ModelManifest(
        model_id="mixed-flow-v1",
        name="Mixed flow detector",
        version="1.0.0",
        backend="ultralytics",
        weights_path=tmp_path / "mixed.pt",
        sha256="a" * 64,
        input_size=1280,
        class_map={
            0: SemanticClass.PEDESTRIAN,
            1: SemanticClass.PEDESTRIAN_UMBRELLA,
            2: SemanticClass.BICYCLE_RIDER,
            3: SemanticClass.EBIKE_RIDER,
        },
        keypoint_names=("left_foot", "right_foot", "front_wheel", "rear_wheel"),
        contact_keypoints={
            SemanticClass.PEDESTRIAN: ("left_foot", "right_foot"),
            SemanticClass.PEDESTRIAN_UMBRELLA: ("left_foot", "right_foot"),
            SemanticClass.BICYCLE_RIDER: ("front_wheel", "rear_wheel"),
            SemanticClass.EBIKE_RIDER: ("front_wheel", "rear_wheel"),
        },
    )


class FakeTensor:
    def __init__(self, value):
        self.value = np.asarray(value)

    def cpu(self):
        return self

    def numpy(self):
        return self.value

    def __len__(self):
        return len(self.value)

    def __getitem__(self, index):
        return FakeTensor(self.value[index])

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)


class FakeBoxes:
    xyxy = FakeTensor([[10, 20, 30, 60]])
    conf = FakeTensor([0.91])
    cls = FakeTensor([0])

    def __len__(self):
        return 1


class FakeKeypoints:
    xy = FakeTensor([[[18, 58], [22, 58], [0, 0], [0, 0]]])
    conf = FakeTensor([[0.9, 0.8, 0.0, 0.0]])


class FakeModel:
    def __init__(self):
        self.calls = []

    def __call__(self, frame, **kwargs):
        self.calls.append(kwargs)
        return [type("Result", (), {"boxes": FakeBoxes(), "keypoints": FakeKeypoints()})()]


def test_ultralytics_detector_uses_manifest_input_size_and_precision(tmp_path: Path) -> None:
    model = FakeModel()
    detector = UltralyticsDetector(
        manifest(tmp_path),
        model_factory=lambda _: model,
        device_resolver=lambda _: "cpu",
    )

    detections = detector.detect(object())

    assert detections[0].keypoints["left_foot"].x == 18
    assert model.calls[0]["imgsz"] == 1280
    assert model.calls[0]["conf"] == pytest.approx(0.10)
    assert model.calls[0]["iou"] == pytest.approx(0.65)
    assert model.calls[0]["device"] == "cpu"
    assert model.calls[0]["half"] is False


class FakeTrackEngine:
    def __init__(self):
        self.inputs = []

    def update(self, detections, frame):
        self.inputs.append(detections)
        return np.array([[10, 20, 30, 60, 7, 0.88, 0, 0]], dtype=float)


def test_boxmot_adapter_tracks_compatible_groups_and_keeps_detection_index(
    tmp_path: Path,
) -> None:
    created = {}

    def factory(**kwargs):
        created.update(kwargs)
        return FakeTrackEngine()

    adapter = BoxMotByteTrackAdapter(
        manifest(tmp_path),
        source_fps=25,
        tracker_factory=factory,
    )
    detections = (
        DecodedDetection(
            raw_class_id=1,
            bbox_xyxy=(10, 20, 30, 60),
            confidence=0.9,
            keypoints={},
        ),
    )

    tracked = adapter.update(
        detections,
        (SemanticClass.PEDESTRIAN_UMBRELLA,),
        object(),
    )

    assert created["track_thresh"] == pytest.approx(0.25)
    assert created["track_buffer"] == 30
    assert adapter.engine.inputs[0][0, 5] == 0
    assert tracked[0].track_id == 7
    assert tracked[0].detection_index == 0


class FakeCapture:
    def __init__(self):
        self.frames = [np.zeros((4, 6, 3)), np.ones((4, 6, 3))]
        self.index = 0
        self.released = False

    def isOpened(self):
        return True

    def get(self, key):
        return {1: 25.0, 2: 2, 3: 6, 4: 4}[key]

    def read(self):
        if self.index >= len(self.frames):
            return False, None
        frame = self.frames[self.index]
        self.index += 1
        return True, frame

    def release(self):
        self.released = True


class FakeCV2:
    CAP_PROP_FPS = 1
    CAP_PROP_FRAME_COUNT = 2
    CAP_PROP_FRAME_WIDTH = 3
    CAP_PROP_FRAME_HEIGHT = 4

    def __init__(self):
        self.capture = FakeCapture()

    def VideoCapture(self, source):
        return self.capture


def test_opencv_frame_sequence_reports_metadata_and_releases_capture(tmp_path: Path) -> None:
    cv2 = FakeCV2()
    sequence = OpenCVFrameSequence(tmp_path / "source.mp4", cv2_module=cv2)

    frames = list(sequence)

    assert sequence.metadata.resolution == (6, 4)
    assert [item.index for item in frames] == [0, 1]
    assert frames[1].timestamp == pytest.approx(0.04)
    assert cv2.capture.released is True
