from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from harness.models import Task, TaskStatus, jsonable


class MemoryEngine:
    """Historial persistente en SQLite; no implementa memoria semántica."""

    def __init__(self, database: str | Path):
        self.database = Path(database).resolve()
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                    status TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL, kind TEXT NOT NULL,
                    details TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS events_task_idx ON events(task_id, sequence);
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL,
                    plan TEXT, result TEXT, error TEXT,
                    started_at TEXT NOT NULL, finished_at TEXT
                );
                CREATE INDEX IF NOT EXISTS executions_task_idx ON executions(task_id);
                CREATE TABLE IF NOT EXISTS id_sequences (
                    year INTEGER PRIMARY KEY, next_number INTEGER NOT NULL
                );
                """
            )

    def next_task_identifier(self, year: int) -> str:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT next_number FROM id_sequences WHERE year=?", (year,)).fetchone()
            if row is None:
                number = 1
                db.execute("INSERT INTO id_sequences(year, next_number) VALUES (?, ?)", (year, 2))
            else:
                number = row["next_number"]
                db.execute("UPDATE id_sequences SET next_number=? WHERE year=?", (number + 1, year))
        return f"ENC-{year}-{number:04d}"

    def create_task(self, task: Task) -> None:
        payload = json.dumps(jsonable(task), ensure_ascii=False)
        with self._connect() as db:
            db.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?)",
                (task.id, payload, task.status.value, task.created_at, task.updated_at),
            )
            self._event(db, task.id, "TASK_CREATED", {"title": task.title, "status": task.status.value}, task.created_at)

    def update_task(self, task: Task, kind: str, details: dict[str, Any] | None = None) -> None:
        payload = json.dumps(jsonable(task), ensure_ascii=False)
        with self._connect() as db:
            cursor = db.execute(
                "UPDATE tasks SET payload=?, status=?, updated_at=? WHERE id=?",
                (payload, task.status.value, task.updated_at, task.id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Tarea desconocida: {task.id}")
            self._event(db, task.id, kind, details or {}, task.updated_at)

    def get_task(self, task_id: str) -> Task:
        with self._connect() as db:
            row = db.execute("SELECT payload FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(f"Tarea desconocida: {task_id}")
        data = json.loads(row["payload"])
        data["status"] = TaskStatus(data["status"])
        return Task(**data)

    def list_tasks(self) -> list[Task]:
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM tasks ORDER BY created_at").fetchall()
        tasks = []
        for row in rows:
            data = json.loads(row["payload"])
            data["status"] = TaskStatus(data["status"])
            tasks.append(Task(**data))
        return tasks

    def record_event(self, task_id: str, kind: str, details: dict[str, Any]) -> None:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            self._event(db, task_id, kind, details, now)

    @staticmethod
    def _event(db: sqlite3.Connection, task_id: str, kind: str, details: dict[str, Any], created_at: str) -> None:
        db.execute(
            "INSERT INTO events(task_id, kind, details, created_at) VALUES (?, ?, ?, ?)",
            (task_id, kind, json.dumps(details, ensure_ascii=False), created_at),
        )

    def history(self, task_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT sequence, kind, details, created_at FROM events WHERE task_id=? ORDER BY sequence",
                (task_id,),
            ).fetchall()
        return [
            {"sequence": row["sequence"], "kind": row["kind"], "details": json.loads(row["details"]), "created_at": row["created_at"]}
            for row in rows
        ]

    def start_execution(self, execution_id: str, task_id: str, started_at: str) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO executions(id, task_id, started_at) VALUES (?, ?, ?)",
                (execution_id, task_id, started_at),
            )
        self.record_event(task_id, "EXECUTION_STARTED", {"execution_id": execution_id})

    def finish_execution(self, execution_id: str, plan: Any, result: Any = None, error: str | None = None, finished_at: str = "") -> None:
        with self._connect() as db:
            cursor = db.execute(
                "UPDATE executions SET plan=?, result=?, error=?, finished_at=? WHERE id=?",
                (
                    json.dumps(jsonable(plan), ensure_ascii=False) if plan is not None else None,
                    json.dumps(jsonable(result), ensure_ascii=False) if result is not None else None,
                    error,
                    finished_at,
                    execution_id,
                ),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Ejecución desconocida: {execution_id}")

    def executions(self, task_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT id, plan, result, error, started_at, finished_at FROM executions WHERE task_id=? ORDER BY started_at",
                (task_id,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "plan": json.loads(row["plan"]) if row["plan"] else None,
                "result": json.loads(row["result"]) if row["result"] else None,
                "error": row["error"],
                "started_at": row["started_at"],
                "finished_at": row["finished_at"],
            }
            for row in rows
        ]
