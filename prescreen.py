import yfinance as yf
from functools import lru_cache
from typing import Optional
import pandas as pd


def _download(*args, **kwargs) -> pd.DataFrame:
    """Wrapper around ``yf.download`` that handles errors."""
    try:
        return yf.download(*args, progress=False, **kwargs)
    except Exception:
        return pd.DataFrame()


def get_premarket_volume(ticker: str) -> int:
    """Return pre-market volume traded for ``ticker``."""

    df = _download(ticker, period="1d", interval="1m", prepost=True)
    if df.empty:
        return 0
    # ensure we have timezone aware index
    if not df.index.tzinfo:
        df.index = df.index.tz_localize("UTC")
    df = df.between_time("04:00", "09:30")
    return int(df["Volume"].sum())


def get_average_volume(ticker: str, days: int = 10) -> Optional[float]:
    """Return average daily volume over ``days`` days."""

    df = _download(ticker, period=f"{days}d", interval="1d")
    if df.empty:
        return None
    return float(df["Volume"].tail(days).mean())


def get_gap_pct(ticker: str) -> Optional[float]:
    """Return percent gap between previous close and today's open."""

    df = _download(ticker, period="2d", interval="1d", prepost=True)
    if len(df) >= 2:
        prev_close = float(df["Close"].iloc[-2])
        today_open = float(df["Open"].iloc[-1])
        if prev_close:
            return (today_open - prev_close) / prev_close * 100
    return None


@lru_cache(maxsize=128)
def screen_ticker(ticker: str) -> bool:
    """Return ``True`` if ``ticker`` meets premarket screening criteria."""

    avg = get_average_volume(ticker) or 0
    if avg == 0:
        return False
    pre_vol = get_premarket_volume(ticker)
    ratio = pre_vol / avg
    gap = get_gap_pct(ticker)
    if gap is None:
        return False
    return ratio > 2 and 5 < abs(gap) < 15
