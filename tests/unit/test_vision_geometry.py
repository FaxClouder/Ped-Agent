from __future__ import annotations

import numpy as np
import pytest

from ped_agent.vision.calibration import (
    CalibrationPoint,
    CharucoBoardSpec,
    FullCameraCalibration,
    calibrate_charuco_images,
    solve_full_camera_from_ground_points,
    solve_homography,
)
from ped_agent.vision.contact_points import extract_contact_point
from ped_agent.vision.contracts import (
    CalibrationMode,
    ContactPointQuality,
    KeypointObservation,
    SemanticClass,
)


def test_pedestrian_contact_point_uses_midpoint_between_feet() -> None:
    result = extract_contact_point(
        semantic_class=SemanticClass.PEDESTRIAN,
        bbox_xyxy=(10.0, 20.0, 30.0, 60.0),
        keypoints={
            "left_foot": KeypointObservation(x=18.0, y=58.0, confidence=0.9),
            "right_foot": KeypointObservation(x=24.0, y=60.0, confidence=0.8),
        },
        minimum_confidence=0.35,
    )

    assert (result.point.x, result.point.y) == pytest.approx((21.0, 59.0))
    assert result.quality is ContactPointQuality.KEYPOINT


def test_rider_contact_point_uses_wheel_contact_midpoint() -> None:
    result = extract_contact_point(
        semantic_class=SemanticClass.EBIKE_RIDER,
        bbox_xyxy=(10.0, 20.0, 70.0, 80.0),
        keypoints={
            "front_wheel": KeypointObservation(x=62.0, y=78.0, confidence=0.9),
            "rear_wheel": KeypointObservation(x=18.0, y=78.0, confidence=0.9),
        },
        minimum_confidence=0.35,
    )

    assert (result.point.x, result.point.y) == pytest.approx((40.0, 78.0))
    assert result.quality is ContactPointQuality.KEYPOINT


def test_contact_point_falls_back_to_bbox_bottom_midpoint() -> None:
    result = extract_contact_point(
        semantic_class=SemanticClass.PEDESTRIAN_UMBRELLA,
        bbox_xyxy=(10.0, 20.0, 30.0, 60.0),
        keypoints={},
        minimum_confidence=0.35,
    )

    assert (result.point.x, result.point.y) == pytest.approx((20.0, 60.0))
    assert result.quality is ContactPointQuality.FALLBACK


def test_full_camera_calibration_intersects_pixel_ray_with_ground_plane() -> None:
    calibration = FullCameraCalibration(
        camera_matrix=((100.0, 0.0, 50.0), (0.0, 100.0, 50.0), (0.0, 0.0, 1.0)),
        distortion=(0.0, 0.0, 0.0, 0.0, 0.0),
        rotation_world_to_camera=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        translation_world_to_camera=(0.0, 0.0, 10.0),
    )

    world = calibration.pixel_to_ground((60.0, 70.0))

    assert world == pytest.approx((1.0, 2.0), abs=1e-9)


def test_homography_solver_requires_eight_fit_points() -> None:
    points = tuple(
        CalibrationPoint(pixel=(float(index), float(index)), world=(float(index), float(index)))
        for index in range(7)
    )

    with pytest.raises(ValueError, match="at least eight fit points"):
        solve_homography(points, points[:4])


def test_homography_solver_recovers_mapping_and_reports_checkpoint_rmse() -> None:
    matrix = np.array(
        [[0.02, 0.001, -1.0], [0.0005, 0.018, 2.0], [0.00001, 0.00002, 1.0]],
        dtype=float,
    )

    def mapped(pixel: tuple[float, float]) -> tuple[float, float]:
        homogeneous = matrix @ np.array([pixel[0], pixel[1], 1.0])
        return (float(homogeneous[0] / homogeneous[2]), float(homogeneous[1] / homogeneous[2]))

    pixels = (
        (20.0, 20.0),
        (100.0, 20.0),
        (180.0, 20.0),
        (20.0, 100.0),
        (100.0, 100.0),
        (180.0, 100.0),
        (20.0, 180.0),
        (100.0, 180.0),
        (180.0, 180.0),
        (60.0, 60.0),
        (140.0, 60.0),
        (140.0, 140.0),
    )
    fit = tuple(CalibrationPoint(pixel=pixel, world=mapped(pixel)) for pixel in pixels[:8])
    checkpoints = tuple(
        CalibrationPoint(pixel=pixel, world=mapped(pixel)) for pixel in pixels[8:]
    )

    calibration = solve_homography(fit, checkpoints)

    assert calibration.transform((75.0, 125.0)) == pytest.approx(mapped((75.0, 125.0)), abs=1e-7)
    assert calibration.report.world_checkpoint_rmse_m < 1e-7
    assert calibration.report.accepted is True


def test_full_camera_solution_uses_intrinsics_and_independent_ground_checkpoints() -> None:
    camera_matrix = ((800.0, 0.0, 320.0), (0.0, 800.0, 240.0), (0.0, 0.0, 1.0))

    def point(x: float, y: float) -> CalibrationPoint:
        return CalibrationPoint(pixel=(80 * x + 320, -80 * y + 240), world=(x, y))

    fit = tuple(
        point(x, y)
        for x, y in (
            (-2, -2),
            (-2, 0),
            (-2, 2),
            (0, -2),
            (0, 2),
            (2, -2),
            (2, 0),
            (2, 2),
        )
    )
    checkpoints = tuple(
        point(x, y) for x, y in ((-1, -1), (-1, 1), (1, -1), (1, 1))
    )

    calibration, report = solve_full_camera_from_ground_points(
        camera_matrix=camera_matrix,
        distortion=(),
        fit_points=fit,
        checkpoints=checkpoints,
        scene_id="scene-1",
        scene_version=1,
    )

    assert calibration.pixel_to_ground(point(0.75, -0.5).pixel) == pytest.approx(
        (0.75, -0.5)
    )
    assert report.mode is CalibrationMode.FULL_CAMERA
    assert report.accepted is True
    assert report.world_checkpoint_rmse_m < 1e-8


class FakeAruco:
    @staticmethod
    def getPredefinedDictionary(dictionary_id):
        return dictionary_id

    @staticmethod
    def CharucoBoard(size, square_length, marker_length, dictionary):
        return (size, square_length, marker_length, dictionary)

    class CharucoDetector:
        def __init__(self, board):
            self.board = board

        def detectBoard(self, image):
            corners = np.arange(12, dtype=float).reshape(6, 1, 2)
            ids = np.arange(6, dtype=np.int32).reshape(6, 1)
            return corners, ids, (), ()

    @staticmethod
    def calibrateCameraCharucoExtended(**kwargs):
        return (
            0.25,
            np.array([[800.0, 0, 320], [0, 800.0, 240], [0, 0, 1.0]]),
            np.zeros((5, 1)),
            (),
            (),
            None,
            None,
            None,
        )


class FakeCV2:
    COLOR_BGR2GRAY = 1
    aruco = FakeAruco()

    @staticmethod
    def imread(path):
        return np.zeros((480, 640, 3), dtype=np.uint8)

    @staticmethod
    def cvtColor(image, mode):
        return image[:, :, 0]


def test_charuco_calibration_collects_multiple_valid_views(tmp_path) -> None:
    images = tuple(tmp_path / f"view-{index}.png" for index in range(5))

    intrinsics = calibrate_charuco_images(
        images,
        CharucoBoardSpec(
            squares_x=5,
            squares_y=7,
            square_length_m=0.04,
            marker_length_m=0.02,
            dictionary_id=0,
        ),
        cv2_module=FakeCV2(),
    )

    assert intrinsics.valid_view_count == 5
    assert intrinsics.image_size == (640, 480)
    assert intrinsics.rms_reprojection_error_px == pytest.approx(0.25)
