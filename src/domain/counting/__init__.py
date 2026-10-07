"""Pure geometry used by future visitor-counting rules."""

from src.domain.counting.crossing import CrossingResult, detect_crossing
from src.domain.counting.event_detector import TrajectoryEventDetector
from src.domain.counting.geometry import (
    CrossingDirection,
    CrossingLine,
    PointSide,
)
from src.domain.counting.models import VisitEvent

__all__ = [
    "CrossingDirection",
    "CrossingLine",
    "CrossingResult",
    "PointSide",
    "TrajectoryEventDetector",
    "VisitEvent",
    "detect_crossing",
]
