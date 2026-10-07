"""OpenCV window used by the current tracking prototype."""

from collections.abc import Sequence
from typing import Any

import cv2

from src.domain.models import TrackedPerson


class OpenCVWindow:
    """Draw tracked people and handle the keyboard shutdown command."""

    def __init__(self, title: str) -> None:
        self._title = title

    def show(self, frame: Any, people: Sequence[TrackedPerson]) -> bool:
        for person in people:
            box = person.bounding_box
            top_left = (int(box.x1), int(box.y1))
            bottom_right = (int(box.x2), int(box.y2))
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"ID {person.tracking_id}",
                (top_left[0], top_left[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

        cv2.imshow(self._title, frame)
        return cv2.waitKey(1) & 0xFF == ord("q")

    def close(self) -> None:
        cv2.destroyAllWindows()
