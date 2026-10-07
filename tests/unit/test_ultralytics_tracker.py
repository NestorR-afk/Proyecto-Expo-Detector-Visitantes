import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeBoxes:
    def __init__(self, boxes, confidences, tracking_ids):
        self.xyxy = [
            types.SimpleNamespace(tolist=lambda values=box: values)
            for box in boxes
        ]
        self.conf = confidences
        self.id = tracking_ids


class FakeResult:
    def __init__(self, boxes, confidences, tracking_ids):
        self.boxes = FakeBoxes(boxes, confidences, tracking_ids)


class FakeYOLO:
    instances = []
    results = []

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.calls = []
        self.instances.append(self)

    def track(self, frame, **kwargs):
        self.calls.append((frame, kwargs))
        return self.results


def load_tracker_module(yolo_class):
    fake_ultralytics = types.SimpleNamespace(YOLO=yolo_class)
    with patch.dict(sys.modules, {"ultralytics": fake_ultralytics}):
        sys.modules.pop("src.infrastructure.tracking.ultralytics_tracker", None)
        return importlib.import_module(
            "src.infrastructure.tracking.ultralytics_tracker"
        )


class TrackerAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        FakeYOLO.instances = []
        FakeYOLO.results = []

    def build_tracker(self, yolo_class=FakeYOLO):
        module = load_tracker_module(yolo_class)
        return module.UltralyticsTracker(
            model_path=Path("models/yolo11n.pt"),
            imgsz=320,
            confidence=0.4,
            iou=0.6,
            person_class_id=0,
            tracker="bytetrack.yaml",
        )

    def test_empty_result_returns_no_people(self) -> None:
        people = self.build_tracker().track("frame")

        self.assertEqual(people, [])

    def test_one_detection_becomes_one_tracked_person(self) -> None:
        FakeYOLO.results = [
            FakeResult([[10, 20, 30, 60]], [0.9], [7])
        ]

        people = self.build_tracker().track("frame")

        self.assertEqual(len(people), 1)
        self.assertEqual(people[0].tracking_id, 7)
        self.assertEqual(people[0].bounding_box.x1, 10)
        self.assertEqual(people[0].centroid.x, 20)

    def test_multiple_detections_become_multiple_tracked_people(self) -> None:
        FakeYOLO.results = [
            FakeResult(
                [[10, 20, 30, 60], [100, 120, 140, 200]],
                [0.9, 0.8],
                [7, 8],
            )
        ]

        people = self.build_tracker().track("frame")

        self.assertEqual([person.tracking_id for person in people], [7, 8])

    def test_detection_without_id_is_ignored(self) -> None:
        FakeYOLO.results = [
            FakeResult([[10, 20, 30, 60]], [0.9], None)
        ]

        people = self.build_tracker().track("frame")

        self.assertEqual(people, [])

    def test_mixed_tracked_and_untracked_boxes_only_returns_tracked_boxes(self) -> None:
        class MixedBoxes(FakeBoxes):
            def __init__(self):
                super().__init__(
                    [[10, 20, 30, 60], [100, 120, 140, 200]],
                    [0.9, 0.8],
                    [7, None],
                )

        class MixedResult:
            boxes = MixedBoxes()

        FakeYOLO.results = [MixedResult()]

        people = self.build_tracker().track("frame")

        self.assertEqual([person.tracking_id for person in people], [7])

    def test_propagates_tracking_parameters(self) -> None:
        tracker = self.build_tracker()

        tracker.track("frame")
        call_kwargs = FakeYOLO.instances[-1].calls[0][1]

        self.assertEqual(call_kwargs["imgsz"], 320)
        self.assertEqual(call_kwargs["conf"], 0.4)
        self.assertEqual(call_kwargs["iou"], 0.6)
        self.assertEqual(call_kwargs["tracker"], "bytetrack.yaml")
        self.assertTrue(call_kwargs["persist"])
        self.assertEqual(call_kwargs["classes"], [0])

    def test_reset_recreates_model_session(self) -> None:
        tracker = self.build_tracker()

        tracker.reset()

        self.assertEqual(len(FakeYOLO.instances), 2)


if __name__ == "__main__":
    unittest.main()
