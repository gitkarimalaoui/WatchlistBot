import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from utils_yf_historical import fetch_yf_historical_data
from utils_finnhub import fetch_finnhub_historical_data, fetch_finnhub_intraday_data


def charger_historique_intelligent(ticker: str) -> pd.DataFrame:
    """Retourne l'historique du ticker en essayant YF puis Finnhub."""
    try:
        df = fetch_yf_historical_data(ticker)
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"[INFO] Historique trouvé via YFinance pour {ticker}")
            return df
        print(f"[YF WARNING] Données vides pour {ticker}")
    except Exception as e:
        print(f"[YF ERROR] {ticker}: {e}")

    try:
        df = fetch_finnhub_historical_data(ticker)
        if isinstance(df, pd.DataFrame) and not df.empty:
            df = df.rename(columns={"Date": "timestamp", "Close": "close"})
            print(f"[INFO] Historique trouvé via Finnhub pour {ticker}")
            return df
        print(f"[Finnhub Historical] No data for {ticker}")
    except Exception as e:
        print(f"[Finnhub ERROR] {ticker}: {e}")

    return pd.DataFrame()


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
