import sqlite3

from core.db import DB_PATH


def update_score_watchlist(
    ticker: str,
    score: float,
    pump_pct: float,
    ema_diff: float,
    rsi: float,
) -> None:
    """Met à jour les informations de scoring pour ``ticker`` dans ``watchlist``."""

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist (
                ticker TEXT PRIMARY KEY,
                score INTEGER,
                pump_pct_60s REAL,
                ema_diff REAL,
                rsi REAL,
                updated_at TEXT
            )
            """,
        )

        conn.execute(
            """
            UPDATE watchlist
            SET score = ?, pump_pct_60s = ?, ema_diff = ?, rsi = ?, updated_at = datetime('now')
            WHERE ticker = ?
            """,
            (score, pump_pct, ema_diff, rsi, ticker),
        )

        conn.commit()
    finally:
        conn.close()
