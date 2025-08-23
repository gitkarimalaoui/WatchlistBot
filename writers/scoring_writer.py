from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from typing import Iterable, Tuple
from db.watchlist_utils import ensure_schema_watchlist_scores


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_watchlist_and_scores(
    conn: sqlite3.Connection,
    rows: Iterable[Tuple[str, float, dict]],
) -> int:
    """
    rows: [(symbol, score, details_dict), ...]
    - snapshot courant dans watchlist (Option A, lu par l'UI)
    - journal du lot dans scores (pour backtest/IA)
    """
    rows = list(rows)
    if not rows:
        return 0

    ensure_schema_watchlist_scores(conn)
    lot_ts = now_iso()

    with conn:  # transaction atomique
        # watchlist (snapshot du lot)
        conn.executemany(
            """
            INSERT INTO watchlist(symbol, score, batch_ts, updated_at)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
              score     = excluded.score,
              batch_ts  = excluded.batch_ts,
              updated_at= excluded.updated_at
            """,
            [(sym, float(score), lot_ts, lot_ts) for sym, score, _ in rows],
        )

        # scores (historique multi-lots)
        conn.executemany(
            """
            INSERT INTO scores(symbol, date, score, details_json, updated_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(symbol, date) DO UPDATE SET
              score        = excluded.score,
              details_json = excluded.details_json,
              updated_at   = excluded.updated_at
            """,
            [
                (sym, lot_ts, float(score), json.dumps(details or {}), lot_ts)
                for sym, score, details in rows
            ],
        )
    return len(rows)
