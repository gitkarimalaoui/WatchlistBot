import os
import time
import json
import requests
import pandas as pd
import sys

# Ensure UTF-8 console output for emoji support
sys.stdout.reconfigure(encoding="utf-8")
from datetime import datetime

# Finnhub token loaded from environment variable
FINNHUB_TOKEN = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1/quote"
SAVE_DIR = "data/ticks"
# Interval between API requests in seconds (reduced for finer granularity)
INTERVAL = 5

TICKERS = ["AAPL", "TSLA", "NVDA", "SPPL", "SONN"]  # You can customize

os.makedirs(SAVE_DIR, exist_ok=True)

def get_quote(ticker):
    url = f"{BASE_URL}?symbol={ticker}&token={FINNHUB_TOKEN}"
    try:
        r = requests.get(url)
        data = r.json()
        data["timestamp"] = int(time.time())
        return data
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def append_tick(ticker, data):
    path = os.path.join(SAVE_DIR, f"{ticker}.csv")
    df = pd.DataFrame([data])
    if os.path.exists(path):
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)

if __name__ == "__main__":
    print("🚀 Starting real-time tick collector...")
    while True:
        for ticker in TICKERS:
            quote = get_quote(ticker)
            if quote and "c" in quote:
                append_tick(ticker, quote)
                print(f"✅ {ticker} at {quote['c']} saved.")
            else:
                print(f"❌ No data for {ticker}.")
        time.sleep(INTERVAL)