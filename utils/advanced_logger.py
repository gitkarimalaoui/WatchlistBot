# utils/advanced_logger.py
import logging
import time

logger = logging.getLogger("WatchlistBot")
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

def safe_api_call(retries=3, delay=1.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Retry {attempt+1}/{retries} failed with error: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def data_validator(required_columns=None, min_rows=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            df = func(*args, **kwargs)
            if df is not None and len(df) >= min_rows:
                if required_columns and all(col in df.columns for col in required_columns):
                    return df
            return None
        return wrapper
    return decorator
