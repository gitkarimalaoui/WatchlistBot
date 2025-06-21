"""Utility functions to compute trading performance metrics."""

from __future__ import annotations

import os
import sqlite3
from typing import Dict, Iterable, List, Tuple

import numpy as np

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trades.db")

TradeRow = Tuple[str, float, int, str, str]


def _load_trades(db_path: str = DB_PATH) -> List[TradeRow]:
    """Return rows from ``trades_reels`` ordered by timestamp."""
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT symbol, price, qty, side, timestamp FROM trades_reels ORDER BY timestamp"
        ).fetchall()
    finally:
        conn.close()
    return rows


def _compute_profits(rows: Iterable[TradeRow]) -> List[float]:
    """Return profit for each closed position using FIFO matching."""
    open_pos: Dict[str, List[List[float]]] = {}
    profits: List[float] = []
    for symbol, price, qty, side, _ in rows:
        side_low = side.lower()
        if side_low.startswith("achat") or side_low.startswith("buy"):
            open_pos.setdefault(symbol, []).append([price, qty])
            continue
        if side_low.startswith("vente") or side_low.startswith("sell"):
            queue = open_pos.setdefault(symbol, [])
            qty_left = qty
            while qty_left > 0 and queue:
                b_price, b_qty = queue[0]
                used = min(qty_left, b_qty)
                profits.append((price - b_price) * used)
                if used < b_qty:
                    queue[0][1] -= used
                    qty_left = 0
                else:
                    queue.pop(0)
                    qty_left -= used
    return profits


def compute_performance_metrics(db_path: str = DB_PATH) -> Dict[str, float]:
    """Compute win rate, profit factor, Sharpe ratio and drawdown from ``trades_reels``."""
    rows = _load_trades(db_path)
    profits = _compute_profits(rows)
    if not profits:
        return {"win_rate": 0.0, "profit_factor": 0.0, "sharpe_ratio": 0.0, "drawdown": 0.0}

    profits_arr = np.array(profits, dtype=float)
    wins = (profits_arr > 0).sum()
    win_rate = wins / len(profits_arr)

    gains = profits_arr[profits_arr > 0].sum()
    losses = -profits_arr[profits_arr < 0].sum()
    if losses == 0:
        profit_factor = float("inf") if gains > 0 else 0.0
    else:
        profit_factor = gains / losses

    mean = profits_arr.mean()
    std = profits_arr.std(ddof=1)
    sharpe = mean / std if std else 0.0

    equity = profits_arr.cumsum()
    running_max = np.maximum.accumulate(equity)
    drawdown = float((equity - running_max).min())

    return {
        "win_rate": round(float(win_rate), 4),
        "profit_factor": round(float(profit_factor), 4),
        "sharpe_ratio": round(float(sharpe), 4),
        "drawdown": round(drawdown, 4),
    }


__all__ = ["compute_performance_metrics"]

