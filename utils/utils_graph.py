import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta

from utils_yf_historical import fetch_yf_historical_data
from utils_finnhub import fetch_finnhub_historical_data, fetch_finnhub_intraday_data
from db_historical import load_historical
import sqlite3
from pathlib import Path


def _fetch_missing(ticker: str) -> pd.DataFrame:
    """Try to download historical data from available sources."""
    df = fetch_yf_historical_data(ticker)
    if df is not None and not df.empty:
        return df
    df = fetch_finnhub_historical_data(ticker)
    if df is not None and not df.empty:
        if "Date" in df.columns:
            df = df.rename(columns={"Date": "timestamp", "Close": "close"})
        return df
    return pd.DataFrame()


from typing import Optional


def charger_historique_intelligent(
    ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """Load historical data from DB and download any missing dates."""

    end_dt = pd.to_datetime(end_date or datetime.today().strftime("%Y-%m-%d")).date()
    start_dt = pd.to_datetime(start_date or (end_dt - timedelta(days=180))).date()

    df_db = load_historical(str(ticker), str(start_dt), str(end_dt))
    max_db_date = df_db["timestamp"].max().date() if not df_db.empty else start_dt - timedelta(days=1)

    df_new = pd.DataFrame()
    if max_db_date < end_dt:
        missing_start = max_db_date + timedelta(days=1)
        fetched = _fetch_missing(ticker)
        if not fetched.empty:
            mask = (fetched["timestamp"].dt.date >= missing_start) & (
                fetched["timestamp"].dt.date <= end_dt
            )
            df_new = fetched.loc[mask]
            if not df_new.empty:
                conn = sqlite3.connect(Path(__file__).resolve().parents[1] / "data" / "trades.db")
                time_col = "timestamp"
                cur = conn.execute("PRAGMA table_info(historical_data)")
                cols = [r[1] for r in cur.fetchall()]
                if "timestamp" not in cols and "date" in cols:
                    time_col = "date"
                    df_new = df_new.rename(columns={"timestamp": "date"})
                df_insert = df_new.copy()
                df_insert["ticker"] = ticker
                df_insert.to_sql("historical_data", conn, if_exists="append", index=False)
                conn.close()

    df_final = pd.concat([df_db, df_new], ignore_index=True)
    if not df_final.empty:
        df_final.sort_values("timestamp", inplace=True)
        df_final.drop_duplicates(subset="timestamp", inplace=True)
    return df_final


def charger_intraday_intelligent(ticker: str) -> pd.DataFrame:
    """Retourne l'intraday du ticker via Finnhub avec fallback YF."""
    try:
        df = fetch_finnhub_intraday_data(ticker)
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"[INFO] Intraday trouvé via Finnhub pour {ticker}")
            return df
        print(f"[Finnhub Intraday] No data for {ticker}")
        raise ValueError("Finnhub intraday data empty")
    except Exception as e:
        print(f"[WARNING] Fallback YF déclenché pour {ticker}: {e}")
        try:
            df = fetch_yf_historical_data(ticker)  # fallback approximatif
            if isinstance(df, pd.DataFrame) and not df.empty:
                print(f"[INFO] Fallback YF intraday réussi pour {ticker}")
                return df
        except Exception as fe:
            print(f"[ERROR] Échec total récupération données intraday pour {ticker}: {fe}")
    return pd.DataFrame()


def charger_donnees_ticker_intelligent(ticker: str) -> tuple:
    """Retourne un tuple (df_historique, df_intraday)."""
    historique = charger_historique_intelligent(ticker)
    intraday = charger_intraday_intelligent(ticker)
    return historique, intraday


def plot_dual_chart(ticker: str, df_hist: pd.DataFrame, df_intraday: pd.DataFrame):
    """Affiche deux graphiques: historique quotidien et données intraday."""
    if df_hist is None or df_hist.empty:
        st.warning(f"Aucune donnée historique disponible pour {ticker}")
        return
    if df_intraday is None or df_intraday.empty:
        st.warning(f"Aucune donnée intraday disponible pour {ticker}")
        return

    st.subheader(f"📈 Graphique de {ticker}")

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    close_col_hist = "close" if "close" in df_hist.columns else "Close"
    if close_col_hist not in df_hist.columns:
        st.error(f"Colonnes inattendues pour les données historiques de {ticker}")
        return
    df_hist[close_col_hist].plot(ax=ax1, title=f"{ticker} - Données Historiques (Daily)", grid=True)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Prix de clôture")
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    close_col_intra = "close" if "close" in df_intraday.columns else "Close"
    if close_col_intra not in df_intraday.columns:
        print(f"[ERROR] Colonne 'close' manquante dans données intraday pour {ticker}")
        st.error(f"Données intraday invalides pour {ticker}")
        return
    df_intraday[close_col_intra].plot(ax=ax2, title=f"{ticker} - Intraday (1m)", grid=True, color="orange")
    ax2.set_xlabel("Heure")
    ax2.set_ylabel("Prix")
    st.pyplot(fig2)
