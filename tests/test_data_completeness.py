import sqlite3
from utils.data_completeness import (
    ensure_table,
    is_ticker_complete,
    update_completeness,
    MIN_HISTORICAL_ROWS,
    MIN_INTRADAY_ROWS,
)


def test_ticker_completeness(tmp_path):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    ensure_table(conn)

    update_completeness(conn, "AAA", MIN_HISTORICAL_ROWS, MIN_INTRADAY_ROWS - 10)
    assert is_ticker_complete(conn, "AAA") == (True, False)

    update_completeness(conn, "AAA", MIN_HISTORICAL_ROWS + 1, MIN_INTRADAY_ROWS + 5)
    assert is_ticker_complete(conn, "AAA") == (True, True)
    conn.close()
