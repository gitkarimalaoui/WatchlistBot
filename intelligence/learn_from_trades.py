import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict

DB_PATH = os.path.join("data", "trades.db")
META_PATH = os.path.join("config", "meta_ia.json")


def load_trades(db_path: str = DB_PATH) -> List[float]:
    """Return a list of gain_net values from the trades_simules table."""
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT gain_net FROM trades_simules").fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows if r[0] is not None]


def compute_performance(gains: List[float]) -> Dict[str, float]:
    """Compute total gain and win rate from a list of gains."""
    total_trades = len(gains)
    gain_total = sum(gains)
    winners = sum(1 for g in gains if g > 0)
    win_rate = winners / total_trades if total_trades else 0.0
    return {
        "trades": total_trades,
        "gain_total": round(gain_total, 2),
        "win_rate": round(win_rate, 4),
    }


def update_meta(stats: Dict[str, float], meta_path: str = META_PATH) -> Dict:
    """Update the meta_ia.json file with new performance statistics."""
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    else:
        meta = {}

    meta["performance"] = stats
    meta["derniere_mise_a_jour"] = datetime.now().isoformat()

    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return meta


def main(db_path: str = DB_PATH, meta_path: str = META_PATH) -> None:
    gains = load_trades(db_path)
    stats = compute_performance(gains)
    update_meta(stats, meta_path)
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    import argparse

    parser = argparse.ArgumentParser(description="Learn from executed trades")
    parser.add_argument("--db", default=DB_PATH, help="Path to trades.db")
    parser.add_argument("--meta", default=META_PATH, help="Path to meta_ia.json")
    args = parser.parse_args()
    main(db_path=args.db, meta_path=args.meta)
