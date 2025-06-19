import os
import sqlite3
from typing import Dict

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trades.db")


def _canonical(ticker: str) -> str:
    return ticker.split(".")[0].strip().upper()


def clean_duplicates(db_path: str = DB_PATH) -> Dict[str, int]:
    """Remove duplicate tickers and related rows across tables.

    Parameters
    ----------
    db_path : str
        SQLite database path.

    Returns
    -------
    Dict[str, int]
        Number of rows deleted per table.
    """
    if not os.path.exists(db_path):
        return {}

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("BEGIN;")
        rows = cur.execute("SELECT id, ticker FROM watchlist").fetchall()
        groups = {}
        for row_id, ticker in rows:
            canon = _canonical(ticker)
            groups.setdefault(canon, []).append((row_id, ticker))

        tables = [
            "intraday_data",
            "intraday_smart",
            "historical_data",
            "trades",
            "trades_reels",
            "trades_simules",
            "news_by_ticker",
        ]
        table_cols = {}
        for t in tables:
            if cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (t,),
            ).fetchone():
                cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})")] 
                table_cols[t] = cols

        deleted = {"watchlist": 0}

        for canon, items in groups.items():
            if len(items) <= 1:
                continue
            items.sort()
            keep_id, keep_ticker = items[0]
            for dup_id, dup_ticker in items[1:]:
                cur.execute("DELETE FROM watchlist WHERE id=?", (dup_id,))
                deleted["watchlist"] += cur.rowcount
                if dup_ticker == keep_ticker:
                    continue
                for table, cols in table_cols.items():
                    column = "ticker" if "ticker" in cols else (
                        "symbol" if "symbol" in cols else None
                    )
                    if not column:
                        continue
                    cur.execute(
                        f"DELETE FROM {table} WHERE {column}=?",
                        (dup_ticker,),
                    )
                    count = cur.rowcount
                    if count:
                        deleted[table] = deleted.get(table, 0) + count

        conn.commit()
        return deleted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
