
import yfinance as yf
import pandas as pd

def fetch_yf_historical_data(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """Download historical data for a ticker using yfinance with fallback."""
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            threads=False,
            progress=False,
        )

        if df.empty:
            print(f"[YF WARNING] Donnees vides pour {ticker} via download, tentative history")
            df = yf.Ticker(ticker).history(period=period, interval=interval)

        if df.empty:
            print(f"[YF WARNING] Donnees toujours vides pour {ticker}")
            return None

        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df[["Date", "Close"]]
        df.columns = ["timestamp", "close"]
        return df.dropna()
    except Exception as e:
        print(f"[YF ERROR] {ticker}: {e}")
        return None
