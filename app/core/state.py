from __future__ import annotations

import json
import sqlite3
from typing import Protocol

from app.core.types import ProposedAction, PENDING


class StateStore(Protocol):
    def enqueue(self, action: ProposedAction) -> None: ...
    def get(self, action_id: str) -> ProposedAction | None: ...
    def pending(self) -> list[ProposedAction]: ...
    def update_status(self, action_id: str, status: str) -> None: ...


class SqliteStateStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS actions (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    params TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def enqueue(self, action: ProposedAction) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO actions (id, action, params, origin, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (action.id, action.action, json.dumps(action.params), action.origin, action.status),
            )

    def _row_to_action(self, row: sqlite3.Row) -> ProposedAction:
        return ProposedAction(
            id=row["id"],
            action=row["action"],
            params=json.loads(row["params"]),
            origin=row["origin"],
            status=row["status"],
        )

    def get(self, action_id: str) -> ProposedAction | None:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM actions WHERE id = ?", (action_id,)).fetchone()
        return self._row_to_action(row) if row else None

    def pending(self) -> list[ProposedAction]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM actions WHERE status = ?", (PENDING,)).fetchall()
        return [self._row_to_action(r) for r in rows]

    def update_status(self, action_id: str, status: str) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE actions SET status = ? WHERE id = ?", (status, action_id))
