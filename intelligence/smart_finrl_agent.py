from __future__ import annotations

import datetime
import importlib
import sqlite3
from pathlib import Path
from typing import Dict, Optional

from core.db import DB_PATH


def _log_metrics(metrics: Dict[str, object]) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS finrl_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                model_path TEXT,
                sharpe REAL,
                cumulative_return REAL
            )
            """
        )
        conn.execute(
            "INSERT INTO finrl_logs (date, model_path, sharpe, cumulative_return) VALUES (?, ?, ?, ?)",
            (
                datetime.datetime.utcnow().isoformat(),
                metrics.get("model_path"),
                metrics.get("sharpe_ratio"),
                metrics.get("cumulative_return"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def run_pipeline() -> Dict[str, object]:
    """Prepare data, train the FinRL model and log metrics."""
    prepare = importlib.import_module("models.finrl.prepare_data_for_finrl")
    data_path: Path = prepare.main()

    trainer = importlib.import_module("train_finrl_model")
    metrics: Dict[str, object] = trainer.train_from_config(data_path=data_path)

    _log_metrics(metrics)
    return metrics


def latest_model(checkpoint_dir: Path = Path("models/finrl/checkpoints")) -> Optional[Path]:
    paths = sorted(checkpoint_dir.glob("ppo_*.zip"))
    return paths[-1] if paths else None


def dummy_live_signals() -> Dict[str, str]:
    """Placeholder live signals using the latest model."""
    path = latest_model()
    if not path:
        return {}
    # Real implementation would load the model and produce signals.
    return {"signal": "HOLD", "model": str(path)}


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run_pipeline()
