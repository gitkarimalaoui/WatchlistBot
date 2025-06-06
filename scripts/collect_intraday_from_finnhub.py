
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

from utils_finnhub import get_candle_data
from utils import load_last_timestamp

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "trades.db"
RETENTION_DAYS = int(os.getenv("INTRADAY_KEEP_DAYS", "5"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intraday_data (
            ticker TEXT,
            timestamp TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER
        )
    ''')
    conn.commit()
    return conn

def get_tickers_from_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT ticker FROM watchlist", conn)
    conn.close()
    return df['ticker'].tolist()

def save_intraday_to_db(ticker, df, conn):
    if df.empty:
        print(f"[SKIP] {ticker} → Intraday vide.")
        return
    df['ticker'] = ticker
    df['timestamp'] = pd.to_datetime(df['t'], unit='s')
    df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
    df = df[['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.to_sql("intraday_data", conn, if_exists="append", index=False)
    print(f"[OK] {ticker} intraday inséré ({len(df)} lignes)")

def prune_old_data(conn):
    """Remove intraday rows older than ``RETENTION_DAYS``."""
    threshold = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    conn.execute(
        "DELETE FROM intraday_data WHERE timestamp < ?",
        (threshold.isoformat(),),
    )
    conn.commit()

def collect_intraday_for_all():
    conn = init_db()
    tickers = get_tickers_from_db()
    print(f"[INFO] {len(tickers)} tickers à analyser.")
    for ticker in tickers:
        try:
            last_ts = load_last_timestamp(ticker)
            if last_ts is None:
                start = int((datetime.utcnow() - timedelta(days=RETENTION_DAYS)).timestamp())
            else:
                start = int(last_ts.timestamp())
            end = int(datetime.utcnow().timestamp())

            df = get_candle_data(ticker, resolution='1', _from=start, to=end)
            df = pd.DataFrame(df)
            if not df.empty and 't' in df.columns:
                save_intraday_to_db(ticker, df, conn)
            else:
                print(f"[WARN] {ticker} → Données intraday manquantes ou incomplètes.")
        except Exception as e:
            print(f"[ERROR] {ticker} → {e}")

    prune_old_data(conn)
    conn.close()

if __name__ == "__main__":
    collect_intraday_for_all()
