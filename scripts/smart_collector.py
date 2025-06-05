
import yfinance as yf
from utils_finnhub import fetch_finnhub_historical_data
from utils_yf_historical import fetch_yf_historical_data
from data.scraper_fallback import scraper_penny_stock_backup

def collect_historical_data_smart(ticker: str):
    try:
        df = fetch_yf_historical_data(ticker)
        if df is not None and not df.empty:
            print(f"[YF] Données récupérées pour {ticker}")
            return df
    except Exception as e:
        print(f"[YF Error] {ticker}: {e}")

    try:
        df = fetch_finnhub_historical_data(ticker)
        if df is not None and not df.empty:
            print(f"[Finnhub] Données récupérées pour {ticker}")
            return df
    except Exception as e:
        print(f"[Finnhub Error] {ticker}: {e}")

    try:
        df = scraper_penny_stock_backup(ticker)
        if df is not None and not df.empty:
            print(f"[Scraper Backup] Données récupérées pour {ticker}")
            return df
    except Exception as e:
        print(f"[Scraper Backup Error] {ticker}: {e}")

    print(f"[WARNING] Aucune donnée trouvée pour {ticker}")
    return None
