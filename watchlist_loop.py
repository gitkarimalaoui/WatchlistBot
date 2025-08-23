"""Batch scanning pipeline using async fetch and DB batching."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3

import pandas as pd

from db.bulk_upsert import bulk_upsert_scores
from db.init_sqlite import init as init_db
from intelligence.ai_scorer import score_batch
from observability.perf import step
from prescreen import screen_ticker, prefilter_quotes
from utils.utils_finnhub import fetch_quotes_batch


def run_scan(universe: str, limit: int = 500) -> None:
    tickers = json.loads(Path(universe).read_text())[:limit]
    tickers = [t for t in tickers if screen_ticker(t)]

    with step("fetch_batch"):
        quotes = fetch_quotes_batch(tickers)

    df = pd.DataFrame(quotes)
    df["symbol"] = pd.Series(tickers, dtype="category")
    df = prefilter_quotes(df)

    with step("score"):
        scored = score_batch(df)

    rows = [
        (row.symbol, pd.Timestamp.utcnow().date().isoformat(), row.score, row.to_json())
        for row in scored.itertuples()
    ]

    conn = sqlite3.connect(Path(__file__).resolve().parent / "data" / "trades.db")
    init_db(conn)
    with step("db_write"):
        bulk_upsert_scores(conn, rows)
    conn.close()


if __name__ == "__main__":  # pragma: no cover - CLI
    import typer

    def main(universe: str, limit: int = 500):
        run_scan(universe, limit)

    typer.run(main)
