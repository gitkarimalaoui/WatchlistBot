
import os
import sqlite3
import yfinance as yf
import pandas as pd

DB_PATH = os.path.join("..", "data", "trades.db")
EXPORT_DIR = os.path.join("..", "data", "historical")
os.makedirs(EXPORT_DIR, exist_ok=True)

def get_tickers_from_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT ticker FROM watchlist", conn)
    conn.close()
    return df["ticker"].dropna().unique()

def download_and_save(ticker):
    filename = os.path.join(EXPORT_DIR, f"{ticker.upper()}.csv")
    if os.path.exists(filename):
        print(f"[SKIP] {ticker} déjà présent.")
        return
    try:
        print(f"[...] Téléchargement {ticker}")
        data = yf.download(ticker, period="2y", interval="1d")
        if data.empty:
            print(f"[WARN] {ticker} → Aucune donnée téléchargée.")
            return
        data.to_csv(filename)
        print(f"[OK] {ticker} enregistré.")
    except Exception as e:
        print(f"[ERREUR] {ticker} → {e}")

def main():
    tickers = get_tickers_from_db()
    print(f"[INFO] {len(tickers)} tickers à traiter.")
    for ticker in tickers:
        download_and_save(ticker)

if __name__ == "__main__":
    main()
