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
        imgsz: int,
        confidence: float,
        iou: float,
        person_class_id: int,
        tracker: str,
    ) -> None:
        self._model_path = model_path
        self._model = self._create_model()
        self._imgsz = imgsz
        self._confidence = confidence
        self._iou = iou
        self._person_class_id = person_class_id
        self._tracker = tracker

    def reset(self) -> None:
        """Create a fresh Ultralytics session after camera recovery."""
        self._model = self._create_model()

    def _create_model(self) -> YOLO:
        return YOLO(str(self._model_path))

    def track(self, frame: Any) -> Sequence[TrackedPerson]:
        results = self._model.track(
            frame,
            imgsz=self._imgsz,
            conf=self._confidence,
            iou=self._iou,
            classes=[self._person_class_id],
            persist=True,
            tracker=self._tracker,
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
                if tracking_id is None:
                    continue

                x1, y1, x2, y2 = (float(value) for value in box.tolist())
                people.append(
                    TrackedPerson(
                        tracking_id=TrackingID(int(tracking_id)),
                        bounding_box=BoundingBox(x1, y1, x2, y2),
                        confidence=float(confidence),
                    )
                )

        return people
