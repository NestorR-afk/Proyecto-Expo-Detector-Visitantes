import unittest

from src.application.tracking_loop import TrackingLoop


class FakeFrameSource:
    def __init__(self) -> None:
        self.frames = [(True, "frame-1"), (True, "frame-2"), (False, None)]
        self.released = False

    def read(self) -> tuple[bool, object]:
        return self.frames.pop(0)

    def release(self) -> None:
        self.released = True


class FakeTracker:
    def __init__(self) -> None:
        self.received: list[object] = []

    def track(self, frame: object) -> list[object]:
        self.received.append(frame)
        return []


class FakePresenter:
    def __init__(self) -> None:
        self.frames: list[object] = []
        self.closed = False

    def show(self, frame: object, people: list[object]) -> bool:
        self.frames.append(frame)
        return frame == "frame-2"

    def close(self) -> None:
        self.closed = True


class TrackingLoopTests(unittest.TestCase):
    def test_releases_adapters_when_presenter_requests_shutdown(self) -> None:
        source = FakeFrameSource()
        tracker = FakeTracker()
        presenter = FakePresenter()

        TrackingLoop(source, tracker, presenter).run()

        self.assertEqual(tracker.received, ["frame-1", "frame-2"])
        self.assertEqual(presenter.frames, ["frame-1", "frame-2"])
        self.assertTrue(source.released)
        self.assertTrue(presenter.closed)


if __name__ == "__main__":
    unittest.main()
