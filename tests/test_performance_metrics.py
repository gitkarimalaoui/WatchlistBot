import sqlite3
from utils.performance_metrics import compute_performance_metrics

def test_compute_metrics(tmp_path):
    db_path = tmp_path / "trades.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE trades_reels (symbol TEXT, price REAL, qty INTEGER, side TEXT, timestamp TEXT, source TEXT)"
    )
    conn.executemany(
        "INSERT INTO trades_reels (symbol, price, qty, side, timestamp, source) VALUES (?,?,?,?,?,?)",
        [
            ("AAA", 10.0, 1, "achat", "2024-01-01T00:00:00", "t"),
            ("AAA", 12.0, 1, "vente", "2024-01-01T01:00:00", "t"),
            ("AAA", 8.0, 1, "achat", "2024-01-01T02:00:00", "t"),
            ("AAA", 6.0, 1, "vente", "2024-01-01T03:00:00", "t"),
        ],
    )
    conn.commit()
    conn.close()

    metrics = compute_performance_metrics(str(db_path))
    assert round(metrics["win_rate"], 2) == 0.5
    assert round(metrics["profit_factor"], 2) == 1.0
    assert round(metrics["sharpe_ratio"], 2) == 0.0
    assert metrics["drawdown"] == -2.0

