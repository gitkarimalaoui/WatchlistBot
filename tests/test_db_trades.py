import sqlite3

from db import trades


def test_enregistrer_trade_ia(tmp_trades_db, monkeypatch):
    db_file = tmp_trades_db

    real_connect = sqlite3.connect

    class DummySqlite:
        def connect(self, path):
            assert path == 'data/trades.db'
            return real_connect(db_file)

    monkeypatch.setattr(trades, 'sqlite3', DummySqlite())

    trades.enregistrer_trade_ia(
        ticker='AAA', prix=1.23, montant=100.0, score=90, pump_pct=5.0,
        rsi=70.0, ema9=2.0, ema21=1.0, momentum=1.1, source='WS'
    )

    conn = sqlite3.connect(db_file)
    row = conn.execute('SELECT ticker, montant, score_at_entry FROM trades').fetchone()
    conn.close()
    assert row == ('AAA', 100.0, 90)
