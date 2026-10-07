"""Ultralytics YOLO adapter for the current combined detect-and-track API."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ultralytics import YOLO

from src.domain.models import BoundingBox, TrackedPerson, TrackingID


class UltralyticsTracker:
    """Use Ultralytics to detect and track people in sequential frames."""

    def __init__(
        self,
        model_path: Path,
        image_size: int,
        person_class_id: int,
        tracker_config: str,
    ) -> None:
        self._model = YOLO(str(model_path))
        self._image_size = image_size
        self._person_class_id = person_class_id
        self._tracker_config = tracker_config

    def track(self, frame: Any) -> Sequence[TrackedPerson]:
        results = self._model.track(
            frame,
            imgsz=self._image_size,
            classes=[self._person_class_id],
            persist=True,
            tracker=self._tracker_config,
            verbose=False,
        )

        people: list[TrackedPerson] = []
        for result in results:
            if result.boxes.id is None:
                continue

            for box, confidence, tracking_id in zip(
                result.boxes.xyxy,
                result.boxes.conf,
                result.boxes.id,
            ):
                x1, y1, x2, y2 = (float(value) for value in box.tolist())
                people.append(
                    TrackedPerson(
                        tracking_id=TrackingID(int(tracking_id)),
                        bounding_box=BoundingBox(x1, y1, x2, y2),
                        confidence=float(confidence),
                    )
                )

        return people
