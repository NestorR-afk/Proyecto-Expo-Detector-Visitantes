import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeBoxes:
    def __init__(self, tracking_ids):
        self.xyxy = [types.SimpleNamespace(tolist=lambda: [10, 20, 30, 40])]
        self.conf = [0.9]
        self.id = tracking_ids


class FakeResult:
    def __init__(self, tracking_ids):
        self.boxes = FakeBoxes(tracking_ids)


class FakeYOLO:
    instances = []

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.calls = []
        self.instances.append(self)

    def track(self, frame, **kwargs):
        self.calls.append((frame, kwargs))
        return [FakeResult([7])]


class TrackerAdapterTests(unittest.TestCase):
    def test_propagates_tracking_parameters_and_ignores_missing_ids(self) -> None:
        fake_ultralytics = types.SimpleNamespace(YOLO=FakeYOLO)
        with patch.dict(sys.modules, {"ultralytics": fake_ultralytics}):
            module = importlib.import_module(
                "src.infrastructure.tracking.ultralytics_tracker"
            )
            tracker = module.UltralyticsTracker(
                model_path=Path("models/yolo11n.pt"),
                imgsz=320,
                confidence=0.4,
                iou=0.6,
                person_class_id=0,
                tracker="bytetrack.yaml",
            )

            people = tracker.track("frame")
            call_kwargs = FakeYOLO.instances[-1].calls[0][1]

        self.assertEqual(len(people), 1)
        self.assertEqual(people[0].tracking_id, 7)
        self.assertEqual(call_kwargs["imgsz"], 320)
        self.assertEqual(call_kwargs["conf"], 0.4)
        self.assertEqual(call_kwargs["iou"], 0.6)
        self.assertEqual(call_kwargs["tracker"], "bytetrack.yaml")
        self.assertTrue(call_kwargs["persist"])
        self.assertEqual(call_kwargs["classes"], [0])

    def test_returns_no_track_for_detection_without_id(self) -> None:
        class NoIDYOLO(FakeYOLO):
            def track(self, frame, **kwargs):
                self.calls.append((frame, kwargs))
                return [FakeResult(None)]

        fake_ultralytics = types.SimpleNamespace(YOLO=NoIDYOLO)
        with patch.dict(sys.modules, {"ultralytics": fake_ultralytics}):
            sys.modules.pop("src.infrastructure.tracking.ultralytics_tracker", None)
            module = importlib.import_module(
                "src.infrastructure.tracking.ultralytics_tracker"
            )
            tracker = module.UltralyticsTracker(
                model_path=Path("models/yolo11n.pt"),
                imgsz=320,
                confidence=0.25,
                iou=0.7,
                person_class_id=0,
                tracker="bytetrack.yaml",
            )

            people = tracker.track("frame")

        self.assertEqual(people, [])


if __name__ == "__main__":
    unittest.main()
