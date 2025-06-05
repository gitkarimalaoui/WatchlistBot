
import yfinance as yf
import requests
from datetime import datetime, timedelta
import pandas as pd
import time

def get_historical_yf(ticker, period='2y', interval='1d'):
    try:
        df = yf.download(ticker, period=period, interval=interval)
        if not df.empty:
            df.reset_index(inplace=True)
            df['source'] = 'yfinance'
            return df
    except Exception as e:
        print(f"[YF Error] {ticker}: {e}")
    return None

def get_historical_finnhub(ticker, api_key, nb_days=730):
    try:
        end = int(time.time())
        start = int((datetime.now() - timedelta(days=nb_days)).timestamp())
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start}&to={end}&token={api_key}"
        r = requests.get(url)
        d = r.json()
        if d.get("s") == "ok":
            df = pd.DataFrame({
                "Date": [datetime.fromtimestamp(ts) for ts in d["t"]],
                "Open": d["o"],
                "High": d["h"],
                "Low": d["l"],
                "Close": d["c"],
                "Volume": d["v"]
            })
            df['source'] = 'finnhub'
            return df
    except Exception as e:
        print(f"[Finnhub Error] {ticker}: {e}")
    return None

def get_historical_yahoo_scraping(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2y"
        r = requests.get(url, timeout=5)
        d = r.json()
        result = d["chart"]["result"][0]
        timestamps = result["timestamp"]
        indicators = result["indicators"]["quote"][0]
        df = pd.DataFrame({
            "Date": [datetime.fromtimestamp(t) for t in timestamps],
            "Open": indicators["open"],
            "High": indicators["high"],
            "Low": indicators["low"],
            "Close": indicators["close"],
            "Volume": indicators["volume"]
        })
        df['source'] = 'yahoo_scraping'
        return df
    except Exception as e:
        print(f"[Yahoo Scraping Error] {ticker}: {e}")
    return None

def charger_historique_intelligent(ticker, api_key):
    df = get_historical_yf(ticker)
    if df is not None and not df.empty:
        return df

    df = get_historical_finnhub(ticker, api_key)
    if df is not None and not df.empty:
        return df

    df = get_historical_yahoo_scraping(ticker)
    return df
