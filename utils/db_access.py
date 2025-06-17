from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
PROJECT_DB_PATH = ROOT / "data" / "project_tracker.db"
TRADES_DB_PATH = ROOT / "data" / "trades.db"


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_tasks(db_path: Path = PROJECT_DB_PATH) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, description, due_date, done, reminder FROM tasks WHERE done = 0"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def fetch_user_stories(db_path: Path = PROJECT_DB_PATH) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, story, priority, status FROM user_stories WHERE LOWER(status) != 'done'"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def fetch_personal_goals(db_path: Path = PROJECT_DB_PATH) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, goal, category, target_date, completed FROM personal_goals WHERE completed = 0"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def fetch_trade_alerts(db_path: Path = TRADES_DB_PATH, limit: int = 5) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT ticker, score, change_percent, updated_at
            FROM watchlist
            WHERE score >= 7
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]
