import os
import sys
import time
import sqlite3
import pandas as pd
import traceback


def main() -> None:
    # Ensure UTF-8 console output for emoji support
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    else:
        sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1, errors="replace")

    # ─── Configuration des chemins ─────────────────────────────────────────────
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    UTILS = os.path.join(ROOT_DIR, "utils")
    DATA = os.path.join(ROOT_DIR, "data")

    if UTILS not in sys.path:
        sys.path.insert(0, UTILS)

    # ─── Import sécurisé de la fonction de collecte ───────────────────────────
    try:
        from utils_yf_historical import fetch_historical_with_fallback
    except ImportError as e:
        print(f"[IMPORT ERROR] Impossible d'importer utils_yf_historical: {e}")
        sys.exit(1)

    # ─── Chargement de la watchlist ───────────────────────────────────────────
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

    # ─── Table cible ──────────────────────────────────────────────────────────
    cur = conn.execute("PRAGMA table_info(historical_data)")
    existing_columns = [row[1] for row in cur.fetchall()]

    if not existing_columns:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS historical_data (
            ticker TEXT,
            timestamp TEXT,
            close REAL,
            PRIMARY KEY (ticker, timestamp)
        )
        """
        )
        existing_columns = ["ticker", "timestamp", "close"]

    time_column = "timestamp" if "timestamp" in existing_columns else "date"

    # ─── Collecte et insertion ───────────────────────────────────────────────
    for i, ticker in enumerate(tickers, start=1):
        print(f"🔄 [{i}/{len(tickers)}] {ticker}")
        try:
            df = fetch_historical_with_fallback(ticker)
        except Exception as e:  # pragma: no cover - unexpected failure
            print(f"[FETCH ERROR] {ticker}: {e}")
            traceback.print_exc()
            continue

        if df is None or df.empty:
            print(f"⛔ Aucun historique pour {ticker}")
            continue

        df["ticker"] = ticker

        # Only keep timestamp and close columns to match the table schema
        required_cols = {"timestamp", "close"}
        if not required_cols.issubset(df.columns):
            print(f"[WARN] Colonnes manquantes pour {ticker}, saute : {df.columns.tolist()}")
            continue

        if time_column != "timestamp":
            df.rename(columns={"timestamp": time_column}, inplace=True)

        df = df[[time_column, "close", "ticker"]]

        try:
            df.to_sql("historical_data", conn, if_exists="append", index=False)
            print(f"✅ Données insérées pour {ticker}")
        except Exception as e:
            print(f"[SQL ERROR] Insertion échouée pour {ticker} : {e}")
            traceback.print_exc()

        time.sleep(1.5)  # Évite le rate limiting Yahoo

    conn.commit()
    conn.close()
    print("🎉 Collecte terminée.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # pragma: no cover - unexpected failure
        print(f"[FATAL] {e}")
        traceback.print_exc()
        sys.exit(1)
