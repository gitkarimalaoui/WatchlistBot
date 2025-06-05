# utils_error_handler.py
import logging
import functools
from typing import Optional, Any, Callable
import streamlit as st

class WatchlistLogger:
    """Gestionnaire de logs centralisé pour WatchlistBot"""
    
    def __init__(self, name: str = "watchlist_bot"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, ticker: str = None):
        prefix = f"[{ticker}] " if ticker else ""
        self.logger.info(f"{prefix}{message}")
    
    def error(self, message: str, ticker: str = None, exception: Exception = None):
        prefix = f"[{ticker}] " if ticker else ""
        error_msg = f"{prefix}{message}"
        if exception:
            error_msg += f" - {str(exception)}"
        self.logger.error(error_msg)
    
    def warning(self, message: str, ticker: str = None):
        prefix = f"[{ticker}] " if ticker else ""
        self.logger.warning(f"{prefix}{message}")

# Instance globale
logger = WatchlistLogger()

def safe_data_fetch(func: Callable) -> Callable:
    """Décorateur pour sécuriser les appels d'API"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Optional[Any]:
        ticker = args[0] if args else kwargs.get('ticker', 'Unknown')
        try:
            result = func(*args, **kwargs)
            if result is not None:
                logger.info(f"Données récupérées avec succès", ticker=ticker)
            else:
                logger.warning(f"Aucune donnée trouvée", ticker=ticker)
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données", ticker=ticker, exception=e)
            return None
    return wrapper

def streamlit_error_boundary(func: Callable) -> Callable:
    """Décorateur pour gérer les erreurs dans Streamlit"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur Streamlit dans {func.__name__}", exception=e)
            return None
    return wrapper