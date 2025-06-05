import os
import pandas as pd
import yfinance as yf
from datetime import datetime
import sqlite3

# Définition des chemins
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_DIR, "data", "trades.db")

# Connexion à la base
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Création de la table intraday_data si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS intraday_data (
    timestamp TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    ticker TEXT
)
""")
conn.commit()


def get_watchlist_tickers():
    df = pd.read_sql_query("SELECT DISTINCT ticker FROM watchlist", conn)
    return df['ticker'].dropna().unique().tolist()


def fetch_and_store_intraday_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty:
            print(f"[WARN] {ticker} → Intraday 1min vide.")
            return False

        df.reset_index(inplace=True)
        df['ticker'] = ticker
        df.rename(columns={
            'Datetime': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)

        df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'ticker']].to_sql(
            "intraday_data", conn, if_exists="append", index=False
        )
        print(f"[OK] {ticker} → Intraday insérés en DB.")
        return True
    except Exception as e:
        print(f"[ERROR] {ticker} → {e}")
        return False


def main():
    tickers = get_watchlist_tickers()
    print(f"[INFO] {len(tickers)} tickers trouvés dans la watchlist.")
    for tic in tickers:
        fetch_and_store_intraday_data(tic)


if __name__ == "__main__":
    main()
    conn.close()
