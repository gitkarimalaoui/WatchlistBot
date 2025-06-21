import sqlite3

from db import scores


def test_update_score_watchlist(tmp_trades_db, monkeypatch):
    db_file = tmp_trades_db
    conn = sqlite3.connect(db_file)
    conn.execute('CREATE TABLE watchlist (ticker TEXT PRIMARY KEY, score INTEGER, pump_pct_60s REAL, ema_diff REAL, rsi REAL, updated_at TEXT)')
    conn.execute("INSERT INTO watchlist (ticker, score, pump_pct_60s, ema_diff, rsi, updated_at) VALUES ('AAA', 0, 0, 0, 0, '')")
    conn.commit()
    conn.close()

    real_connect = sqlite3.connect

    class DummySqlite:
        def connect(self, path):
            assert path.endswith('trades.db')
            return real_connect(db_file)

    monkeypatch.setattr(scores, 'sqlite3', DummySqlite())
    monkeypatch.setattr(scores, 'DB_PATH', str(db_file), raising=False)
    monkeypatch.setattr('core.db.DB_PATH', str(db_file), raising=False)

    scores.update_score_watchlist('AAA', 9.9, 5.0, 0.2, 70.0)

    conn = sqlite3.connect(db_file)
    row = conn.execute('SELECT score, pump_pct_60s, ema_diff, rsi FROM watchlist WHERE ticker="AAA"').fetchone()
    conn.close()
    assert row == (9.9, 5.0, 0.2, 70.0)
