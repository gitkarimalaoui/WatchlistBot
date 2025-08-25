import sqlite3

def init(conn: sqlite3.Connection):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_intraday_smart_ticker ON intraday_smart(ticker);"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_intraday_smart_ticker_created_at ON intraday_smart(ticker, created_at);"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scores_symbol_date ON scores(symbol, date);"
    )
