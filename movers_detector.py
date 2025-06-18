"""Real-time pump detection helper."""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Dict, List, Optional

from data.stream_data_manager import get_latest_data, WATCHLIST, latest_data

_WINDOW = 60.0  # seconds
_PUMP_THRESHOLD = 1.5  # percent

_price_history: Dict[str, Deque[tuple[float, float]]] = {}
_lock = threading.Lock()


def _trim(history: Deque[tuple[float, float]]) -> None:
    now = time.time()
    while history and now - history[0][0] > _WINDOW:
        history.popleft()


def update_price(ticker: str, price: float, ts: Optional[float] = None) -> None:
    """Record ``price`` for ``ticker`` at timestamp ``ts`` (default ``time.time()``)."""
    ts = ts or time.time()
    with _lock:
        hist = _price_history.setdefault(ticker, deque())
        hist.append((ts, price))
        _trim(hist)


def get_pump_pct(ticker: str) -> float:
    """Return percent gain over the last ``_WINDOW`` seconds for ``ticker``."""
    with _lock:
        hist = list(_price_history.get(ticker, []))
    if len(hist) < 2:
        return 0.0
    start = hist[0][1]
    end = hist[-1][1]
    if not start:
        return 0.0
    return (end - start) / start * 100.0


def get_momentum(ticker: str) -> float:
    """Return short term momentum based on the two latest prices."""
    with _lock:
        hist = list(_price_history.get(ticker, []))
    if len(hist) < 2:
        return 0.0
    prev = hist[-2][1]
    last = hist[-1][1]
    if not prev:
        return 0.0
    return (last - prev) / prev * 100.0


def get_top_movers(tickers: Optional[List[str]] = None) -> List[dict]:
    """Return top 10 tickers pumping over the last minute."""
    tickers = tickers or WATCHLIST
    movers: List[dict] = []
    for tic in tickers:
        data = get_latest_data(tic)
        if data.get("status") == "ERR":
            continue
        price = data.get("price")
        if price is None:
            continue
        volume = data.get("volume", 0)
        update_price(tic, float(price))
        pct = get_pump_pct(tic)
        data["pump_pct_60s"] = round(pct, 2)
        latest_data.setdefault(tic, {}).update({"pump_pct_60s": round(pct, 2)})
        if pct >= _PUMP_THRESHOLD:
            movers.append(
                {
                    "ticker": tic,
                    "pump_pct_60s": round(pct, 2),
                    "price": price,
                    "volume": volume,
                }
            )
    movers.sort(key=lambda x: x["pump_pct_60s"], reverse=True)
    return movers[:10]
