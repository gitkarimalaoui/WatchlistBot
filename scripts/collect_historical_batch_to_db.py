
import os
import sys
import time
import sqlite3
import pandas as pd

# Ensure UTF-8 console output for emoji support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

# ─── Configuration des chemins ─────────────────────────────────────────────────
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UTILS = os.path.join(ROOT_DIR, "utils")
DATA = os.path.join(ROOT_DIR, "data")

if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

# ─── Import sécurisé de la fonction de collecte ────────────────────────────────
try:
    from utils_yf_historical import fetch_historical_with_fallback
except ImportError as e:
    print(f"[IMPORT ERROR] Impossible d'importer utils_yf_historical: {e}")
    sys.exit(1)

# ─── Chargement de la watchlist ────────────────────────────────────────────────
watchlist_path = os.path.join(DATA, "trades.db")
conn = sqlite3.connect(watchlist_path)

try:
    df_watchlist = pd.read_sql_query("SELECT DISTINCT ticker FROM watchlist", conn)
except Exception as e:
    print(f"[DB ERROR] Impossible de lire la watchlist : {e}")
    conn.close()
    sys.exit(1)

tickers = df_watchlist["ticker"].dropna().unique()
print(f"[INFO] {len(tickers)} tickers à traiter.")

# ─── Table cible ───────────────────────────────────────────────────────────────
conn.execute("""
CREATE TABLE IF NOT EXISTS historical_data (
    ticker TEXT,
    timestamp TEXT,
    close REAL,
    PRIMARY KEY (ticker, timestamp)
)
""")

# ─── Collecte et insertion ─────────────────────────────────────────────────────
for i, ticker in enumerate(tickers, start=1):
    print(f"🔄 [{i}/{len(tickers)}] {ticker}")
    df = fetch_historical_with_fallback(ticker)
    if df is None or df.empty:
        print(f"⛔ Aucun historique pour {ticker}")
        continue

    df["ticker"] = ticker
    try:
        df.to_sql("historical_data", conn, if_exists="append", index=False)
        print(f"✅ Données insérées pour {ticker}")
    except Exception as e:
        print(f"[SQL ERROR] Insertion échouée pour {ticker} : {e}")

    time.sleep(1.5)  # Évite le rate limiting Yahoo

conn.commit()
conn.close()
print("🎉 Collecte terminée.")
