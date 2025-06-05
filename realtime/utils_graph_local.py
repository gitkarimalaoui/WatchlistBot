
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from realtime.build_intraday_candles import build_candles

def plot_candles(candles, ticker):
    if candles.empty:
        print(f"No candles to plot for {ticker}.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    for i in range(len(candles)):
        time = candles.loc[i, "timestamp"]
        o = candles.loc[i, "o"]
        h = candles.loc[i, "h"]
        l = candles.loc[i, "l"]
        c = candles.loc[i, "c"]
        color = "green" if c >= o else "red"
        ax.plot([time, time], [l, h], color=color)
        ax.plot([time, time], [o, c], color=color, linewidth=5)

    ax.set_title(f"{ticker} - Candle Chart")
    ax.set_ylabel("Price ($)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

def generer_graphique_local(ticker):
    try:
        candles = build_candles(ticker)
        if candles.empty:
            print(f"[!] Aucune donnée de candle pour {ticker}")
            return
        plot_candles(candles, ticker)
    except Exception as e:
        print(f"[❌] Erreur graphique pour {ticker} : {e}")
