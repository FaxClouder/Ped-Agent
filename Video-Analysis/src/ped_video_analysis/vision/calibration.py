from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import Field
from scipy.optimize import least_squares

from ped_video_analysis.vision.contracts import CalibrationMode, CalibrationReport, FrozenModel


@dataclass(frozen=True)
class CalibrationPoint:
    pixel: tuple[float, float]
    world: tuple[float, float]


class CharucoBoardSpec(FrozenModel):
    squares_x: int = Field(ge=2)
    squares_y: int = Field(ge=2)
    square_length_m: float = Field(gt=0)
    marker_length_m: float = Field(gt=0)
    dictionary_id: int = Field(ge=0)
    minimum_views: int = Field(default=5, ge=3)
    minimum_corners_per_view: int = Field(default=4, ge=4)


class CameraIntrinsics(FrozenModel):
    camera_matrix: tuple[tuple[float, float, float], ...]
    distortion: tuple[float, ...]
    image_size: tuple[int, int]
    rms_reprojection_error_px: float = Field(ge=0)
    valid_view_count: int = Field(ge=1)


@dataclass(frozen=True)
class HomographyCalibration:
    matrix: np.ndarray
    report: CalibrationReport

    def transform(self, pixel: tuple[float, float]) -> tuple[float, float]:
        transformed = _project(self.matrix, np.asarray([pixel], dtype=float))[0]
        return (float(transformed[0]), float(transformed[1]))

    def transform_many(self, pixels: np.ndarray) -> np.ndarray:
        return _project(self.matrix, np.asarray(pixels, dtype=float))


@dataclass(frozen=True)
class FullCameraCalibration:
    camera_matrix: tuple[tuple[float, float, float], ...]
    distortion: tuple[float, ...]
    rotation_world_to_camera: tuple[tuple[float, float, float], ...]
    translation_world_to_camera: tuple[float, float, float]

    def pixel_to_ground(self, pixel: tuple[float, float]) -> tuple[float, float]:
        camera_matrix = np.asarray(self.camera_matrix, dtype=float)
        rotation = np.asarray(self.rotation_world_to_camera, dtype=float)
        translation = np.asarray(self.translation_world_to_camera, dtype=float)
        normalized = self._normalized_camera_ray(pixel, camera_matrix)
        ray_world = rotation.T @ normalized
        camera_center_world = -rotation.T @ translation
        if abs(ray_world[2]) < 1e-12:
            raise ValueError("pixel ray is parallel to the ground plane")
        distance = -camera_center_world[2] / ray_world[2]
        if distance <= 0:
            raise ValueError("ground intersection lies behind the camera")
        point = camera_center_world + distance * ray_world
        return (float(point[0]), float(point[1]))

    def _normalized_camera_ray(
        self,
        pixel: tuple[float, float],
        camera_matrix: np.ndarray,
    ) -> np.ndarray:
        distortion = np.asarray(self.distortion, dtype=float)
        if distortion.size and not np.allclose(distortion, 0.0):
            try:
                import cv2
            except ImportError as exc:
                raise RuntimeError(
                    "opencv-contrib-python is required to undistort calibrated points"
                ) from exc
            normalized = cv2.undistortPoints(
                np.asarray(pixel, dtype=float).reshape(1, 1, 2),
                camera_matrix,
                distortion,
            ).reshape(2)
            return np.array([normalized[0], normalized[1], 1.0], dtype=float)
        homogeneous = np.linalg.inv(camera_matrix) @ np.array([pixel[0], pixel[1], 1.0])
        return homogeneous / homogeneous[2]


def calibrate_charuco_images(
    image_paths: tuple[Path, ...],
    board_spec: CharucoBoardSpec,
    *,
    cv2_module: Any | None = None,
) -> CameraIntrinsics:
    if len(image_paths) < board_spec.minimum_views:
        raise ValueError(f"ChArUco calibration requires at least {board_spec.minimum_views} images")
    if cv2_module is None:
        try:
            import cv2 as cv2_module
        except ImportError as exc:
            raise RuntimeError("opencv-contrib-python is required for ChArUco calibration") from exc
    aruco = cv2_module.aruco
    dictionary = aruco.getPredefinedDictionary(board_spec.dictionary_id)
    board = aruco.CharucoBoard(
        (board_spec.squares_x, board_spec.squares_y),
        board_spec.square_length_m,
        board_spec.marker_length_m,
        dictionary,
    )
    detector = aruco.CharucoDetector(board)
    all_corners = []
    all_ids = []
    image_size: tuple[int, int] | None = None
    for path in image_paths:
        image = cv2_module.imread(str(path))
        if image is None:
            continue
        gray = cv2_module.cvtColor(image, cv2_module.COLOR_BGR2GRAY)
        current_size = (int(gray.shape[1]), int(gray.shape[0]))
        if image_size is None:
            image_size = current_size
        elif image_size != current_size:
            raise ValueError("all ChArUco images must have the same resolution")
        corners, ids, _, _ = detector.detectBoard(gray)
        if ids is None or len(ids) < board_spec.minimum_corners_per_view:
            continue
        all_corners.append(corners)
        all_ids.append(ids)
    if len(all_corners) < board_spec.minimum_views or image_size is None:
        raise ValueError("not enough valid ChArUco views with detected corners")
    result = aruco.calibrateCameraCharucoExtended(
        charucoCorners=all_corners,
        charucoIds=all_ids,
        board=board,
        imageSize=image_size,
        cameraMatrix=None,
        distCoeffs=None,
    )
    rms, camera_matrix, distortion = result[:3]
    return CameraIntrinsics(
        camera_matrix=tuple(
            tuple(float(value) for value in row) for row in np.asarray(camera_matrix)
        ),
        distortion=tuple(float(value) for value in np.asarray(distortion).reshape(-1)),
        image_size=image_size,
        rms_reprojection_error_px=float(rms),
        valid_view_count=len(all_corners),
    )


def solve_full_camera_from_ground_points(
    *,
    camera_matrix: tuple[tuple[float, float, float], ...],
    distortion: tuple[float, ...],
    fit_points: tuple[CalibrationPoint, ...],
    checkpoints: tuple[CalibrationPoint, ...],
    scene_id: str,
    scene_version: int,
    cv2_module: Any | None = None,
) -> tuple[FullCameraCalibration, CalibrationReport]:
    matrix = np.asarray(camera_matrix, dtype=float)
    fit_pixels = _undistorted_pixels(
        tuple(point.pixel for point in fit_points),
        matrix,
        distortion,
        cv2_module,
    )
    checkpoint_pixels = _undistorted_pixels(
        tuple(point.pixel for point in checkpoints),
        matrix,
        distortion,
        cv2_module,
    )
    undistorted_fit = tuple(
        CalibrationPoint(pixel=tuple(pixel), world=point.world)
        for pixel, point in zip(fit_pixels, fit_points, strict=True)
    )
    undistorted_checkpoints = tuple(
        CalibrationPoint(pixel=tuple(pixel), world=point.world)
        for pixel, point in zip(checkpoint_pixels, checkpoints, strict=True)
    )
    homography = solve_homography(undistorted_fit, undistorted_checkpoints)
    world_to_image = np.linalg.inv(homography.matrix)
    normalized = np.linalg.inv(matrix) @ world_to_image
    scale = 2.0 / (np.linalg.norm(normalized[:, 0]) + np.linalg.norm(normalized[:, 1]))
    first = scale * normalized[:, 0]
    second = scale * normalized[:, 1]
    translation = scale * normalized[:, 2]
    if translation[2] < 0:
        first = -first
        second = -second
        translation = -translation
    third = np.cross(first, second)
    approximate_rotation = np.column_stack((first, second, third))
    u, _, vh = np.linalg.svd(approximate_rotation)
    rotation = u @ vh
    if np.linalg.det(rotation) < 0:
        u[:, -1] *= -1
        rotation = u @ vh
    calibration = FullCameraCalibration(
        camera_matrix=camera_matrix,
        distortion=distortion,
        rotation_world_to_camera=tuple(tuple(float(value) for value in row) for row in rotation),
        translation_world_to_camera=tuple(float(value) for value in translation),
    )
    errors = [
        np.asarray(calibration.pixel_to_ground(point.pixel)) - np.asarray(point.world)
        for point in checkpoints
    ]
    world_rmse = float(np.sqrt(np.mean([float(error @ error) for error in errors])))
    digest = sha256(matrix.tobytes() + rotation.tobytes() + translation.tobytes()).hexdigest()[:16]
    report = CalibrationReport(
        calibration_id=f"full-camera-{digest}",
        scene_id=scene_id,
        scene_version=scene_version,
        mode=CalibrationMode.FULL_CAMERA,
        image_reprojection_rmse_px=homography.report.image_reprojection_rmse_px,
        world_checkpoint_rmse_m=world_rmse,
        checkpoint_count=len(checkpoints),
        camera_matrix=camera_matrix,
        distortion=distortion,
        rotation_world_to_camera=calibration.rotation_world_to_camera,
        translation_world_to_camera=calibration.translation_world_to_camera,
    )
    return calibration, report


def _undistorted_pixels(
    pixels: tuple[tuple[float, float], ...],
    camera_matrix: np.ndarray,
    distortion: tuple[float, ...],
    cv2_module: Any | None,
) -> np.ndarray:
    array = np.asarray(pixels, dtype=float)
    if not distortion or np.allclose(distortion, 0):
        return array
    if cv2_module is None:
        try:
            import cv2 as cv2_module
        except ImportError as exc:
            raise RuntimeError(
                "opencv-contrib-python is required to undistort control points"
            ) from exc
    return cv2_module.undistortPoints(
        array.reshape(-1, 1, 2),
        camera_matrix,
        np.asarray(distortion),
        P=camera_matrix,
    ).reshape(-1, 2)


def solve_homography(
    fit_points: tuple[CalibrationPoint, ...],
    checkpoints: tuple[CalibrationPoint, ...],
    *,
    ransac_threshold_m: float = 0.10,
    max_trials: int = 250,
    random_seed: int = 0,
) -> HomographyCalibration:
    if len(fit_points) < 8:
        raise ValueError("homography calibration requires at least eight fit points")
    if len(checkpoints) < 4:
        raise ValueError("homography calibration requires at least four independent checkpoints")
    source = np.asarray([point.pixel for point in fit_points], dtype=float)
    destination = np.asarray([point.world for point in fit_points], dtype=float)
    matrix = _ransac_homography(
        source,
        destination,
        threshold=ransac_threshold_m,
        max_trials=max_trials,
        random_seed=random_seed,
    )
    matrix = _refine_homography(matrix, source, destination)

    checkpoint_pixels = np.asarray([point.pixel for point in checkpoints], dtype=float)
    checkpoint_world = np.asarray([point.world for point in checkpoints], dtype=float)
    world_errors = _project(matrix, checkpoint_pixels) - checkpoint_world
    world_rmse = float(np.sqrt(np.mean(np.sum(world_errors**2, axis=1))))

    inverse = np.linalg.inv(matrix)
    pixel_errors = _project(inverse, destination) - source
    pixel_rmse = float(np.sqrt(np.mean(np.sum(pixel_errors**2, axis=1))))
    normalized = matrix / matrix[2, 2]
    matrix_tuple = tuple(tuple(float(value) for value in row) for row in normalized)
    digest = sha256(normalized.tobytes()).hexdigest()[:16]
    report = CalibrationReport(
        calibration_id=f"homography-{digest}",
        scene_id="unbound",
        scene_version=1,
        mode=CalibrationMode.HOMOGRAPHY,
        image_reprojection_rmse_px=pixel_rmse,
        world_checkpoint_rmse_m=world_rmse,
        checkpoint_count=len(checkpoints),
        matrix=matrix_tuple,
    )
    return HomographyCalibration(matrix=normalized, report=report)


def _ransac_homography(
    source: np.ndarray,
    destination: np.ndarray,
    *,
    threshold: float,
    max_trials: int,
    random_seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(random_seed)
    best_inliers = np.ones(len(source), dtype=bool)
    best_count = 0
    best_error = float("inf")
    for _ in range(max_trials):
        indices = rng.choice(len(source), size=4, replace=False)
        try:
            candidate = _normalized_dlt(source[indices], destination[indices])
            errors = np.linalg.norm(_project(candidate, source) - destination, axis=1)
        except (np.linalg.LinAlgError, ValueError, FloatingPointError):
            continue
        inliers = errors <= threshold
        count = int(inliers.sum())
        error = float(errors[inliers].mean()) if count else float("inf")
        if count > best_count or (count == best_count and error < best_error):
            best_count = count
            best_error = error
            best_inliers = inliers
    if best_count < 4:
        best_inliers = np.ones(len(source), dtype=bool)
    return _normalized_dlt(source[best_inliers], destination[best_inliers])


def _normalized_dlt(source: np.ndarray, destination: np.ndarray) -> np.ndarray:
    if len(source) < 4:
        raise ValueError("homography requires at least four point pairs")
    source_normalized, source_transform = _normalize_points(source)
    destination_normalized, destination_transform = _normalize_points(destination)
    rows: list[list[float]] = []
    for (x, y), (u, v) in zip(source_normalized, destination_normalized, strict=True):
        rows.append([-x, -y, -1.0, 0.0, 0.0, 0.0, u * x, u * y, u])
        rows.append([0.0, 0.0, 0.0, -x, -y, -1.0, v * x, v * y, v])
    _, _, vh = np.linalg.svd(np.asarray(rows, dtype=float))
    normalized = vh[-1].reshape(3, 3)
    matrix = np.linalg.inv(destination_transform) @ normalized @ source_transform
    if abs(matrix[2, 2]) < 1e-12:
        raise np.linalg.LinAlgError("degenerate homography")
    return matrix / matrix[2, 2]


def _normalize_points(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centroid = points.mean(axis=0)
    centered = points - centroid
    mean_distance = float(np.linalg.norm(centered, axis=1).mean())
    if mean_distance < 1e-12:
        raise ValueError("calibration points must span an area")
    scale = np.sqrt(2.0) / mean_distance
    transform = np.array(
        [[scale, 0.0, -scale * centroid[0]], [0.0, scale, -scale * centroid[1]], [0, 0, 1]],
        dtype=float,
    )
    homogeneous = np.column_stack((points, np.ones(len(points))))
    normalized = (transform @ homogeneous.T).T
    return normalized[:, :2] / normalized[:, 2, None], transform


def _refine_homography(
    matrix: np.ndarray, source: np.ndarray, destination: np.ndarray
) -> np.ndarray:
    normalized = matrix / matrix[2, 2]
    initial = np.array(
        [
            normalized[0, 0],
            normalized[0, 1],
            normalized[0, 2],
            normalized[1, 0],
            normalized[1, 1],
            normalized[1, 2],
            normalized[2, 0],
            normalized[2, 1],
        ]
    )

    def residual(parameters: np.ndarray) -> np.ndarray:
        candidate = np.array(
            [
                [parameters[0], parameters[1], parameters[2]],
                [parameters[3], parameters[4], parameters[5]],
                [parameters[6], parameters[7], 1.0],
            ]
        )
        return (_project(candidate, source) - destination).ravel()

    result = least_squares(residual, initial, method="trf")
    parameters = result.x
    return np.array(
        [
            [parameters[0], parameters[1], parameters[2]],
            [parameters[3], parameters[4], parameters[5]],
            [parameters[6], parameters[7], 1.0],
        ],
        dtype=float,
    )


def _project(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
    homogeneous = np.column_stack((points, np.ones(len(points))))
    transformed = (matrix @ homogeneous.T).T
    denominators = transformed[:, 2]
    if np.any(np.abs(denominators) < 1e-12):
        raise ValueError("point projects to infinity")
    return transformed[:, :2] / denominators[:, None]


__all__ = [
    "CameraIntrinsics",
    "CalibrationPoint",
    "CharucoBoardSpec",
    "FullCameraCalibration",
    "HomographyCalibration",
    "calibrate_charuco_images",
    "solve_full_camera_from_ground_points",
    "solve_homography",
]
