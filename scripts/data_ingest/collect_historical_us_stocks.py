from pathlib import Path
import sys
import pandas as pd
import yfinance as yf
import logging

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

# Charger la watchlist
WATCHLIST_FILE = ROOT_DIR / "scripts" / "tickers_watchlist_US_only.txt"
if not WATCHLIST_FILE.exists():
    logging.error(f"Fichier watchlist non trouvé: {WATCHLIST_FILE}")
    sys.exit(1)
with WATCHLIST_FILE.open('r', encoding='utf-8') as f:
    tickers = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
logging.info(f"{len(tickers)} tickers chargés: {tickers}")

# Colonnes cibles pour uniformité
TARGET_COLS = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# Fonction de téléchargement et sauvegarde uniformisée
def fetch_and_save(symbol: str, period: str, interval: str, out_dir: Path, suffix: str):
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, threads=False)
        if df.empty:
            logging.warning(f"Aucune donnée pour {symbol} (period={period}, interval={interval})")
            return
        # Nommer l'index pour garantir la colonne Date
        df.index.name = 'Date'
        # Reset index pour transformer l'index en colonne Date
        df_reset = df.reset_index()
        # Formater la colonne Date et supprimer timezone
        df_reset['Date'] = pd.to_datetime(df_reset['Date'], utc=True).dt.tz_localize(None)
        df_reset['Date'] = df_reset['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Compléter ou renommer les colonnes manquantes
        if 'Adj Close' not in df_reset.columns and 'Close' in df_reset.columns:
            df_reset['Adj Close'] = df_reset['Close']
        # Assurer toutes les colonnes TARGET_COLS
        for col in TARGET_COLS:
            if col not in df_reset.columns:
                df_reset[col] = pd.NA
        # Sélection et ré-ordonnancement
        df_clean = df_reset[TARGET_COLS]
        # Chemin de sortie
        out_file = out_dir / f"{symbol.replace('.', '_')}_{suffix}.csv"
        df_clean.to_csv(out_file, index=False)
        logging.info(f"Données {suffix} pour {symbol} enregistrées: {out_file}")
    except Exception as e:
        logging.error(f"Erreur lors du fetch {symbol} ({period},{interval}): {e}")

# Execution principale
for symbol in tickers:
    logging.info(f"--- Traitement de {symbol} ---")
    fetch_and_save(symbol, period="2y", interval="1d", out_dir=HIST_DIR, suffix="2y_daily")
    fetch_and_save(symbol, period="7d", interval="1m", out_dir=INTRADAY_DIR, suffix="7d_1m")
logging.info("Traitement terminé.")
