"""Presentation adapter for runs without a preview window."""

from collections.abc import Sequence
from typing import Any

from src.domain.models import TrackedPerson


class NoOpPresenter:
    """Discard frames while keeping the application loop running."""

    def show(self, frame: Any, people: Sequence[TrackedPerson]) -> bool:
        return False

    def close(self) -> None:
        return None
