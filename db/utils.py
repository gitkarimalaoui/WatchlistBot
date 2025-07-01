import os
import sqlite3

from core.db import DB_PATH


def ensure_schema(db_path: str = DB_PATH) -> None:
    """Ensure required tables and columns exist in the database."""

    if not os.path.exists(db_path):
        return
    conn = sqlite3.connect(str(db_path))
    try:
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trades'"
        ).fetchone()
        if table:
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
        # Ensure trades_simules table
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trades_simules'"
        ).fetchone()
        if not table:
            conn.execute(
                """
                CREATE TABLE trades_simules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT,
                    prix_achat REAL,
                    quantite INTEGER,
                    frais REAL,
                    montant_total REAL,
                    sl REAL,
                    tp REAL,
                    exit_price REAL,
                    date DATETIME,
                    provenance TEXT,
                    note TEXT
                )
                """
            )
        else:
            rows = conn.execute("PRAGMA table_info(trades_simules)").fetchall()
            existing = {r[1] for r in rows}
            columns = [
                ("ticker", "TEXT"),
                ("prix_achat", "REAL"),
                ("quantite", "INTEGER"),
                ("frais", "REAL"),
                ("montant_total", "REAL"),
                ("sl", "REAL"),
                ("tp", "REAL"),
                ("exit_price", "REAL"),
                ("date", "DATETIME"),
                ("provenance", "TEXT"),
                ("note", "TEXT"),
            ]
            for col, typ in columns:
                if col not in existing:
                    conn.execute(
                        f"ALTER TABLE trades_simules ADD COLUMN {col} {typ};"
                    )
        # Ensure progression_ia table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progression_ia (
                module TEXT PRIMARY KEY,
                completed INTEGER DEFAULT 0,
                badge TEXT,
                completion_date TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
