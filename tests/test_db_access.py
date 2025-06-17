import sqlite3
from pathlib import Path

from utils import db_access as db


def test_fetch_tasks(tmp_path: Path):
    db_path = tmp_path / "project_tracker.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE tasks (id INTEGER PRIMARY KEY, description TEXT, due_date TEXT, done INTEGER, reminder INTEGER)"
    )
    conn.execute(
        "INSERT INTO tasks (description, due_date, done, reminder) VALUES (?, ?, 0, 1)",
        ("Test", "2025-12-31"),
    )
    conn.commit()
    conn.close()

    rows = db.fetch_tasks(db_path)
    assert rows
    assert rows[0]["description"] == "Test"


def test_fetch_trade_alerts(tmp_path: Path):
    db_path = tmp_path / "trades.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE watchlist (ticker TEXT, score REAL, change_percent REAL, updated_at TEXT)"
    )
    conn.execute(
        "INSERT INTO watchlist (ticker, score, change_percent, updated_at) VALUES (?, ?, ?, ?)",
        ("ABC", 9.0, 5.0, "2024-01-01"),
    )
    conn.commit()
    conn.close()

    rows = db.fetch_trade_alerts(db_path)
    assert rows
    assert rows[0]["ticker"] == "ABC"
