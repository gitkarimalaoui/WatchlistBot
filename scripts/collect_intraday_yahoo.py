import os
import pandas as pd
import yfinance as yf
from datetime import datetime
import sqlite3

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_DIR, "data", "trades.db")

def get_watchlist_tickers():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT ticker FROM watchlist", conn)
    conn.close()
    return df['ticker'].dropna().unique().tolist()

def save_intraday_to_db(df, ticker):
    if df.empty:
        return
    df = df.reset_index()
    df['ticker'] = ticker
    df.rename(columns={"Datetime": "timestamp"}, inplace=True)
    df['timestamp'] = df['timestamp'].astype(str)
    
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("intraday_data", conn, if_exists="append", index=False)
    conn.close()

def fetch_and_store_intraday_yahoo(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False)
        if df.empty:
            print(f"[WARN] {ticker} → Intraday 1min vide.")
            return False
        save_intraday_to_db(df, ticker)
        print(f"[OK] {ticker} → Données 1min enregistrées dans la base.")
        return True
    except Exception as e:
        print(f"[ERROR] {ticker} → {e}")
        return False

def main():
    tickers = get_watchlist_tickers()
    print(f"[INFO] {len(tickers)} tickers trouvés.")
    for ticker in tickers:
        fetch_and_store_intraday_yahoo(ticker)

if __name__ == "__main__":
    main()
