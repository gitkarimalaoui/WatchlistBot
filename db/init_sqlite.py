import sqlite3

def init(conn: sqlite3.Connection):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ticks_symbol_ts ON intraday_smart(symbol, ts);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scores_symbol_date ON scores(symbol, date);")
