"""Minimal configuration for the current prototype."""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    """Values needed to run the current camera and YOLO prototype."""

    camera_index: int = 0
    model_path: Path = PROJECT_ROOT / "models" / "yolo11n.pt"
    camera_width: int | None = None
    camera_height: int | None = None
    imgsz: int = 320
    confidence: float = 0.25
    iou: float = 0.7
    person_class_id: int = 0
    tracker: str = "bytetrack.yaml"
    show_preview: bool = True
    window_title: str = "Expo Visitor Counter - YOLO Prototype"
