import requests
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
from advanced_logger import logger, safe_api_call, data_validator
from config_manager import config_manager
from data_standardizer import DataStandardizer, DataSource
from unified_data_collector import DataProvider


class FinnhubProvider(DataProvider):
    """Fournisseur de données via API Finnhub"""
    
    def __init__(self):
        self.api_key = config_manager.get("finnhub_api")
        self.base_url = "https://finnhub.io/api/v1"

    @safe_api_call(retries=2, delay=1.0)
    @data_validator(required_columns=['Close'], min_rows=1)
    def fetch_historical_data(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Récupère les données historiques journalières via Finnhub"""
        try:
            logger.info("📈 Récupération données historiques Finnhub", ticker=ticker, period=period)
            
            end_time = int(datetime.utcnow().timestamp())
            start_time = end_time - (365 * 24 * 60 * 60)  # 1 an
            
            url = f"{self.base_url}/stock/candle"
            params = {
                "symbol": ticker,
                "resolution": "D",
                "from": start_time,
                "to": end_time,
                "token": self.api_key
            }
            resp = requests.get(url, params=params)
            data = resp.json()

            if data.get("s") != "ok":
                logger.warning("❌ Aucune donnée valide Finnhub", ticker=ticker)
                return None

            df = pd.DataFrame({
                "Date": pd.to_datetime(data["t"], unit="s"),
                "Open": data["o"],
                "High": data["h"],
                "Low": data["l"],
                "Close": data["c"],
                "Volume": data["v"]
            })

            df_std = DataStandardizer.standardize_ohlcv(df, DataSource.FINNHUB, ticker)
            logger.info("✅ Données historiques Finnhub récupérées", ticker=ticker, rows=len(df_std))
            return df_std

        except Exception as e:
            logger.error("Erreur récupération Finnhub historique", ticker=ticker, exception=e)
            return None

    @safe_api_call(retries=2, delay=1.0)
    @data_validator(min_rows=1)
    def fetch_intraday_data(self, ticker: str, interval: str = "1") -> Optional[pd.DataFrame]:
        """Récupère les données intraday (1 minute) via Finnhub"""
        try:
            now = int(datetime.utcnow().timestamp())
            one_day_ago = now - (24 * 60 * 60)
            
            url = f"{self.base_url}/stock/candle"
            params = {
                "symbol": ticker,
                "resolution": interval,  # '1' pour 1min
                "from": one_day_ago,
                "to": now,
                "token": self.api_key
            }
            resp = requests.get(url, params=params)
            data = resp.json()

            if data.get("s") != "ok":
                logger.warning("⚠️ Aucune donnée intraday Finnhub", ticker=ticker)
                return None

            df = pd.DataFrame({
                "Date": pd.to_datetime(data["t"], unit="s"),
                "Open": data["o"],
                "High": data["h"],
                "Low": data["l"],
                "Close": data["c"],
                "Volume": data["v"]
            })

            df_std = DataStandardizer.standardize_ohlcv(df, DataSource.FINNHUB, ticker)
            logger.info("✅ Données intraday Finnhub récupérées", ticker=ticker, rows=len(df_std))
            return df_std

        except Exception as e:
            logger.error("Erreur récupération Finnhub intraday", ticker=ticker, exception=e)
            return None

    @safe_api_call(retries=1, delay=0.5)
    def get_current_price(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Récupère le prix actuel"""
        try:
            url = f"{self.base_url}/quote?symbol={ticker}&token={self.api_key}"
            resp = requests.get(url)
            data = resp.json()

            if not data:
                return None

            return {
                'price': data.get("c"),
                'change': data.get("d"),
                'change_percent': data.get("dp"),
                'volume': data.get("v"),
                'source': 'finnhub'
            }
        except Exception as e:
            logger.error("Erreur prix courant Finnhub", ticker=ticker, exception=e)
            return None
