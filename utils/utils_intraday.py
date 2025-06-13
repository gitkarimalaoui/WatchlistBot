import os
import pandas as pd
import requests
import time
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import asyncio
from utils.async_utils import async_to_thread
from config.config_manager import _load_dotenv, config_manager
try:
    from .utils_finnhub import fetch_finnhub_intraday_data
except Exception:
    from utils_finnhub import fetch_finnhub_intraday_data

_load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY") or config_manager.get("finnhub_api")

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# Logging configuration
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)
intraday_logger = logging.getLogger("intraday_fetch")
if not intraday_logger.handlers:
    intraday_logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    fh = logging.FileHandler(LOG_DIR / "intraday_fetch.log", encoding="utf-8")
    fh.setFormatter(formatter)
    intraday_logger.addHandler(fh)


def fetch_from_yfinance(ticker: str) -> Optional[pd.DataFrame]:
    start = time.time()
    intraday_logger.info("Fetching %s from yfinance", ticker)
    try:
        import yfinance as yf
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty:
            intraday_logger.warning("%s → empty DataFrame from yfinance", ticker)
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
        intraday_logger.info(
            "Success fetching %s from yfinance in %.2fs",
            ticker,
            time.time() - start,
        )
        return df[["timestamp", "open", "high", "low", "close", "volume"]]
    except Exception as e:  # pragma: no cover - best effort log only
        intraday_logger.error("Failed yfinance fetch for %s: %s", ticker, e, exc_info=True)
        return None

async def fetch_from_yfinance_async(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_yfinance, ticker)


def fetch_from_finnhub(ticker: str) -> Optional[pd.DataFrame]:
    start = time.time()
    intraday_logger.info("Fetching %s from finnhub", ticker)
    try:
        df = fetch_finnhub_intraday_data(ticker)
        if df is None or df.empty:
            intraday_logger.warning("%s → empty DataFrame from finnhub", ticker)
            return None
        intraday_logger.info(
            "Success fetching %s from finnhub in %.2fs",
            ticker,
            time.time() - start,
        )
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        intraday_logger.error("Failed finnhub fetch for %s: %s", ticker, e, exc_info=True)
        return None

async def fetch_from_finnhub_async(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_finnhub, ticker)


def fetch_from_alphavantage(ticker: str) -> Optional[pd.DataFrame]:
    start = time.time()
    intraday_logger.info("Fetching %s from alphavantage", ticker)
    try:
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=compact"
        )
        res = requests.get(url).json()
        data = res.get("Time Series (1min)", {})
        if not data:
            intraday_logger.warning("%s → empty data from alphavantage", ticker)
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
        intraday_logger.info(
            "Success fetching %s from alphavantage in %.2fs",
            ticker,
            time.time() - start,
        )
        return df
    except Exception as e:  # pragma: no cover - best effort log only
        intraday_logger.error(
            "Failed alphavantage fetch for %s: %s", ticker, e, exc_info=True
        )
        return None

async def fetch_from_alphavantage_async(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_alphavantage, ticker)


def fetch_from_fmp(ticker: str) -> Optional[pd.DataFrame]:
    start = time.time()
    intraday_logger.info("Fetching %s from fmp", ticker)
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{ticker}?apikey={FMP_API_KEY}"
        res = requests.get(url).json()
        if not isinstance(res, list):
            intraday_logger.warning("%s → empty data from fmp", ticker)
            return None
        df = pd.DataFrame(res)
        df.rename(columns={"date": "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        intraday_logger.info(
            "Success fetching %s from fmp in %.2fs",
            ticker,
            time.time() - start,
        )
        return df.sort_values("timestamp")
    except Exception as e:  # pragma: no cover - best effort log only
        intraday_logger.error("Failed fmp fetch for %s: %s", ticker, e, exc_info=True)
        return None

async def fetch_from_fmp_async(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_fmp, ticker)


def fetch_from_polygon(ticker: str) -> Optional[pd.DataFrame]:
    start_t = time.time()
    intraday_logger.info("Fetching %s from polygon", ticker)
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        start = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start}/{today}?adjusted=true&sort=asc&limit=5000&apiKey={POLYGON_API_KEY}"
        )
        res = requests.get(url).json()
        results = res.get("results", [])
        if not results:
            intraday_logger.warning("%s → empty data from polygon", ticker)
            return None
        df = pd.DataFrame(results)
        df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        intraday_logger.info(
            "Success fetching %s from polygon in %.2fs",
            ticker,
            time.time() - start_t,
        )
        return df.sort_values("timestamp")
    except Exception as e:  # pragma: no cover - best effort log only
        intraday_logger.error("Failed polygon fetch for %s: %s", ticker, e, exc_info=True)
        return None

async def fetch_from_polygon_async(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_polygon, ticker)


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


def fetch_intraday_data(ticker: str) -> Optional[pd.DataFrame]:
    """Try multiple sources for intraday data using asyncio."""
    return asyncio.run(fetch_intraday_data_async(ticker))


import inspect


async def fetch_intraday_data_async(ticker: str) -> Optional[pd.DataFrame]:
    tasks = {}
    for name, func in ASYNC_SOURCES:
        try:
            params = inspect.signature(func).parameters
            if len(params) > 1:
                task = asyncio.create_task(func(ticker, None))
            else:
                task = asyncio.create_task(func(ticker))
            tasks[name] = task
        except Exception:
            tasks[name] = asyncio.create_task(func(ticker))
    results = {}
    for name, task in tasks.items():
        try:
            results[name] = await task
        except Exception as e:  # pragma: no cover - best effort log only
            print(f"[{name} async ERROR] {e}")
            results[name] = None
    for name, _ in ASYNC_SOURCES:
        df = results.get(name)
        if df is not None and not df.empty:
            print(f"✅ Success with {name}, {len(df)} records for {ticker}")
            return df
    print(f"❌ All intraday sources failed for {ticker}")
    return None


# Backward compatibility wrapper
def fetch_intraday_with_fallback(ticker: str) -> Optional[pd.DataFrame]:
    return fetch_intraday_data(ticker)


# ---------------------------------------------------------------------------
# Async versions
# ---------------------------------------------------------------------------

async def async_fetch_from_yfinance(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_yfinance, ticker)


async def async_fetch_from_finnhub(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_finnhub, ticker)


async def async_fetch_from_alphavantage(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_alphavantage, ticker)


async def async_fetch_from_fmp(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_fmp, ticker)


async def async_fetch_from_polygon(ticker: str) -> Optional[pd.DataFrame]:
    return await async_to_thread(fetch_from_polygon, ticker)


ASYNC_SOURCES = [
    ("Yahoo Finance", async_fetch_from_yfinance),
    ("Finnhub", async_fetch_from_finnhub),
    ("Alpha Vantage", async_fetch_from_alphavantage),
    ("FMP", async_fetch_from_fmp),
    ("Polygon", async_fetch_from_polygon),
]


async def async_fetch_intraday_data(ticker: str) -> Optional[pd.DataFrame]:
    """Asynchronously try multiple sources for intraday data."""
    for name, func in ASYNC_SOURCES:
        print(f"[TRYING] {name} intraday for {ticker}...")
        df = await func(ticker)
        if df is not None and not df.empty:
            print(f"✅ Success with {name}, {len(df)} records for {ticker}")
            return df
        await asyncio.sleep(1.5 + random.uniform(0, 1.5))
    print(f"❌ All intraday sources failed for {ticker}")
    return None


async def async_fetch_intraday_with_fallback(ticker: str) -> Optional[pd.DataFrame]:
    return await async_fetch_intraday_data(ticker)