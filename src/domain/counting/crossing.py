"""Pure detection of a trajectory crossing a finite virtual line."""

from dataclasses import dataclass

from src.domain.counting.geometry import (
    CrossingDirection,
    CrossingLine,
    PointSide,
    segments_intersect,
)
from src.domain.models import Point


@dataclass(frozen=True, slots=True)
class CrossingResult:
    """Geometric result for one pair of consecutive centroid positions."""

    crossed: bool
    previous_side: PointSide
    current_side: PointSide
    direction: CrossingDirection | None


def detect_crossing(
    previous_centroid: Point,
    current_centroid: Point,
    crossing_line: CrossingLine,
) -> CrossingResult:
    """Determine whether one movement segment crosses ``crossing_line``.

    A crossing requires non-neutral, opposite sides and an intersection with
    the finite line segment. If either point is ON_LINE, the result exposes
    that neutral side but does not infer a crossing. COUNT-002 can preserve
    the last non-neutral side across frames when it needs A -> ON_LINE -> B
    to become one logical crossing.
    """
    previous_side = crossing_line.side(previous_centroid)
    current_side = crossing_line.side(current_centroid)
    direction = _direction(previous_side, current_side)

    crossed = (
        direction is not None
        and segments_intersect(
            previous_centroid,
            current_centroid,
            crossing_line.start,
            crossing_line.end,
        )
    )

    return CrossingResult(
        crossed=crossed,
        previous_side=previous_side,
        current_side=current_side,
        direction=direction if crossed else None,
    )


def _direction(
    previous_side: PointSide,
    current_side: PointSide,
) -> CrossingDirection | None:
    if previous_side is PointSide.SIDE_A and current_side is PointSide.SIDE_B:
        return CrossingDirection.SIDE_A_TO_B
    if previous_side is PointSide.SIDE_B and current_side is PointSide.SIDE_A:
        return CrossingDirection.SIDE_B_TO_A
    return None
