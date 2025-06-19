def test_clean_duplicates(tmp_path):
    import sqlite3
    from db import cleanup

    db_file = tmp_path / "trades.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        "CREATE TABLE watchlist (id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT)"
    )
    conn.execute("CREATE TABLE intraday_data (ticker TEXT, timestamp TEXT)")
    conn.execute("CREATE TABLE historical_data (ticker TEXT, timestamp TEXT, close REAL)")
    conn.execute("CREATE TABLE trades (id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT)")
    conn.commit()

    conn.executemany(
        "INSERT INTO watchlist (ticker) VALUES (?)",
        [("ABC",), ("ABC.US",), ("XYZ",), ("XYZ",)],
    )
    for tic in ["ABC", "ABC.US", "XYZ"]:
        conn.execute("INSERT INTO intraday_data (ticker, timestamp) VALUES (?, 't')", (tic,))
        conn.execute(
            "INSERT INTO historical_data (ticker, timestamp, close) VALUES (?, 't', 1.0)",
            (tic,),
        )
        conn.execute("INSERT INTO trades (ticker) VALUES (?)", (tic,))
    conn.commit()
    conn.close()

    stats = cleanup.clean_duplicates(str(db_file))
    assert stats["watchlist"] == 2

    conn = sqlite3.connect(db_file)
    wl = [r[0] for r in conn.execute("SELECT ticker FROM watchlist ORDER BY id").fetchall()]
    assert wl == ["ABC", "XYZ"]
    assert conn.execute("SELECT COUNT(*) FROM intraday_data").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM historical_data").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0] == 2
    conn.close()
