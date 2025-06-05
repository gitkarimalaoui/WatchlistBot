import os
import pandas as pd
from datetime import datetime

SAVE_DIR = "data/ticks"

def build_candles(ticker, interval="1min"):
    path = os.path.join(SAVE_DIR, f"{ticker}.csv")
    if not os.path.exists(path):
        print(f"No tick data available for {ticker}.")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df.set_index("timestamp", inplace=True)

    # Only today's data
    today = pd.Timestamp.now().normalize()
    df = df[df.index >= today]

    rule = "1min" if interval == "1min" else "5min"
    candles = df.resample(rule).agg({
        "o": "first",
        "h": "max",
        "l": "min",
        "c": "last",
        "v": "sum" if "v" in df.columns else "count"
    }).dropna()
    candles.reset_index(inplace=True)
    return candles