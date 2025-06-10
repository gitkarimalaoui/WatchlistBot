import sqlite3
import pandas as pd
from utils import db_historical as db


def test_insert_historical(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE historical_data (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL,
            volume INTEGER
        )
        """
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(db, "DB_PATH", db_file)

    df = pd.DataFrame({
        "Date": ["2024-01-01"],
        "Open": [1.0],
        "High": [1.1],
        "Low": [0.9],
        "Close": [1.0],
        "Adj Close": [1.0],
        "Volume": [100]
    })
    db.insert_historical("AAA", df)

    conn = sqlite3.connect(db_file)
    count = conn.execute("SELECT COUNT(*) FROM historical_data").fetchone()[0]
    conn.close()

    assert count == 1
