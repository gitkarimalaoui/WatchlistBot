import os
import sys
import logging
from pathlib import Path

# ─── Early logger setup to capture import failures ───────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
UTILS = ROOT_DIR / "utils"
DATA = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_path = LOG_DIR / "historical_batch.log"
logger = logging.getLogger("historical_batch")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # Stream logs to stderr so subprocess callers can capture errors
    logger.addHandler(logging.StreamHandler(sys.stderr))

if str(UTILS) not in sys.path:
    sys.path.insert(0, str(UTILS))

try:
    import time
    import sqlite3
    import pandas as pd
except ImportError as e:  # pragma: no cover - early dependency failure
    logger.error("Module import failed: %s", e)
    sys.exit(1)


def main() -> None:
    # Ensure UTF-8 console output for emoji support
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    else:
        sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1, errors="replace")

    # ─── Configuration des chemins ─────────────────────────────────────────────

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
    logger.info("%d tickers à traiter", len(tickers))

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
        logger.info("Start collecting data for ticker: %s", ticker)
        start_time = time.time()
        try:
            df = fetch_historical_with_fallback(ticker)
            duration = time.time() - start_time
            logger.info("Fetched %s in %.2fs", ticker, duration)
        except Exception as e:  # pragma: no cover - unexpected failure
            logger.error("Failed to collect %s: %s", ticker, e, exc_info=True)
            continue

        if df is None or df.empty:
            logger.warning("%s → Aucun historique", ticker)
            continue

        df["ticker"] = ticker

        # Only keep timestamp and close columns to match the table schema
        required_cols = {"timestamp", "close"}
        if not required_cols.issubset(df.columns):
            logger.warning("Colonnes manquantes pour %s : %s", ticker, df.columns.tolist())
            continue

        if time_column != "timestamp":
            df.rename(columns={"timestamp": time_column}, inplace=True)

        df = df[[time_column, "close", "ticker"]]

        try:
            df.to_sql("historical_data", conn, if_exists="append", index=False)
            logger.info("Successfully saved data for ticker: %s", ticker)
        except Exception as e:
            logger.error("Insertion échouée pour %s: %s", ticker, e, exc_info=True)

        time.sleep(1.5)  # Évite le rate limiting Yahoo

    conn.commit()
    conn.close()
    logger.info("Collecte terminée")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # pragma: no cover - unexpected failure
        logging.getLogger("historical_batch").error("Fatal error: %s", e, exc_info=True)
        sys.exit(1)
