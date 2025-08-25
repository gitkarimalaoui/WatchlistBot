"""AI score for pump detection."""

from __future__ import annotations

from typing import Optional

from data.indicateurs import (
    get_rsi,
    get_ema,
    get_vwap,
    get_float_shares,
    get_macd,
)
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
    vwap = get_vwap(ticker)
    float_shares = get_float_shares(ticker)
    macd, macd_signal = get_macd(ticker)
    pump_pct = get_pump_pct(ticker)
    momentum = get_momentum(ticker)
    ema_diff = (ema9 - ema21) if (ema9 is not None and ema21 is not None) else None

    score = 0.0
    if rsi is not None and 65 <= rsi <= 72:
        score += 10
    if (
        ema9 is not None
        and ema21 is not None
        and ema21 != 0
        and ema9 > ema21 * 1.001
    ):
        score += 25
    if volume and volume > 750_000:
        score += 15
    if vwap is not None and price is not None and price < vwap:
        score += 5
    if float_shares is not None and float_shares < 100_000_000:
        score += 5
    if (
        macd is not None
        and macd_signal is not None
        and macd > macd_signal
        and momentum is not None
        and momentum > 1
    ):
        score += 10
    if pump_pct > 1.5:
        score += 20

    score = round(min(score, 100), 2)

    return {
        "ticker": ticker,
        "score": score,
        "rsi": rsi,
        "ema9": ema9,
        "ema21": ema21,
        "volume": volume,
        "pump_pct_60s": round(pump_pct, 2),
        "momentum": momentum,
        "vwap": vwap,
        "float_shares": float_shares,
        "macd": macd,
        "macd_signal": macd_signal,
        "ema_diff": ema_diff,
        "status": "OK",
    }
