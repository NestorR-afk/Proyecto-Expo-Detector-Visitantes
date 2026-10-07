"""Pure geometry used by future visitor-counting rules."""

from src.domain.counting.crossing import CrossingResult, detect_crossing
from src.domain.counting.geometry import (
    CrossingDirection,
    CrossingLine,
    PointSide,
)

__all__ = [
    "CrossingDirection",
    "CrossingLine",
    "CrossingResult",
    "PointSide",
    "detect_crossing",
]
