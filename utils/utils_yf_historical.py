
import yfinance as yf
import pandas as pd


def fetch_yf_historical_data(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
    threads: bool = False,
) -> pd.DataFrame:
    """Download historical prices from Yahoo Finance.

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
            print(f"[YF WARNING] Donnees vides pour {ticker}")
            return None

        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df[["Date", "Close"]]
        df.columns = ["timestamp", "close"]
        return df

    except Exception as e:
        print(f"[YF ERROR] {ticker}: {e}")
        return None


def fetch_historical_with_fallback(ticker: str) -> pd.DataFrame:
    """Attempt to fetch data from Yahoo Finance then fall back to Finnhub."""
    df = fetch_yf_historical_data(ticker)
    if df is not None and not df.empty:
        return df

    from utils_finnhub import fetch_finnhub_historical_data

    print(f"[INFO] Fallback Finnhub pour {ticker}")
    df = fetch_finnhub_historical_data(ticker)
    if df is None or df.empty:
        return None

    df = df.rename(columns={"Date": "timestamp", "Close": "close"})
    df = df[["timestamp", "close"]]
    return df
