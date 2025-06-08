import pandas as pd
import requests
import time
import random
from datetime import datetime, timedelta
from typing import Optional
import asyncio
import aiohttp

try:
    from .utils_finnhub import fetch_finnhub_intraday_data
except Exception:
    from utils_finnhub import fetch_finnhub_intraday_data

FINNHUB_API_KEY = "cvs634hr01qvc2mv1e00cvs634hr01qvc2mv1e0g"
ALPHA_VANTAGE_API_KEY = "LMIOGZ2DXX9HJ6OL"
FMP_API_KEY = "c0uNeGCdI4sIJ060nGu5kvk1zbYxhK7R"
POLYGON_API_KEY = "OeOiRyypszZztM1W9Hb00TF3RoNRySSX"


def fetch_from_yfinance(ticker: str) -> Optional[pd.DataFrame]:
    try:
        import yfinance as yf
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        df.rename(
            columns={
                "Datetime": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            },
            inplace=True,
        )
        return df[["timestamp", "open", "high", "low", "close", "volume"]]
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[YF INTRADAY ERROR] {e}")
        return None


def fetch_from_finnhub(ticker: str) -> Optional[pd.DataFrame]:
    try:
        return fetch_finnhub_intraday_data(ticker)
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[FINNHUB INTRADAY ERROR] {e}")
        return None


def fetch_from_alphavantage(ticker: str) -> Optional[pd.DataFrame]:
    try:
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=compact"
        )
        res = requests.get(url).json()
        data = res.get("Time Series (1min)", {})
        if not data:
            return None
        records = []
        for ts, values in data.items():
            records.append(
                {
                    "timestamp": pd.to_datetime(ts),
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": float(values.get("5. volume", 0)),
                }
            )
        df = pd.DataFrame(records).sort_values("timestamp")
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[AV INTRADAY ERROR] {e}")
        return None


def fetch_from_fmp(ticker: str) -> Optional[pd.DataFrame]:
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{ticker}?apikey={FMP_API_KEY}"
        res = requests.get(url).json()
        if not isinstance(res, list):
            return None
        df = pd.DataFrame(res)
        df.rename(columns={"date": "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        return df.sort_values("timestamp")
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[FMP INTRADAY ERROR] {e}")
        return None


def fetch_from_polygon(ticker: str) -> Optional[pd.DataFrame]:
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        start = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start}/{today}?adjusted=true&sort=asc&limit=5000&apiKey={POLYGON_API_KEY}"
        )
        res = requests.get(url).json()
        results = res.get("results", [])
        if not results:
            return None
        df = pd.DataFrame(results)
        df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        return df.sort_values("timestamp")
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[POLYGON INTRADAY ERROR] {e}")
        return None


async def fetch_from_yfinance_async(ticker: str, session: aiohttp.ClientSession) -> Optional[pd.DataFrame]:
    """Async version using Yahoo Finance chart API."""
    try:
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        )
        async with session.get(url) as resp:
            data = await resp.json()
        result = data.get("chart", {}).get("result")
        if not result:
            return None
        result = result[0]
        timestamps = result.get("timestamp", [])
        quote = result.get("indicators", {}).get("quote", [{}])[0]
        if not timestamps:
            return None
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(timestamps, unit="s"),
            "open": quote.get("open", []),
            "high": quote.get("high", []),
            "low": quote.get("low", []),
            "close": quote.get("close", []),
            "volume": quote.get("volume", []),
        })
        df.dropna(subset=["close"], inplace=True)
        return df if not df.empty else None
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[YF INTRADAY ERROR] {e}")
        return None


async def fetch_from_finnhub_async(ticker: str, session: aiohttp.ClientSession) -> Optional[pd.DataFrame]:
    try:
        end = int(time.time())
        start = end - 60 * 60 * 6
        url = (
            f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=5&from={start}&to={end}&token={FINNHUB_API_KEY}"
        )
        async with session.get(url) as resp:
            data = await resp.json()
        if data.get("s") != "ok":
            return None
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(data["t"], unit="s"),
            "open": data["o"],
            "high": data["h"],
            "low": data["l"],
            "close": data["c"],
            "volume": data["v"],
        })
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[FINNHUB INTRADAY ERROR] {e}")
        return None


async def fetch_from_alphavantage_async(ticker: str, session: aiohttp.ClientSession) -> Optional[pd.DataFrame]:
    try:
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=compact"
        )
        async with session.get(url) as resp:
            res = await resp.json()
        data = res.get("Time Series (1min)", {})
        if not data:
            return None
        records = []
        for ts, values in data.items():
            records.append(
                {
                    "timestamp": pd.to_datetime(ts),
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": float(values.get("5. volume", 0)),
                }
            )
        df = pd.DataFrame(records).sort_values("timestamp")
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[AV INTRADAY ERROR] {e}")
        return None


async def fetch_from_fmp_async(ticker: str, session: aiohttp.ClientSession) -> Optional[pd.DataFrame]:
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{ticker}?apikey={FMP_API_KEY}"
        async with session.get(url) as resp:
            res = await resp.json()
        if not isinstance(res, list):
            return None
        df = pd.DataFrame(res)
        df.rename(columns={"date": "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        return df.sort_values("timestamp")
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[FMP INTRADAY ERROR] {e}")
        return None


async def fetch_from_polygon_async(ticker: str, session: aiohttp.ClientSession) -> Optional[pd.DataFrame]:
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        start = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start}/{today}?adjusted=true&sort=asc&limit=5000&apiKey={POLYGON_API_KEY}"
        )
        async with session.get(url) as resp:
            res = await resp.json()
        results = res.get("results", [])
        if not results:
            return None
        df = pd.DataFrame(results)
        df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        return df.sort_values("timestamp")
    except Exception as e:  # pragma: no cover - best effort log only
        print(f"[POLYGON INTRADAY ERROR] {e}")
        return None


SOURCES = [
    ("Yahoo Finance", fetch_from_yfinance),
    ("Finnhub", fetch_from_finnhub),
    ("Alpha Vantage", fetch_from_alphavantage),
    ("FMP", fetch_from_fmp),
    ("Polygon", fetch_from_polygon),
]


ASYNC_SOURCES = [
    ("Yahoo Finance", fetch_from_yfinance_async),
    ("Finnhub", fetch_from_finnhub_async),
    ("Alpha Vantage", fetch_from_alphavantage_async),
    ("FMP", fetch_from_fmp_async),
    ("Polygon", fetch_from_polygon_async),
]


async def fetch_intraday_data_async(ticker: str) -> Optional[pd.DataFrame]:
    """Fetch intraday data concurrently from all sources."""
    async with aiohttp.ClientSession() as session:
        tasks = [func(ticker, session) for _, func in ASYNC_SOURCES]
        results = await asyncio.gather(*tasks)

    for (name, _), df in zip(ASYNC_SOURCES, results):
        if df is not None and not df.empty:
            print(f"✅ Success with {name}, {len(df)} records for {ticker}")
            return df
    print(f"❌ All intraday sources failed for {ticker}")
    return None


# Backward compatibility wrapper

def fetch_intraday_with_fallback(ticker: str) -> Optional[pd.DataFrame]:
    return fetch_intraday_data(ticker)


def fetch_intraday_data(ticker: str) -> Optional[pd.DataFrame]:
    """Synchronous wrapper around the async implementation."""
    return asyncio.run(fetch_intraday_data_async(ticker))
