from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Tuple

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trades.db"
MIN_HISTORICAL_ROWS = 250
MIN_INTRADAY_ROWS = 1500


def ensure_table(conn: sqlite3.Connection) -> None:
    """Ensure the completeness tracking table exists."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS data_completeness (
            ticker TEXT PRIMARY KEY,
            hist_rows INTEGER DEFAULT 0,
            intra_rows INTEGER DEFAULT 0,
            hist_complete INTEGER DEFAULT 0,
            intra_complete INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()


def is_ticker_complete(conn: sqlite3.Connection, ticker: str) -> Tuple[bool, bool]:
    """Return completeness flags for ``ticker``."""
    cur = conn.execute(
        "SELECT hist_complete, intra_complete FROM data_completeness WHERE ticker = ?",
        (ticker,),
    )
    row = cur.fetchone()
    if not row:
        return False, False
    return bool(row[0]), bool(row[1])


def update_completeness(
    conn: sqlite3.Connection, ticker: str, hist_rows: int, intra_rows: int
) -> None:
    """Update completeness counts and flags for ``ticker``."""
    hist_complete = int(hist_rows >= MIN_HISTORICAL_ROWS)
    intra_complete = int(intra_rows >= MIN_INTRADAY_ROWS)
    conn.execute(
        """
        INSERT INTO data_completeness (ticker, hist_rows, intra_rows, hist_complete, intra_complete)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET
            hist_rows = excluded.hist_rows,
            intra_rows = excluded.intra_rows,
            hist_complete = excluded.hist_complete,
            intra_complete = excluded.intra_complete
        """,
        (ticker, hist_rows, intra_rows, hist_complete, intra_complete),
    )
    conn.commit()
