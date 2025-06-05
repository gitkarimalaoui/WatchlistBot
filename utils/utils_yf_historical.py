
import yfinance as yf
import pandas as pd
from utils_finnhub import fetch_finnhub_historical_data


def fetch_yf_historical_data(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
    threads: bool = False,
) -> pd.DataFrame:
    """Download historical prices from Yahoo Finance and fall back to Finnhub.

    Parameters are exposed so they can easily be tuned if the default call
    returns empty dataframes. ``threads`` is disabled by default as it sometimes
    causes connection issues in constrained environments.
    """

    try:
        df = yf.download(
            tickers=ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
            threads=threads,
            group_by="ticker",
        )

        if df.empty:
            print(f"[YF WARNING] Donnees vides pour {ticker}, fallback Finnhub")
            df = fetch_finnhub_historical_data(ticker)
            if df is None or df.empty:
                return None
            return df

        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"])

        # group columns if empty or multi-indexed results
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        column_map = {
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
        available_cols = [c for c in column_map.keys() if c in df.columns]
        if not available_cols:
            print(f"[YF ERROR] Colonnes manquantes pour {ticker}")
            return None

        df = df[available_cols]
        df.rename({k: column_map[k] for k in available_cols}, axis=1, inplace=True)
        # ensure final column order
        ordered = [column_map[c] for c in column_map if c in available_cols]
        df = df[ordered]
        return df

    except Exception as e:
        print(f"[YF ERROR] {ticker}: {e}")
        return None


def fetch_historical_with_fallback(ticker: str) -> pd.DataFrame:
    """Backward compatible wrapper around :func:`fetch_yf_historical_data`."""
    return fetch_yf_historical_data(ticker)
