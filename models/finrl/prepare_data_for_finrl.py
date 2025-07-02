from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from core.db import DB_PATH

DEFAULT_OUT = Path(__file__).resolve().parent / "finrl_data.csv"


def main(out_path: Path = DEFAULT_OUT) -> Path:
    """Extract intraday data from the DB into a CSV file for FinRL."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        df = pd.read_sql_query(
            "SELECT timestamp, ticker, close FROM intraday_data ORDER BY timestamp",
            conn,
        )
    finally:
        conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
