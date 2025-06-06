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

def insert_intraday(ticker: str, df: pd.DataFrame) -> None:
    """Append intraday rows for ``ticker`` to the database."""
    if df is None or df.empty:
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        df = df.copy()
        df['ticker'] = ticker
        df.to_sql('intraday_data', conn, if_exists='append', index=False)
    finally:
        conn.close()


def load_intraday(ticker: str, start: str | None = None) -> pd.DataFrame:
    """Load intraday rows for ``ticker`` from the database."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = "SELECT * FROM intraday_data WHERE ticker = ?"
        params = [ticker]
        if start:
            query += " AND timestamp >= ?"
            params.append(start)
        query += " ORDER BY timestamp"
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df
