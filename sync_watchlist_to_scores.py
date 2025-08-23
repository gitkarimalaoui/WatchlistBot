#!/usr/bin/env python3
"""Synchronise watchlist tickers to the scores table.

Reads tickers from the ``watchlist`` table, computes a score for each ticker
using the existing scalping logic and upserts the results into ``scores``.
This bridges the gap between the Jaguar import which fills ``watchlist`` and
 the scoring process consumed by the UI.
"""

from __future__ import annotations

from db.bulk_upsert import DB_PATH, get_conn
from execution.strategie_scalping import _compute_score
from writers.scoring_writer import upsert_watchlist_and_scores


def process_watchlist_to_scores() -> None:
    """Fetch tickers from watchlist, score them and persist snapshots/history."""

    conn = get_conn()
    print("USING DB:", DB_PATH)
    tickers = [row[0] for row in conn.execute("SELECT DISTINCT ticker FROM watchlist;")]
    rows = []
    for sym in tickers:
        data = _compute_score(sym)
        if not data:
            continue
        rows.append((sym, float(data.get("score", 0)), data))
    if rows:
        upsert_watchlist_and_scores(conn, rows)
    conn.close()


if __name__ == "__main__":  # pragma: no cover - manual execution
    process_watchlist_to_scores()
