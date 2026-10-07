"""Command-line entrypoint for the current PC YOLO prototype."""

from src.application.tracking_loop import TrackingLoop
from src.config.settings import Settings
from src.domain.counting import CrossingLine, TrajectoryEventDetector
from src.domain.models import Point
from src.infrastructure.camera.opencv_camera import OpenCVCamera
from src.infrastructure.tracking.ultralytics_tracker import UltralyticsTracker
from src.presentation.noop import NoOpPresenter
from src.presentation.opencv.window import OpenCVWindow


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
    )
    presenter = (
        OpenCVWindow(settings.window_title)
        if settings.show_preview
        else NoOpPresenter()
    )
    crossing_line = build_crossing_line(settings)
    event_detector = TrajectoryEventDetector(crossing_line)
    return TrackingLoop(camera, tracker, event_detector, crossing_line, presenter)


def main() -> None:
    """Run the current prototype until the camera ends or Q is pressed."""
    build_application(Settings()).run()


if __name__ == "__main__":
    main()
