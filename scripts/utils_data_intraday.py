
import yfinance as yf
import requests
from datetime import datetime, timedelta
import pandas as pd
import time

def get_intraday_finnhub(ticker, api_key, nb_minutes=360):
    try:
        end = int(time.time())
        start = end - nb_minutes * 60
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=1&from={start}&to={end}&token={api_key}"
        r = requests.get(url)
        d = r.json()
        if d.get("s") == "ok":
            df = pd.DataFrame({
                "Datetime": [datetime.fromtimestamp(ts) for ts in d["t"]],
                "Open": d["o"],
                "High": d["h"],
                "Low": d["l"],
                "Close": d["c"],
                "Volume": d["v"]
            })
            df['source'] = 'finnhub'
            return df
    except Exception as e:
        print(f"[Finnhub Intraday Error] {ticker}: {e}")
    return None

def get_intraday_yahoo_scraping(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        r = requests.get(url, timeout=5)
        d = r.json()
        result = d["chart"]["result"][0]
        timestamps = result["timestamp"]
        indicators = result["indicators"]["quote"][0]
        df = pd.DataFrame({
            "Datetime": [datetime.fromtimestamp(t) for t in timestamps],
            "Open": indicators["open"],
            "High": indicators["high"],
            "Low": indicators["low"],
            "Close": indicators["close"],
            "Volume": indicators["volume"]
        })
        df['source'] = 'yahoo_scraping'
        return df
    except Exception as e:
        print(f"[Yahoo Intraday Error] {ticker}: {e}")
    return None

def charger_intraday_intelligent(ticker, api_key):
    df = get_intraday_finnhub(ticker, api_key)
    if df is not None and not df.empty:
        return df

    df = get_intraday_yahoo_scraping(ticker)
    return df
