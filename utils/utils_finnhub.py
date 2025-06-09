import requests
import pandas as pd
import os
import time
from config.config_manager import _load_dotenv

# API key is now read strictly from the environment
_load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def _missing_key() -> bool:
    return (
        not FINNHUB_API_KEY
        or "your_real_api_key_here" in FINNHUB_API_KEY
        or "your_default_api_key_here" in FINNHUB_API_KEY
    )

def fetch_finnhub_historical_data(ticker: str) -> pd.DataFrame:
    if _missing_key():
        print("[Finnhub ERROR] API key missing")
        return None
    end = int(time.time())
    start = end - 60 * 60 * 24 * 180  # 6 mois
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start}&to={end}&token={FINNHUB_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("s") != "ok":
            print(f"[Finnhub Historical] No data for {ticker}")
            return None

        df = pd.DataFrame({
            "timestamp": pd.to_datetime(data["t"], unit="s"),
            "open": data["o"],
            "high": data["h"],
            "low": data["l"],
            "close": data["c"],
            "volume": data["v"]
        })
        return df
    except Exception as e:
        print(f"[Finnhub Historical ERROR] {ticker}: {e}")
        return None


def fetch_finnhub_intraday_data(ticker: str) -> pd.DataFrame:
    if _missing_key():
        print("[Finnhub ERROR] API key missing")
        return None
    end = int(time.time())
    start = end - 60 * 60 * 6  # 6 heures
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=5&from={start}&to={end}&token={FINNHUB_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("s") != "ok":
            print(f"[Finnhub Intraday] No data for {ticker}")
            return None

        df = pd.DataFrame({
            "timestamp": pd.to_datetime(data["t"], unit="s"),
            "open": data["o"],
            "high": data["h"],
            "low": data["l"],
            "close": data["c"],
            "volume": data["v"]
        })
        return df
    except Exception as e:
        print(f"[Finnhub Intraday ERROR] {ticker}: {e}")
        return None
