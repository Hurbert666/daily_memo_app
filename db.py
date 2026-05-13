from __future__ import annotations

import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
DB_PATH = DATA_DIR / "daily_memo.db"


@dataclass
class Task:
    id: int
    date: str
    title: str
    description: str
    priority: str
    is_done: bool
    due_time: str
    order_index: int
    created_at: str
    updated_at: str


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, path: Path = DB_PATH) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    priority TEXT NOT NULL DEFAULT '中',
                    is_done INTEGER NOT NULL DEFAULT 0,
                    due_time TEXT NOT NULL DEFAULT '',
                    order_index INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date)")
            columns = {
                row["name"]
                for row in self.conn.execute("PRAGMA table_info(tasks)").fetchall()
            }
            added_order_index = False
            if "order_index" not in columns:
                self.conn.execute(
                    "ALTER TABLE tasks ADD COLUMN order_index INTEGER NOT NULL DEFAULT 0"
                )
                added_order_index = True
            if added_order_index:
                self._backfill_order_indexes()

    def _backfill_order_indexes(self) -> None:
        dates = self.conn.execute(
            "SELECT DISTINCT date FROM tasks WHERE order_index = 0"
        ).fetchall()
        for date_row in dates:
            rows = self.conn.execute(
                "SELECT id FROM tasks WHERE date = ? ORDER BY id ASC",
                (date_row["date"],),
            ).fetchall()
            for index, row in enumerate(rows):
                self.conn.execute(
                    "UPDATE tasks SET order_index = ? WHERE id = ?",
                    (index, row["id"]),
                )

    def get_memo(self, date_text: str) -> str:
        row = self.conn.execute(
            "SELECT content FROM memos WHERE date = ?", (date_text,)
        ).fetchone()
        return row["content"] if row else ""

    def save_memo(self, date_text: str, content: str) -> None:
        current = now_text()
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO memos(date, content, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    content = excluded.content,
                    updated_at = excluded.updated_at
                """,
                (date_text, content, current, current),
            )

    def list_tasks(self, date_text: str, status: str = "全部") -> list[Task]:
        params: list[object] = [date_text]
        where = "WHERE date = ?"
        if status == "未完成":
            where += " AND is_done = 0"
        elif status == "已完成":
            where += " AND is_done = 1"

        rows = self.conn.execute(
            f"""
            SELECT id, date, title, description, priority, is_done, due_time,
                   order_index, created_at, updated_at
            FROM tasks
            {where}
            ORDER BY order_index ASC, id ASC
            """,
            params,
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def add_task(
        self,
        date_text: str,
        title: str,
        description: str = "",
        priority: str = "中",
        due_time: str = "",
    ) -> None:
        current = now_text()
        row = self.conn.execute(
            "SELECT COALESCE(MAX(order_index), -1) + 1 AS next_index FROM tasks WHERE date = ?",
            (date_text,),
        ).fetchone()
        order_index = int(row["next_index"] if row else 0)
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO tasks(date, title, description, priority, due_time, order_index,
                                  created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    date_text,
                    title.strip(),
                    description.strip(),
                    priority,
                    due_time.strip(),
                    order_index,
                    current,
                    current,
                ),
            )

    def update_task(
        self,
        task_id: int,
        title: str,
        description: str,
        priority: str,
        due_time: str,
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, due_time = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    title.strip(),
                    description.strip(),
                    priority,
                    due_time.strip(),
                    now_text(),
                    task_id,
                ),
            )

    def set_task_done(self, task_id: int, is_done: bool) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET is_done = ?, updated_at = ? WHERE id = ?",
                (1 if is_done else 0, now_text(), task_id),
            )

    def delete_task(self, task_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def reorder_tasks(self, date_text: str, task_ids: list[int]) -> None:
        with self.conn:
            for index, task_id in enumerate(task_ids):
                self.conn.execute(
                    """
                    UPDATE tasks
                    SET order_index = ?, updated_at = ?
                    WHERE id = ? AND date = ?
                    """,
                    (index, now_text(), task_id, date_text),
                )

    def get_task(self, task_id: int) -> Task | None:
        row = self.conn.execute(
            """
            SELECT id, date, title, description, priority, is_done, due_time,
                   order_index, created_at, updated_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
        return self._row_to_task(row) if row else None

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            date=row["date"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            is_done=bool(row["is_done"]),
            due_time=row["due_time"],
            order_index=row["order_index"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
