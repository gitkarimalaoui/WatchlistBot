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

        # Convert index to a dedicated timestamp column regardless of its name
        df.index = pd.to_datetime(df.index)
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)

        # group columns if empty or multi-indexed results
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        column_map = {
            "timestamp": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "close",
            "Volume": "volume",
        }
        available_cols = [c for c in column_map.keys() if c in df.columns]
        if "timestamp" not in available_cols or "Close" not in df.columns and "Adj Close" not in df.columns:
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
    """Attempt to fetch data from Yahoo Finance then fall back to Finnhub."""
    df = fetch_yf_historical_data(ticker)
    if df is not None and not df.empty:
        return df

    print(f"[INFO] Fallback Finnhub pour {ticker}")
    df = fetch_finnhub_historical_data(ticker)
    if df is None or df.empty:
        return None

    df = df.rename(columns={"Date": "timestamp", "Close": "close"})

    if "timestamp" not in df.columns:
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)

    if "close" not in df.columns and "Close" in df.columns:
        df.rename(columns={"Close": "close"}, inplace=True)

    if "timestamp" not in df.columns or "close" not in df.columns:
        print(f"[Finnhub ERROR] Colonnes manquantes pour {ticker}")
        return None

    df = df[["timestamp", "close"]]
    return df
