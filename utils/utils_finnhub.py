
import requests
import pandas as pd
import os
from datetime import datetime
import time

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "cvs634hr01qvc2mv1e00cvs634hr01qvc2mv1e0g")

def fetch_finnhub_historical_data(ticker: str) -> pd.DataFrame:
    end = int(time.time())
    start = end - 60 * 60 * 24 * 180  # 6 mois
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start}&to={end}&token={FINNHUB_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("s") != "ok":
            print(f"[Finnhub Historical] No data for {ticker}")
            return None

        df = pd.DataFrame({
            "Date": pd.to_datetime(data["t"], unit="s"),
            "Open": data["o"],
            "High": data["h"],
            "Low": data["l"],
            "Close": data["c"],
            "Volume": data["v"]
        })
        return df
    except Exception as e:
        print(f"[Finnhub Historical ERROR] {ticker}: {e}")
        return None


def fetch_finnhub_intraday_data(ticker: str) -> pd.DataFrame:
    end = int(time.time())
    start = end - 60 * 60 * 6  # 6 heures
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=5&from={start}&to={end}&token={FINNHUB_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("s") != "ok":
            print(f"[Finnhub Intraday] No data for {ticker}")
            return None

        df = pd.DataFrame({
            "Datetime": pd.to_datetime(data["t"], unit="s"),
            "Open": data["o"],
            "High": data["h"],
            "Low": data["l"],
            "Close": data["c"],
            "Volume": data["v"]
        })
        return df
    except Exception as e:
        print(f"[Finnhub Intraday ERROR] {ticker}: {e}")
        return None
