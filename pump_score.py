"""AI score for pump detection."""

from __future__ import annotations

from typing import Optional

from data.indicateurs import get_rsi, get_ema
from data.stream_data_manager import get_latest_data
from movers_detector import get_pump_pct, get_momentum


_DEF_SCORE = 0


def score_pump_ia(ticker: str) -> dict:
    """Return a pump score between 0 and 100 for ``ticker``."""
    tick = get_latest_data(ticker)
    if tick.get("status") == "ERR" or tick.get("price") is None:
        return {"ticker": ticker, "status": "NO_DATA", "score": 0}

    price = tick.get("price")
    volume = tick.get("volume")
    rsi = get_rsi(ticker)
    emas = get_ema(ticker, [9, 21])
    ema9 = emas.get(9)
    ema21 = emas.get(21)
    pump_pct = get_pump_pct(ticker)
    momentum = get_momentum(ticker)

    score = 0.0
    if pump_pct:
        score += min(pump_pct * 20, 40)  # up to 40 points
    if volume:
        if volume > 1_000_000:
            score += 15
        elif volume > 500_000:
            score += 10
        elif volume > 100_000:
            score += 5
    if ema9 is not None and ema21 is not None and ema21 != 0 and ema9 > ema21:
        score += 20
    if rsi is not None:
        if rsi > 70:
            score += 15
        elif rsi > 60:
            score += 10
    if momentum > 0:
        score += 10

    score = round(min(score, 100), 2)

    return {
        "ticker": ticker,
        "score": score,
        "rsi": rsi,
        "ema9": ema9,
        "ema21": ema21,
        "volume": volume,
        "pump_pct_60s": round(pump_pct, 2),
        "status": "OK",
    }
