"""Framework-independent geometry for finite virtual crossing lines."""

from dataclasses import dataclass
from enum import Enum

from src.domain.models import Point


EPSILON = 1e-9


class PointSide(Enum):
    """The side of a point relative to a line directed from start to end."""

    SIDE_A = "SIDE_A"
    SIDE_B = "SIDE_B"
    ON_LINE = "ON_LINE"


class CrossingDirection(Enum):
    """Geometric direction; it has no business meaning such as entry/exit."""

    SIDE_A_TO_B = "SIDE_A_TO_B"
    SIDE_B_TO_A = "SIDE_B_TO_A"


@dataclass(frozen=True, slots=True)
class CrossingLine:
    """A finite segment used as a virtual crossing line.

    SIDE_A is the positive orientation side of the directed segment from
    ``start`` to ``end``. SIDE_B is the negative side. The segment endpoints
    are included when checking whether a path crosses the line.
    """

    start: Point
    end: Point

    def __post_init__(self) -> None:
        if self.start == self.end:
            raise ValueError("CrossingLine requires two distinct points")

    def side(self, point: Point) -> PointSide:
        """Return the oriented side of ``point`` relative to this segment."""
        orientation = _cross(self.start, self.end, point)
        if abs(orientation) <= EPSILON:
            return PointSide.ON_LINE
        return PointSide.SIDE_A if orientation > 0 else PointSide.SIDE_B


def _cross(origin: Point, first: Point, second: Point) -> float:
    """Return the 2D cross product of (first-origin) and (second-origin)."""
    first_x = first.x - origin.x
    first_y = first.y - origin.y
    second_x = second.x - origin.x
    second_y = second.y - origin.y
    return first_x * second_y - first_y * second_x


def _cross_vectors(first: Point, second: Point) -> float:
    return first.x * second.y - first.y * second.x


def _subtract(first: Point, second: Point) -> Point:
    return Point(first.x - second.x, first.y - second.y)


def segments_intersect(
    first_start: Point,
    first_end: Point,
    second_start: Point,
    second_end: Point,
) -> bool:
    """Return whether two finite segments intersect, including endpoints."""
    first_vector = _subtract(first_end, first_start)
    second_vector = _subtract(second_end, second_start)
    denominator = _cross_vectors(first_vector, second_vector)

    if abs(denominator) <= EPSILON:
        return False

    between_starts = _subtract(second_start, first_start)
    first_parameter = _cross_vectors(between_starts, second_vector) / denominator
    second_parameter = _cross_vectors(between_starts, first_vector) / denominator

    return (
        -EPSILON <= first_parameter <= 1 + EPSILON
        and -EPSILON <= second_parameter <= 1 + EPSILON
    )
