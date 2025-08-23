import sqlite3
import sqlite3
from pathlib import Path
import sqlite3
from typing import Iterable, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "trades.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH.as_posix(), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS scores(
      symbol TEXT NOT NULL,
      date   TEXT NOT NULL,
      score  REAL NOT NULL,
      details_json TEXT,
      PRIMARY KEY (symbol, date)
    );
    """
    )
    conn.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_scores_symbol_date
      ON scores(symbol, date);
    """
    )
    conn.commit()


def bulk_upsert_scores(rows: Iterable[Tuple[str, str, float, str]]) -> None:
    """Insert or update many score rows in a single transaction."""
    conn = get_conn()
    init_schema(conn)
    with conn:
        conn.executemany(
            """
          INSERT INTO scores(symbol, date, score, details_json)
          VALUES (?, ?, ?, ?)
          ON CONFLICT(symbol, date) DO UPDATE SET
            score=excluded.score,
            details_json=excluded.details_json;
        """,
            rows,
        )
    conn.close()
