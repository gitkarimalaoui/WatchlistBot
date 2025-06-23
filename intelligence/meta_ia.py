from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, Tuple

META_PATH = os.path.join("config", "meta_ia.json")
BACKUP_DIR = os.path.join("config", "meta_ia_backup")

DEFAULT_WEIGHTS = {
    "rsi_high": 0.2,
    "ema_bullish": 0.2,
    "momentum_pos": 0.2,
    "pump": 0.2,
}


def load_meta(path: str = META_PATH) -> Dict:
    """Return IA configuration from ``path`` with defaults applied."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}
    data.setdefault("weights", DEFAULT_WEIGHTS.copy())
    data.setdefault("disabled_signals", {})
    data.setdefault("history", [])
    return data


def save_meta(data: Dict, path: str = META_PATH, backup_dir: str = BACKUP_DIR) -> None:
    """Persist ``data`` to ``path`` and archive previous version."""
    if os.path.exists(path):
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy2(path, os.path.join(backup_dir, f"meta_ia_{ts}.json"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _extract_gain(row: Dict) -> Tuple[float, bool]:
    """Return ``gain`` and ``valid`` flag from a trade row dict."""
    entry = row.get("prix") or row.get("prix_achat") or row.get("entry_price")
    exit_p = row.get("exit_price") or row.get("prix_vente")
    frais = row.get("frais", 0.0)
    gain = row.get("gain_net")
    if gain is None and entry is not None and exit_p is not None:
        gain = (exit_p - entry) - frais
    return float(gain or 0.0), gain is not None


def update_meta_ia_from_results(db_path: str = "data/trades.db", meta_path: str = META_PATH) -> Dict:
    """Analyze trades to adjust IA weights and store the new configuration."""
    import sqlite3

    from intelligence.learn_from_trades import track_signal_effectiveness

    # Compute effectiveness metrics
    _, stats = track_signal_effectiveness(db_path)

    meta = load_meta(meta_path)
    weights = meta.get("weights", {}).copy()
    disabled = meta.get("disabled_signals", {})
    now = datetime.now()

    for signal, info in stats.items():
        win_rate = info.get("win_rate", 0.0)
        old = weights.get(signal, DEFAULT_WEIGHTS.get(signal, 0.0))
        if win_rate < 0.3:
            weights[signal] = 0.0
            disabled[signal] = {"until": (now + timedelta(days=7)).strftime("%Y-%m-%d")}
            continue
        if signal in disabled:
            try:
                until = datetime.fromisoformat(disabled[signal].get("until", ""))
                if until <= now:
                    disabled.pop(signal, None)
            except Exception:
                disabled.pop(signal, None)
        delta = (win_rate - 0.5) * 0.1
        weights[signal] = max(0.0, min(1.0, old + delta))

    meta["weights"] = weights
    meta["disabled_signals"] = disabled
    meta.setdefault("history", []).append({"timestamp": now.isoformat(), "stats": stats})
    save_meta(meta, meta_path)
    return meta
