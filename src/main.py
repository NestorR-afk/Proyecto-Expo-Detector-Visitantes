"""Command-line entrypoint for the current PC YOLO prototype."""

import logging

from src.application.tracking_loop import TrackingLoop
from src.config.settings import Settings
from src.domain.counting import CrossingLine, TrajectoryEventDetector
from src.domain.models import Point
from src.infrastructure.camera.opencv_camera import OpenCVCamera
from src.infrastructure.persistence.sqlite_visit_event_repository import (
    SQLiteVisitEventRepository,
)
from src.infrastructure.tracking.ultralytics_tracker import UltralyticsTracker
from src.presentation.noop import NoOpPresenter
from src.presentation.opencv.window import OpenCVWindow


LOGGER = logging.getLogger(__name__)


def build_crossing_line(settings: Settings) -> CrossingLine:
    return CrossingLine(
        start=Point(settings.counting_line_start_x, settings.counting_line_start_y),
        end=Point(settings.counting_line_end_x, settings.counting_line_end_y),
    )


def build_application(settings: Settings) -> TrackingLoop:
    """Build the concrete adapters used by the current prototype."""
    tracker = UltralyticsTracker(
        model_path=settings.model_path,
        imgsz=settings.imgsz,
        confidence=settings.confidence,
        iou=settings.iou,
        person_class_id=settings.person_class_id,
        tracker=settings.tracker,
    )
    camera = OpenCVCamera(
        camera_index=settings.camera_index,
        width=settings.camera_width,
        height=settings.camera_height,
        max_consecutive_read_failures=settings.camera_max_consecutive_read_failures,
        reopen_attempts=settings.camera_reopen_attempts,
        reopen_delay_seconds=settings.camera_reopen_delay_seconds,
    )
    presenter = (
        OpenCVWindow(settings.window_title)
        if settings.show_preview
        else NoOpPresenter()
    )
    crossing_line = build_crossing_line(settings)
    event_detector = TrajectoryEventDetector(crossing_line)
    repository = SQLiteVisitEventRepository(settings.database_path)
    try:
        initial_total = repository.count()
    except Exception:
        repository.close()
        raise
    return TrackingLoop(
        camera,
        tracker,
        event_detector,
        crossing_line,
        presenter,
        repository,
        initial_total,
    )


def main() -> None:
    """Run the current prototype until the camera ends or Q is pressed."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        build_application(Settings()).run()
    except KeyboardInterrupt:
        LOGGER.info("Shutdown requested by user")


if __name__ == "__main__":
    main()
