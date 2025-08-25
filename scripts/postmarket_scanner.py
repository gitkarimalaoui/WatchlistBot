
import yfinance as yf
from datetime import datetime
import pandas as pd

def scan_postmarket_watchlist(threshold_percent=50, min_volume=500_000, max_float_shares=200_000_000):
    now = datetime.now()
    tickers = ['TSLA', 'AMD', 'NVDA', 'SPCE', 'LYFT']  # Exemple – à remplacer par liste dynamique
    results = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False)
            if df.empty:
                continue

            open_price = df["Open"].iloc[0]
            last_price = df["Close"].iloc[-1]
            change = ((last_price - open_price) / open_price) * 100
            volume = df["Volume"].sum()

            if change >= threshold_percent and volume >= min_volume:
                results.append({
                    "symbol": ticker,
                    "percent_change": round(change, 2),
                    "volume": int(volume),
                    "timestamp": now.isoformat()
                })
        except Exception as e:
            print(f"[SCAN ERROR] {ticker}: {e}")
            continue

    return results
