import sqlite3
from pathlib import Path
from typing import Optional

from utils.db_access import TRADES_DB_PATH


def _ensure_columns(conn: sqlite3.Connection) -> None:
    cur = conn.execute("PRAGMA table_info(watchlist)")
    cols = [row[1] for row in cur.fetchall()]
    mapping = {
        "pdufa_date": "TEXT",
        "market_cap": "REAL",
        "de_ratio": "REAL",
        "cash_runway": "REAL",
    }
    for col, typ in mapping.items():
        if col not in cols:
            conn.execute(f"ALTER TABLE watchlist ADD COLUMN {col} {typ}")
    conn.commit()


def update_fundamentals(
    ticker: str,
    pdufa_date: Optional[str],
    market_cap: Optional[float],
    de_ratio: Optional[float],
    cash_runway: Optional[float],
    db_path: Path = TRADES_DB_PATH,
) -> None:
    if not db_path.exists():
        return
    conn = sqlite3.connect(str(db_path))
    try:
        _ensure_columns(conn)
        conn.execute(
            """
            UPDATE watchlist
            SET pdufa_date = ?, market_cap = ?, de_ratio = ?, cash_runway = ?,
                updated_at = datetime('now')
            WHERE ticker = ?
            """,
            (pdufa_date, market_cap, de_ratio, cash_runway, ticker),
        )
        conn.commit()
    finally:
        conn.close()
