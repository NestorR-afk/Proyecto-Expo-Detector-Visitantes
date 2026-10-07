"""OpenCV implementation of the frame source port."""

from collections.abc import Callable
import logging
from time import sleep
from typing import Any


LOGGER = logging.getLogger(__name__)


class CameraError(RuntimeError):
    """Base error for camera acquisition failures."""


class CameraOpenError(CameraError):
    """The camera could not be opened initially."""


class CameraRecoveryError(CameraError):
    """The camera could not be reopened after read failures."""


class OpenCVCamera:
    """Read frames from a local camera through OpenCV."""

    def __init__(
        self,
        camera_index: int,
        width: int | None = None,
        height: int | None = None,
        max_consecutive_read_failures: int = 3,
        reopen_attempts: int = 3,
        reopen_delay_seconds: float = 1.0,
        capture_factory: Callable[[int], Any] | None = None,
        sleep_function: Callable[[float], None] = sleep,
    ) -> None:
        if max_consecutive_read_failures <= 0:
            raise ValueError("max_consecutive_read_failures must be positive")
        if reopen_attempts <= 0:
            raise ValueError("reopen_attempts must be positive")
        if reopen_delay_seconds < 0:
            raise ValueError("reopen_delay_seconds cannot be negative")

        self._camera_index = camera_index
        self._width = width
        self._height = height
        self._max_consecutive_read_failures = max_consecutive_read_failures
        self._reopen_attempts = reopen_attempts
        self._reopen_delay_seconds = reopen_delay_seconds
        self._capture_factory = capture_factory or _create_capture
        self._sleep = sleep_function
        self._recovery_pending = False
        self._capture = self._capture_factory(camera_index)
        if not self._capture.isOpened():
            self._capture.release()
            raise CameraOpenError(f"Unable to open camera index {camera_index}")

        self._configure_capture(self._capture)

    def read(self) -> tuple[bool, Any]:
        consecutive_failures = 0
        reopened_in_read = False

        while True:
            frame_ok, frame = self._capture.read()
            if frame_ok:
                return True, frame

            consecutive_failures += 1
            LOGGER.warning(
                "Camera read failed (%s/%s)",
                consecutive_failures,
                self._max_consecutive_read_failures,
            )
            if consecutive_failures < self._max_consecutive_read_failures:
                self._sleep(self._reopen_delay_seconds)
                continue

            if reopened_in_read:
                raise CameraRecoveryError(
                    "Camera still unavailable after reopening"
                )

            self._reopen()
            reopened_in_read = True
            consecutive_failures = 0

    def release(self) -> None:
        self._capture.release()

    def consume_recovery(self) -> bool:
        """Return whether the camera was reopened since the last successful read."""
        recovered = self._recovery_pending
        self._recovery_pending = False
        return recovered

    def _reopen(self) -> None:
        LOGGER.warning("Reopening camera index %s", self._camera_index)
        self._capture.release()

        for attempt in range(1, self._reopen_attempts + 1):
            if attempt > 1:
                self._sleep(self._reopen_delay_seconds)

            try:
                capture = self._capture_factory(self._camera_index)
            except Exception as error:
                LOGGER.warning("Camera reopen attempt %s failed: %s", attempt, error)
                continue

            if capture.isOpened():
                self._capture = capture
                self._configure_capture(capture)
                self._recovery_pending = True
                LOGGER.info("Camera reopened on attempt %s", attempt)
                return

            capture.release()
            LOGGER.warning("Camera reopen attempt %s returned a closed device", attempt)

        raise CameraRecoveryError(
            f"Unable to reopen camera index {self._camera_index}"
        )

    def _configure_capture(self, capture: Any) -> None:
        if self._width is not None:
            capture.set(_property("CAP_PROP_FRAME_WIDTH"), self._width)
        if self._height is not None:
            capture.set(_property("CAP_PROP_FRAME_HEIGHT"), self._height)


def _create_capture(camera_index: int) -> Any:
    import cv2

    return cv2.VideoCapture(camera_index)


def _property(name: str) -> int:
    import cv2

    return int(getattr(cv2, name))
