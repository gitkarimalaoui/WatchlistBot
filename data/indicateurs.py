import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trades.db")


def _download(ticker: str, period: str = "1d", interval: str = "1m") -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.reset_index()
    except Exception:
        return pd.DataFrame()


def get_rsi(ticker: str, period: int = 14) -> Optional[float]:
    df = _download(ticker, "2d", "1m")
    if df.empty or len(df) < period + 1:
        return None
    close = df["Close"].astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean()
    rs = avg_gain.iloc[-1] / avg_loss.iloc[-1] if avg_loss.iloc[-1] else None
    return 100 - (100 / (1 + rs)) if rs else None


def get_ema(ticker: str, periods: List[int] = [9, 21]) -> Dict[int, Optional[float]]:
    df = _download(ticker, "7d", "1m")
    if df.empty:
        return {p: None for p in periods}
    close = df["Close"].astype(float)
    return {p: close.ewm(span=p, adjust=False).mean().iloc[-1] for p in periods}


def get_vwap(ticker: str) -> Optional[float]:
    df = _download(ticker, "1d", "1m")
    if df.empty:
        return None
    pv = (df["Close"] * df["Volume"]).cumsum()
    vol = df["Volume"].cumsum()
    return (pv / vol).iloc[-1] if not vol.empty else None


def get_macd(ticker: str) -> Tuple[Optional[float], Optional[float]]:
    df = _download(ticker, "7d", "1m")
    if df.empty:
        return None, None
    close = df["Close"].astype(float)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]


def get_volume(ticker: str, interval: str = "1m") -> Optional[float]:
    df = _download(ticker, "1d", interval)
    if df.empty:
        return None
    return float(df["Volume"].iloc[-1])


def get_last_price(ticker: str) -> Optional[float]:
    df = _download(ticker, "1d", "1m")
    if df.empty:
        return None
    return float(df["Close"].iloc[-1])


def get_price_5s_ago(ticker: str) -> Optional[float]:
    df = _download(ticker, "1d", "1m")
    if df.empty:
        return None
    if len(df) < 2:
        return float(df["Close"].iloc[-1])
    return float(df["Close"].iloc[-2])


def get_float(ticker: str) -> Optional[float]:
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT float FROM watchlist WHERE ticker = ?", (ticker,)
        ).fetchone()
    finally:
        conn.close()
    return float(row[0]) if row and row[0] is not None else None


def get_catalyseur_score(ticker: str) -> Optional[float]:
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT score FROM news_score WHERE symbol = ? ORDER BY last_analyzed DESC LIMIT 1",
            (ticker,)
        ).fetchone()
    finally:
        conn.close()
    return float(row[0]) if row else None


def check_breakout_sustain(momentum: float, volume_now: float, volume_5min_ago: float) -> bool:
    if volume_5min_ago == 0 or volume_5min_ago is None or volume_now is None:
        return False
    vol_ratio = volume_now / volume_5min_ago
    return momentum > 1.0 and vol_ratio >= 1.5
