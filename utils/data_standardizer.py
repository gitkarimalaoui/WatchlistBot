# utils/data_standardizer.py
import pandas as pd
from enum import Enum

class DataSource(Enum):
    YFINANCE = "yfinance"
    FINNHUB = "finnhub"

class DataStandardizer:
    @staticmethod
    def standardize_ohlcv(df: pd.DataFrame, source: DataSource, ticker: str) -> pd.DataFrame:
        if source == DataSource.YFINANCE:
            df.columns = [col.capitalize() for col in df.columns]
            df["Ticker"] = ticker
            return df[["Date", "Open", "High", "Low", "Close", "Volume", "Ticker"]]

        elif source == DataSource.FINNHUB:
            df["Ticker"] = ticker
            return df[["Date", "Open", "High", "Low", "Close", "Volume", "Ticker"]]

        return df
