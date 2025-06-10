from pathlib import Path
import sys
import pandas as pd
import yfinance as yf
import logging
import sqlite3

from utils.db_historical import insert_historical
from utils.db_intraday import insert_intraday

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Vérifier que yfinance est installé
try:
    import yfinance as yf  # noqa: F401
except ImportError:
    logging.error("Le module 'yfinance' n'est pas installé. Installez-le avec: pip install yfinance")
    sys.exit(1)

# Définir le chemin racine du projet (un niveau au-dessus de 'scripts')
SCRIPT_PATH = Path(__file__).resolve()
ROOT_DIR = SCRIPT_PATH.parents[1] if len(SCRIPT_PATH.parents) >= 2 else SCRIPT_PATH.parent

# Répertoires de sortie
HIST_DIR = ROOT_DIR / "scripts" / "data" / "historical"
INTRADAY_DIR = ROOT_DIR / "scripts" / "data" / "intraday"
HIST_DIR.mkdir(parents=True, exist_ok=True)
INTRADAY_DIR.mkdir(parents=True, exist_ok=True)

# Charger la watchlist depuis la base de données
DB_PATH = ROOT_DIR / "data" / "trades.db"
conn = sqlite3.connect(DB_PATH)
try:
    df_watchlist = pd.read_sql_query("SELECT DISTINCT ticker FROM watchlist", conn)
finally:
    conn.close()

tickers = df_watchlist["ticker"].dropna().str.upper().tolist()
logging.info(f"{len(tickers)} tickers chargés depuis la DB: {tickers}")

# Colonnes cibles pour uniformité
TARGET_COLS = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# Fonction de téléchargement et insertion en base
def fetch_and_store(symbol: str, period: str, interval: str, kind: str) -> None:
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, threads=False)
        if df.empty:
            logging.warning(f"Aucune donnée pour {symbol} (period={period}, interval={interval})")
            return
        df.index.name = 'Date'
        df_reset = df.reset_index()
        df_reset['Date'] = pd.to_datetime(df_reset['Date'], utc=True).dt.tz_localize(None)
        df_reset['Date'] = df_reset['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'Adj Close' not in df_reset.columns and 'Close' in df_reset.columns:
            df_reset['Adj Close'] = df_reset['Close']
        for col in TARGET_COLS:
            if col not in df_reset.columns:
                df_reset[col] = pd.NA
        df_clean = df_reset[TARGET_COLS]
        if kind == 'historical':
            insert_historical(symbol, df_clean.rename(columns={'Date': 'date', 'Adj Close': 'adj_close'}))
        else:
            df_intraday = df_clean.rename(columns={
                'Date': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            insert_intraday(symbol, df_intraday)
        logging.info(f"Données {kind} insérées pour {symbol}")
    except Exception as e:
        logging.error(f"Erreur lors du fetch {symbol} ({period},{interval}): {e}")

# Execution principale
for symbol in tickers:
    logging.info(f"--- Traitement de {symbol} ---")
    fetch_and_store(symbol, period="2y", interval="1d", kind="historical")
    fetch_and_store(symbol, period="7d", interval="1m", kind="intraday")
logging.info("Traitement terminé.")
