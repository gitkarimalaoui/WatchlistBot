import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trades.db"


def _time_column(conn: sqlite3.Connection) -> str:
    cur = conn.execute("PRAGMA table_info(historical_data)")
    cols = [row[1] for row in cur.fetchall()]
    return "timestamp" if "timestamp" in cols else "date"


def load_historical(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Return historical quotes for ``ticker`` between ``start_date`` and ``end_date``.

    Parameters
    ----------
    ticker : str
        Symbol to query.
    start_date : str
        First date (inclusive) ``YYYY-MM-DD``.
    end_date : str
        Last date (inclusive) ``YYYY-MM-DD``.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        time_col = _time_column(conn)
        query = (
            f"SELECT * FROM historical_data WHERE ticker = ? AND {time_col} BETWEEN ? AND ? ORDER BY {time_col}"
        )
        df = pd.read_sql_query(query, conn, params=(ticker, start_date, end_date))
    finally:
        conn.close()

    if time_col != "timestamp" and "timestamp" not in df.columns and time_col in df.columns:
        df.rename(columns={time_col: "timestamp"}, inplace=True)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def insert_historical(ticker: str, df: pd.DataFrame) -> None:
    """Insert historical rows for ``ticker`` into the database."""
    if df is None or df.empty:
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("PRAGMA table_info(historical_data)")
        cols = [row[1] for row in cur.fetchall()]
        time_col = "timestamp" if "timestamp" in cols else "date"

        df = df.copy()
        df["ticker"] = ticker
        if "Adj Close" in df.columns:
            df.rename(columns={"Adj Close": "adj_close"}, inplace=True)
        if time_col == "date" and "timestamp" in df.columns:
            df.rename(columns={"timestamp": "date"}, inplace=True)
        elif time_col == "timestamp" and "date" in df.columns:
            df.rename(columns={"date": "timestamp"}, inplace=True)
        df.to_sql("historical_data", conn, if_exists="append", index=False)
    finally:
        conn.close()
