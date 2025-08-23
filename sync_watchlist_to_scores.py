#!/usr/bin/env python3
"""Synchronise watchlist tickers to the scores table.

Reads tickers from the ``watchlist`` table, computes a score for each ticker
using the existing scalping logic and upserts the results into ``scores``.
This bridges the gap between the Jaguar import which fills ``watchlist`` and
 the scoring process consumed by the UI.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from db.bulk_upsert import bulk_upsert_scores, get_conn, DB_PATH
from db.init_sqlite import init
from execution.strategie_scalping import _compute_score


def now_iso() -> str:
    """Return the current UTC timestamp in ISO format."""

    return datetime.now(timezone.utc).isoformat()


def process_watchlist_to_scores() -> None:
    """Fetch tickers from watchlist, score them and persist to ``scores``."""

    conn = get_conn()
    init(conn)
    print("USING DB:", DB_PATH)
    tickers = [row[0] for row in conn.execute("SELECT DISTINCT ticker FROM watchlist;")]
    rows = []
    for sym in tickers:
        data = _compute_score(sym)
        if not data:
            continue
        rows.append((sym, now_iso(), float(data.get("score", 0)), json.dumps(data)))
    conn.close()
    if rows:
        bulk_upsert_scores(rows)


if __name__ == "__main__":  # pragma: no cover - manual execution
    process_watchlist_to_scores()
