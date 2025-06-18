import sqlite3
from db.trades import enregistrer_trade_ia
from db.scores import update_score_watchlist


def test_enregistrer_trade_ia(monkeypatch, tmp_path):
    db_file = tmp_path / "trades.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT,
            ticker TEXT,
            action TEXT,
            prix REAL,
            montant REAL,
            score_at_entry INTEGER,
            pump_pct_60s REAL,
            rsi_at_entry REAL,
            ema9 REAL,
            ema21 REAL,
            momentum REAL,
            source_data TEXT
        )
        """
    )
    conn.commit()
    conn.close()

    orig_connect = sqlite3.connect

    def fake_connect(path):
        if path == "data/trades.db":
            return orig_connect(db_file)
        return orig_connect(path)

    monkeypatch.setattr(sqlite3, "connect", fake_connect)

    enregistrer_trade_ia("ABC", 1.0, 100.0, 90, 2.0, 70, 10, 9, 1.2, "test")

    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT ticker, score_at_entry, pump_pct_60s FROM trades").fetchone()
    conn.close()
    assert row == ("ABC", 90, 2.0)


def test_update_score_watchlist(monkeypatch, tmp_path):
    db_file = tmp_path / "trades.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE watchlist (
            ticker TEXT PRIMARY KEY,
            score INTEGER,
            pump_pct_60s REAL,
            ema_diff REAL,
            rsi REAL,
            updated_at TEXT
        )
        """
    )
    conn.execute("INSERT INTO watchlist (ticker, score, pump_pct_60s, ema_diff, rsi) VALUES ('ABC', 0, 0, 0, 0)")
    conn.commit()
    conn.close()

    orig_connect = sqlite3.connect

    def fake_connect(path):
        if path == "data/trades.db":
            return orig_connect(db_file)
        return orig_connect(path)

    monkeypatch.setattr(sqlite3, "connect", fake_connect)

    update_score_watchlist("ABC", 95, 2.0, 0.5, 70)

    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT score, pump_pct_60s, ema_diff, rsi FROM watchlist WHERE ticker='ABC'").fetchone()
    conn.close()
    assert row == (95, 2.0, 0.5, 70)
