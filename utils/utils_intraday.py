import pandas as pd
import requests
import time
import random
from datetime import datetime, timedelta
from typing import Optional

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


SOURCES = [
    ("Yahoo Finance", fetch_from_yfinance),
    ("Finnhub", fetch_from_finnhub),
    ("Alpha Vantage", fetch_from_alphavantage),
    ("FMP", fetch_from_fmp),
    ("Polygon", fetch_from_polygon),
]


def fetch_intraday_data(ticker: str) -> Optional[pd.DataFrame]:
    """Try multiple sources for intraday data."""
    for name, func in SOURCES:
        print(f"[TRYING] {name} intraday for {ticker}...")
        df = func(ticker)
        if df is not None and not df.empty:
            print(f"✅ Success with {name}, {len(df)} records for {ticker}")
            return df
        time.sleep(1.5 + random.uniform(0, 1.5))
    print(f"❌ All intraday sources failed for {ticker}")
    return None


# Backward compatibility wrapper

def fetch_intraday_with_fallback(ticker: str) -> Optional[pd.DataFrame]:
    return fetch_intraday_data(ticker)
