import json
import pandas as pd
from pathlib import Path

import intelligence.hybrid_learning as hl


def test_run_hybrid_learning(monkeypatch, tmp_path):
    df_backtest = pd.DataFrame({
        "ticker": ["T1", "T2"],
        "ai_score": [60, 40],
        "avg_return_pct": [5.0, -2.0],
    })

    monkeypatch.setattr(hl, "run_backtest", lambda *a, **k: df_backtest)
    monkeypatch.setattr(hl, "load_trades", lambda db: [1.0, -0.5])
    monkeypatch.setattr(hl, "compute_performance", lambda gains: {"trades": len(gains), "gain_total": sum(gains), "win_rate": 0.5})

    db_path = tmp_path / "trades.db"
    meta_path = tmp_path / "meta.json"

    result = hl.run_hybrid_learning(["A"], "2024-01-01", "2024-06-01", db_path=str(db_path), meta_path=meta_path)

    assert meta_path.exists()
    data = json.loads(meta_path.read_text())
    assert "hybrid_learning" in data
    assert result["hybrid_learning"]["backtest"]["count"] == 2
    assert result["hybrid_learning"]["realtime"]["trades"] == 2
