
import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime

def telecharger_donnees_historique(ticker: str):
    """
    Récupère les données historiques daily sur 2 ans pour un ticker
    """
    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        if df.empty:
            return False
        df.reset_index(inplace=True)
        df["Ticker"] = ticker
        df = df.rename(columns={"Date": "date"})
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        with sqlite3.connect("data/trades.db") as conn:
            df.to_sql("historical_data", conn, if_exists="append", index=False)
        return True
    except Exception as e:
        print(f"Erreur lors du téléchargement des données historiques pour {ticker} : {e}")
        return False
