from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trades.db"

def load_last_timestamp(ticker: str) -> pd.Timestamp | None:
    """Return the most recent timestamp stored for ``ticker``.

    Parameters
    ----------
    ticker : str
        Symbol to query.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(
            "SELECT MAX(timestamp) FROM intraday_data WHERE ticker = ?",
            (ticker,),
        )
        value = cur.fetchone()[0]
    finally:
        conn.close()

    if value:
        try:
            return pd.to_datetime(value)
        except Exception:
            return None
    return None
