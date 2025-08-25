import asyncio
import sqlite3
from pathlib import Path
from typing import Any, List, Dict
import pandas as pd
from intelligence.ai_scorer import compute_global_score
from utils.db_access import TRADES_DB_PATH
from utils.async_utils import async_to_thread


def _fetch_watchlist(db_path: Path = TRADES_DB_PATH) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(
            """
            SELECT
                w.ticker,
                w.source,
                w.date,
                w.description,
                COALESCE(w.has_fda, 0) AS has_fda,
                w.float_shares AS float_shares,
                COALESCE(w.score, 0) AS score,
                COALESCE(ns.score, 0) AS score_gpt,
                COALESCE(ns.sentiment, 'NA') AS sentiment,
                i.price,
                i.volume,
                i.change_percent AS percent_gain
            FROM watchlist w
            LEFT JOIN news_score ns ON w.ticker = ns.symbol
            LEFT JOIN (
                SELECT s.ticker, s.price, s.volume, s.change_percent, s.timestamp
                FROM intraday_smart s
                JOIN (
                    SELECT ticker, MAX(timestamp) AS max_ts
                    FROM intraday_smart
                    GROUP BY ticker
                ) m ON s.ticker = m.ticker AND s.timestamp = m.max_ts
            ) i ON w.ticker = i.ticker
            """,
            conn,
        )
    finally:
        conn.close()
    df["global_score"] = df.apply(
        lambda r: compute_global_score(
            r.get("score"),
            r.get("score_gpt"),
            r.get("percent_gain"),
            r.get("volume"),
            r.get("float_shares"),
            r.get("sentiment"),
        ),
        axis=1,
    )
    return df.to_dict(orient="records")


async def get_watchlist_data_for_ui(db_path: Path = TRADES_DB_PATH) -> List[Dict[str, Any]]:
    return await async_to_thread(_fetch_watchlist, db_path)


def to_csv(data: List[Dict[str, Any]]) -> str:
    df = pd.DataFrame(data)
    return df.to_csv(index=False)
