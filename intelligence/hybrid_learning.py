import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Dict, Any, Union

import pandas as pd

from backtest.ai_backtest_runner import run_backtest
from intelligence.learn_from_trades import load_trades, compute_performance

DEFAULT_META_PATH = Path("config/meta_ia.json")
DEFAULT_MODEL = "dummy_model_v1"


def _analyse_backtest(
    tickers: Iterable[str],
    start: str,
    end: str,
    model_version: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Run backtest and return aggregated statistics."""
    df = run_backtest(tickers, start, end, model_version, report_path=Path("/tmp/report.csv"))
    if df.empty:
        return {"backtest": {}}
    return {
        "backtest": {
            "count": int(len(df)),
            "avg_ai_score": float(df["ai_score"].mean()),
            "avg_return_pct": float(df["avg_return_pct"].mean()),
        }
    }


def _analyse_realtime(db_path: str) -> Dict[str, Any]:
    gains = load_trades(db_path)
    perf = compute_performance(gains)
    return {"realtime": perf}


def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    res = {}
    res.update(a)
    res.update(b)
    return res


def update_meta(stats: Dict[str, Any], meta_path: Union[str, Path] = DEFAULT_META_PATH) -> Dict[str, Any]:
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    else:
        meta = {}
    meta["hybrid_learning"] = stats
    meta["derniere_mise_a_jour"] = datetime.now().isoformat()
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return meta


def run_hybrid_learning(
    tickers: Iterable[str],
    start: str,
    end: str,
    model_version: str = DEFAULT_MODEL,
    db_path: str = "data/trades.db",

    meta_path: Union[str, Path] = DEFAULT_META_PATH,

) -> Dict[str, Any]:
    """Execute backtest and realtime analysis then update meta file."""
    meta_path = Path(meta_path)
    backtest_stats = _analyse_backtest(tickers, start, end, model_version)
    realtime_stats = _analyse_realtime(db_path)
    combined = _merge(backtest_stats, realtime_stats)
    return update_meta(combined, meta_path)
