import os
import sqlite3

from core.db import DB_PATH


def ensure_schema(db_path: str = DB_PATH) -> None:
    if not os.path.exists(db_path):
        return
    conn = sqlite3.connect(str(db_path))
    try:
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trades'"
        ).fetchone()
        if not table:
            return
        rows = conn.execute("PRAGMA table_info(trades)").fetchall()
        existing = {r[1] for r in rows}
        columns = [
            ("atr", "REAL"),
            ("gap_pct", "REAL"),
            ("stop_loss", "REAL"),
            ("take_profit", "REAL"),
            ("entry_time", "TEXT"),
            ("partial_exit_3pct", "REAL"),
            ("partial_exit_7pct", "REAL"),
        ]
        for col, typ in columns:
            if col not in existing:
                conn.execute(f"ALTER TABLE trades ADD COLUMN {col} {typ};")
        conn.commit()
    finally:
        conn.close()
