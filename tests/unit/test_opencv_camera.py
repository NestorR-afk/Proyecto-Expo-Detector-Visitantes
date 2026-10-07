import unittest

from src.infrastructure.camera.opencv_camera import (
    CameraOpenError,
    CameraRecoveryError,
    OpenCVCamera,
)


class FakeCapture:
    def __init__(self, opened: bool, reads: list[tuple[bool, object]]) -> None:
        self.opened = opened
        self.reads = reads
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def read(self) -> tuple[bool, object]:
        if self.reads:
            return self.reads.pop(0)
        return False, None

    def release(self) -> None:
        self.released = True

    def set(self, property_id: int, value: int) -> bool:
        return True


class CaptureFactory:
    def __init__(self, captures: list[FakeCapture]) -> None:
        self.captures = captures
        self.created: list[FakeCapture] = []

    def __call__(self, camera_index: int) -> FakeCapture:
        capture = self.captures.pop(0)
        self.created.append(capture)
        return capture


class CameraTests(unittest.TestCase):
    def test_valid_frame_is_returned(self) -> None:
        factory = CaptureFactory([FakeCapture(True, [(True, "frame")])])
        camera = OpenCVCamera(0, capture_factory=factory)

        self.assertEqual(camera.read(), (True, "frame"))
        self.assertFalse(camera.consume_recovery())
        camera.release()

    def test_initial_open_failure_is_explicit(self) -> None:
        factory = CaptureFactory([FakeCapture(False, [])])

        with self.assertRaises(CameraOpenError):
            OpenCVCamera(0, capture_factory=factory)

        self.assertTrue(factory.created[0].released)

    def test_temporary_read_failure_is_retried(self) -> None:
        sleeps: list[float] = []
        factory = CaptureFactory(
            [FakeCapture(True, [(False, None), (True, "frame")])]
        )
        camera = OpenCVCamera(
            0,
            max_consecutive_read_failures=3,
            sleep_function=sleeps.append,
            capture_factory=factory,
        )

        self.assertEqual(camera.read(), (True, "frame"))
        self.assertEqual(sleeps, [1.0])
        camera.release()

    def test_consecutive_failures_reopen_and_reset_recovery_flag(self) -> None:
        sleeps: list[float] = []
        factory = CaptureFactory(
            [
                FakeCapture(True, [(False, None), (False, None)]),
                FakeCapture(True, [(True, "recovered")]),
            ]
        )
        camera = OpenCVCamera(
            0,
            max_consecutive_read_failures=2,
            sleep_function=sleeps.append,
            capture_factory=factory,
        )

        self.assertEqual(camera.read(), (True, "recovered"))
        self.assertTrue(camera.consume_recovery())
        self.assertFalse(camera.consume_recovery())
        self.assertTrue(factory.created[0].released)
        camera.release()

    def test_reopen_failures_are_bounded(self) -> None:
        factory = CaptureFactory(
            [
                FakeCapture(True, [(False, None)]),
                FakeCapture(False, []),
                FakeCapture(False, []),
            ]
        )
        camera = OpenCVCamera(
            0,
            max_consecutive_read_failures=1,
            reopen_attempts=2,
            capture_factory=factory,
            sleep_function=lambda _: None,
        )

        with self.assertRaises(CameraRecoveryError):
            camera.read()

        self.assertEqual(len(factory.created), 3)


if __name__ == "__main__":
    unittest.main()
