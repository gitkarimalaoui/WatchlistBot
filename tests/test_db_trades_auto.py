import sqlite3
from datetime import datetime
from db.trades import get_nb_trades_du_jour


def test_get_nb_trades_du_jour(tmp_path):
    db_path = tmp_path / "trades.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE trades_reels (id INTEGER PRIMARY KEY, symbol TEXT, price REAL, qty INTEGER, side TEXT, timestamp TEXT, source TEXT)"
    )
    conn.executemany(
        "INSERT INTO trades_reels (symbol, price, qty, side, timestamp, source) VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("ABC", 1.0, 1, "buy", "2024-01-01T10:00:00", "t"),
            ("ABC", 1.0, 1, "buy", "2024-01-01T11:00:00", "t"),
            ("XYZ", 1.0, 1, "buy", "2024-01-01T12:00:00", "t"),
        ],
    )
    conn.commit()
    conn.close()

    count = get_nb_trades_du_jour("ABC", datetime(2024, 1, 1), db_path=str(db_path))
    assert count == 2
