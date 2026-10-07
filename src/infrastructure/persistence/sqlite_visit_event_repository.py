"""SQLite adapter for persisted visit events."""

from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from src.domain.counting import VisitEvent


class SQLiteVisitEventRepository:
    """Persist visit events in a small local SQLite database."""

    def __init__(self, database_path: Path | str) -> None:
        self._connection = self._open(database_path)
        self._initialize_schema()

    def save_many(self, events: Sequence[VisitEvent]) -> None:
        """Insert all events in one transaction."""
        if not events:
            return

        rows = [
            (
                int(event.tracking_id),
                event.direction.value,
                datetime.now(timezone.utc).isoformat(),
            )
            for event in events
        ]
        with self._connection:
            self._connection.executemany(
                """
                INSERT INTO visit_events (tracking_id, direction, created_at)
                VALUES (?, ?, ?)
                """,
                rows,
            )

    def count(self) -> int:
        """Return the number of events currently stored."""
        row = self._connection.execute(
            "SELECT COUNT(*) FROM visit_events"
        ).fetchone()
        return int(row[0])

    def close(self) -> None:
        """Close the database connection once."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @staticmethod
    def _open(database_path: Path | str) -> sqlite3.Connection:
        if database_path != ":memory:":
            path = Path(database_path)
            path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(database_path)

    def _initialize_schema(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS visit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracking_id INTEGER NOT NULL,
                    direction TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
