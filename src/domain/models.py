"""Small, framework-independent models for tracked people."""

from dataclasses import dataclass
from typing import NewType


TrackingID = NewType("TrackingID", int)


@dataclass(frozen=True, slots=True)
class Point:
    """A point in image coordinates."""

    x: float
    y: float


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """An axis-aligned bounding box in image coordinates."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        if self.x2 < self.x1 or self.y2 < self.y1:
            raise ValueError("BoundingBox coordinates must be ordered")

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def centroid(self) -> Point:
        return Point(
            x=(self.x1 + self.x2) / 2,
            y=(self.y1 + self.y2) / 2,
        )

    @property
    def center(self) -> Point:
        """Backward-compatible alias for ``centroid``."""
        return self.centroid


@dataclass(frozen=True, slots=True)
class TrackedPerson:
    """A person track produced by an infrastructure tracker."""

    tracking_id: TrackingID
    bounding_box: BoundingBox
    confidence: float

    @property
    def centroid(self) -> Point:
        return self.bounding_box.centroid
