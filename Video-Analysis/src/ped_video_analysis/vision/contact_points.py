from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ped_video_analysis.vision.contracts import (
    ContactPointQuality,
    KeypointObservation,
    PixelPoint,
    SemanticClass,
)


class ContactPointEstimate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    point: PixelPoint
    quality: ContactPointQuality
    used_keypoints: tuple[str, ...] = ()


def extract_contact_point(
    *,
    semantic_class: SemanticClass,
    bbox_xyxy: tuple[float, float, float, float],
    keypoints: dict[str, KeypointObservation],
    minimum_confidence: float,
) -> ContactPointEstimate:
    required = _required_keypoints(semantic_class)
    available = tuple(
        name
        for name in required
        if name in keypoints and keypoints[name].confidence >= minimum_confidence
    )
    if len(available) == 2:
        first, second = (keypoints[name] for name in available)
        return ContactPointEstimate(
            point=PixelPoint(x=(first.x + second.x) / 2.0, y=(first.y + second.y) / 2.0),
            quality=ContactPointQuality.KEYPOINT,
            used_keypoints=available,
        )
    if len(available) == 1:
        point = keypoints[available[0]]
        return ContactPointEstimate(
            point=PixelPoint(x=point.x, y=point.y),
            quality=ContactPointQuality.ESTIMATED,
            used_keypoints=available,
        )
    x1, _, x2, y2 = bbox_xyxy
    return ContactPointEstimate(
        point=PixelPoint(x=(x1 + x2) / 2.0, y=y2),
        quality=ContactPointQuality.FALLBACK,
    )


def _required_keypoints(semantic_class: SemanticClass) -> tuple[str, str]:
    if semantic_class in {
        SemanticClass.PEDESTRIAN,
        SemanticClass.PEDESTRIAN_UMBRELLA,
    }:
        return ("left_foot", "right_foot")
    return ("front_wheel", "rear_wheel")


__all__ = ["ContactPointEstimate", "extract_contact_point"]
