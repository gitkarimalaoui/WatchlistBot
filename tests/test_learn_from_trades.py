import json
import sqlite3
from intelligence.learn_from_trades import load_trades, compute_performance, update_meta

def test_compute_and_update(tmp_path):
    db_path = tmp_path / "trades.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE trades_simules (gain_net REAL)")
    conn.executemany(
        "INSERT INTO trades_simules (gain_net) VALUES (?)",
        [(5.0,), (-3.0,), (2.0,)],
    )
    conn.commit()
    conn.close()

    gains = load_trades(str(db_path))
    stats = compute_performance(gains)
    assert stats["trades"] == 3
    assert stats["gain_total"] == 4.0
    assert abs(stats["win_rate"] - 2/3) < 1e-4

    meta_path = tmp_path / "meta.json"
    update_meta(stats, str(meta_path))
    data = json.loads(meta_path.read_text())
    assert data["performance"]["trades"] == 3
