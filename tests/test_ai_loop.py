import json
import sqlite3
from intelligence.meta_ia import update_meta_ia_from_results, load_meta


def _setup_db(path):
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE trades (rsi_at_entry REAL, ema9 REAL, ema21 REAL, momentum REAL, pump_pct_60s REAL, prix REAL, exit_price REAL, frais REAL)"
    )
    conn.executemany(
        "INSERT INTO trades VALUES (?,?,?,?,?,?,?,?)",
        [
            (72, 1.2, 1.1, 0.5, 6, 1.0, 1.1, 0.02),
            (80, 1.3, 1.2, 0.2, 7, 1.0, 0.9, 0.02),
            (60, 0.9, 1.0, -0.5, 3, 1.0, 0.95, 0.02),
        ],
    )
    conn.commit()
    conn.close()


def test_update_meta_and_weights(tmp_path):
    db_path = tmp_path / "trades.db"
    _setup_db(db_path)
    meta_path = tmp_path / "meta.json"
    update_meta_ia_from_results(str(db_path), str(meta_path))
    data = load_meta(str(meta_path))
    for w in data["weights"].values():
        assert 0.0 <= w <= 1.0

    before = data["weights"].get("rsi_high")
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO trades VALUES (75,1.5,1.3,0.6,8,1.0,1.2,0.02)"
    )
    conn.commit()
    conn.close()
    update_meta_ia_from_results(str(db_path), str(meta_path))
    after = load_meta(str(meta_path))["weights"].get("rsi_high")
    assert after >= before
