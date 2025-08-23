from __future__ import annotations
import sqlite3

DATE_CANDIDATES = ["batch_ts", "updated_at", "created_at", "date", "ts", "timestamp"]

def get_watchlist_cols(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("PRAGMA table_info(watchlist);").fetchall()
    return {r[1] for r in rows}

def ensure_column(conn: sqlite3.Connection, table: str, col: str, coltype: str) -> None:
    has = conn.execute(
        "SELECT 1 FROM pragma_table_info(?) WHERE name=?;", (table, col)
    ).fetchone()
    # Note: sqlite ne supporte pas ce PRAGMA paramétré → fallback string:
    if not has:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype};")

def ensure_indexes(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON watchlist(symbol);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_batch  ON watchlist(batch_ts);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_date        ON scores(date);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_symbol_date ON scores(symbol, date);")

def ensure_schema_watchlist_scores(conn: sqlite3.Connection) -> None:
    # colonnes Option A pour watchlist
    cols = get_watchlist_cols(conn)
    if "score" not in cols:
        conn.execute("ALTER TABLE watchlist ADD COLUMN score REAL;")
    if "batch_ts" not in cols:
        conn.execute("ALTER TABLE watchlist ADD COLUMN batch_ts TEXT;")
    if "updated_at" not in cols:
        conn.execute("ALTER TABLE watchlist ADD COLUMN updated_at TEXT;")

    # table scores (journal historique)
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS scores(
      symbol       TEXT NOT NULL,
      date         TEXT NOT NULL,
      score        REAL NOT NULL,
      details_json TEXT,
      updated_at   TEXT,
      PRIMARY KEY(symbol, date)
    );
    """
    )
    ensure_indexes(conn)
    conn.commit()

def pick_date_column(conn: sqlite3.Connection) -> str | None:
    cols = get_watchlist_cols(conn)
    for c in DATE_CANDIDATES:
        if c in cols:
            return c
    return None
