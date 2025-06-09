import pandas as pd
import requests
import time
import random
from datetime import datetime
from typing import Optional
import os
import asyncio
from config.config_manager import _load_dotenv, config_manager

try:
    from .utils_finnhub import fetch_finnhub_historical_data
except Exception:
    from utils_finnhub import fetch_finnhub_historical_data

_load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY") or config_manager.get("finnhub_api")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")


def fetch_from_yfinance(ticker: str) -> Optional[pd.DataFrame]:
    """Retrieve daily prices via Yahoo Finance."""
    try:
        import yfinance as yf
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty:
            return None
        # yfinance may return a MultiIndex when requesting a single ticker
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        df.rename(
            columns={
                "Date": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "close",
                "Volume": "volume",
            },
            inplace=True,
        )
        return df[["timestamp", "open", "high", "low", "close", "volume"]]
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[YF ERROR] {e}")
        return None


def fetch_from_finnhub(ticker: str) -> Optional[pd.DataFrame]:
    """Retrieve daily prices via Finnhub."""
    try:
        return fetch_finnhub_historical_data(ticker)
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[FINNHUB ERROR] {e}")
        return None


def fetch_from_alphavantage(ticker: str) -> Optional[pd.DataFrame]:
    """Retrieve daily prices via Alpha Vantage."""
    try:
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=compact"
        )
        res = requests.get(url).json()
        data = res.get("Time Series (Daily)", {})
        if not data:
            return None
        df = pd.DataFrame.from_dict(data, orient="index", dtype=float)
        df = df.rename(
            columns={
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. volume": "volume",
            }
        )
        df["timestamp"] = pd.to_datetime(df.index)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]].sort_values(
            "timestamp"
        )
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[AV ERROR] {e}")
        return None


def fetch_from_fmp(ticker: str) -> Optional[pd.DataFrame]:
    """Retrieve daily close prices via Financial Modeling Prep."""
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={FMP_API_KEY}&serietype=line"
        res = requests.get(url).json()
        historical = res.get("historical", [])
        if not historical:
            return None
        df = pd.DataFrame(historical)
        df.rename(columns={"date": "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[["timestamp", "close"]]
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[FMP ERROR] {e}")
        return None


def fetch_from_polygon(ticker: str) -> Optional[pd.DataFrame]:
    """Retrieve recent daily prices via Polygon."""
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/2024-12-01/{today}?adjusted=true&sort=asc&limit=120&apiKey={POLYGON_API_KEY}"
        )
        res = requests.get(url).json()
        results = res.get("results", [])
        if not results:
            return None
        df = pd.DataFrame(results)
        df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
        df.rename(
            columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"},
            inplace=True,
        )
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[POLYGON ERROR] {e}")
        return None


SOURCES = [
    ("Yahoo Finance", fetch_from_yfinance),
    ("Finnhub", fetch_from_finnhub),
    ("Alpha Vantage", fetch_from_alphavantage),
    ("FMP", fetch_from_fmp),
    ("Polygon", fetch_from_polygon),
]


def fetch_historical_data(ticker: str) -> Optional[pd.DataFrame]:
    """Try multiple free sources until one succeeds."""
    for name, func in SOURCES:
        print(f"[TRYING] {name} for {ticker}...")
        df = func(ticker)
        if df is not None and not df.empty:
            print(f"✅ Success with {name}, {len(df)} records for {ticker}")
            return df
        time.sleep(1.5 + random.uniform(0, 1.5))
    print(f"❌ All sources failed for {ticker}")
    return None


# ---------------------------------------------------------------------------
# Backward compatibility wrappers
# ---------------------------------------------------------------------------

def fetch_yf_historical_data(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
    threads: bool = False,
) -> Optional[pd.DataFrame]:
    """Legacy wrapper that only queries Yahoo Finance."""
    _ = period, interval, threads
    return fetch_from_yfinance(ticker)


def fetch_historical_with_fallback(ticker: str) -> Optional[pd.DataFrame]:
    """Legacy wrapper that calls :func:`fetch_historical_data`."""
    return fetch_historical_data(ticker)


# ---------------------------------------------------------------------------
# Async versions
# ---------------------------------------------------------------------------

async def async_fetch_from_yfinance(ticker: str) -> Optional[pd.DataFrame]:
    return await asyncio.to_thread(fetch_from_yfinance, ticker)


async def async_fetch_from_finnhub(ticker: str) -> Optional[pd.DataFrame]:
    return await asyncio.to_thread(fetch_from_finnhub, ticker)


async def async_fetch_from_alphavantage(ticker: str) -> Optional[pd.DataFrame]:
    return await asyncio.to_thread(fetch_from_alphavantage, ticker)


async def async_fetch_from_fmp(ticker: str) -> Optional[pd.DataFrame]:
    return await asyncio.to_thread(fetch_from_fmp, ticker)


async def async_fetch_from_polygon(ticker: str) -> Optional[pd.DataFrame]:
    return await asyncio.to_thread(fetch_from_polygon, ticker)


ASYNC_SOURCES = [
    ("Yahoo Finance", async_fetch_from_yfinance),
    ("Finnhub", async_fetch_from_finnhub),
    ("Alpha Vantage", async_fetch_from_alphavantage),
    ("FMP", async_fetch_from_fmp),
    ("Polygon", async_fetch_from_polygon),
]


async def async_fetch_historical_data(ticker: str) -> Optional[pd.DataFrame]:
    """Asynchronously try multiple free sources until one succeeds."""
    for name, func in ASYNC_SOURCES:
        print(f"[TRYING] {name} for {ticker}...")
        df = await func(ticker)
        if df is not None and not df.empty:
            print(f"✅ Success with {name}, {len(df)} records for {ticker}")
            return df
        await asyncio.sleep(1.5 + random.uniform(0, 1.5))
    print(f"❌ All sources failed for {ticker}")
    return None


async def async_fetch_historical_with_fallback(ticker: str) -> Optional[pd.DataFrame]:
    return await async_fetch_historical_data(ticker)

