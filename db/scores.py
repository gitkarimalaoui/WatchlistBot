import sqlite3


def update_score_watchlist(ticker: str, score: int, pump_pct: float, ema_diff: float, rsi: float) -> None:
    conn = sqlite3.connect("data/trades.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE watchlist
        SET score = ?, pump_pct_60s = ?, ema_diff = ?, rsi = ?, updated_at = datetime('now')
        WHERE ticker = ?
        """,
        (score, pump_pct, ema_diff, rsi, ticker),
    )
    conn.commit()
    conn.close()
