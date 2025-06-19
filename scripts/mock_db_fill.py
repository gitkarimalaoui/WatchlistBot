"""Create a small set of rows in trades.db for testing purposes."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trades.db"

WATCHLIST_SQL = """
CREATE TABLE IF NOT EXISTS watchlist (
    ticker TEXT PRIMARY KEY,
    score REAL,
    volume REAL,
    updated_at TEXT
)
"""

TRADES_SQL = """
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT,
    ticker TEXT,
    action TEXT,
    prix REAL,
    montant REAL
)
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(WATCHLIST_SQL)
        conn.execute(TRADES_SQL)
        conn.execute(
            "INSERT OR REPLACE INTO watchlist (ticker, score, volume, updated_at) VALUES ('AAA', 9.0, 1000, datetime('now'))"
        )
        conn.execute(
            "INSERT INTO trades (datetime, ticker, action, prix, montant) VALUES (datetime('now'), 'AAA', 'achat', 1.0, 100)"
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
