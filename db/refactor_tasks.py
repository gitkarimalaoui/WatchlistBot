import sqlite3
from pathlib import Path
from typing import List, Dict, Any

from utils.db_access import PROJECT_DB_PATH


def _ensure_table(db_path: Path = PROJECT_DB_PATH) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS refactor_tasks (
                id TEXT PRIMARY KEY,
                description TEXT,
                module TEXT,
                priority TEXT,
                status TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def fetch_tasks(db_path: Path = PROJECT_DB_PATH) -> List[Dict[str, Any]]:
    _ensure_table(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, description, module, priority, status FROM refactor_tasks"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def upsert_tasks(tasks: List[Dict[str, Any]], db_path: Path = PROJECT_DB_PATH) -> None:
    _ensure_table(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        with conn:
            conn.execute("DELETE FROM refactor_tasks")
            conn.executemany(
                "INSERT INTO refactor_tasks (id, description, module, priority, status) VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        t.get("id"),
                        t.get("description"),
                        t.get("module"),
                        t.get("priority"),
                        t.get("status"),
                    )
                    for t in tasks
                ],
            )
    finally:
        conn.close()
