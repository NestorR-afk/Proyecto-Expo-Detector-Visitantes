"""Presentation adapter for runs without a preview window."""

from typing import Any

from src.application.ports import PresentationState


class NoOpPresenter:
    """Discard frames while keeping the application loop running."""

    def show(self, frame: Any, state: PresentationState) -> bool:
        return False

    def close(self) -> None:
        return None
