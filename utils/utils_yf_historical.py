
import yfinance as yf
import pandas as pd

def fetch_yf_historical_data(ticker: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
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
