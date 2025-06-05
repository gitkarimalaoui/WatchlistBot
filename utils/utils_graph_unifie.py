import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from utils_yf_historical import fetch_yf_historical_data
from utils_finnhub import fetch_finnhub_historical_data, fetch_finnhub_intraday_data


def prepare_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure the dataframe has the expected OHLCV columns.

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataframe potentially using various column names.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``['timestamp', 'open', 'high', 'low', 'close', 'volume']``
        or an empty DataFrame if required columns are missing.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    rename_map = {
        "Date": "timestamp",
        "Timestamp": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "close",
        "Volume": "volume",
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    expected = ["timestamp", "open", "high", "low", "close", "volume"]
    if not all(col in df.columns for col in expected):
        missing = [c for c in expected if c not in df.columns]
        print(f"[GRAPH ERROR] Colonnes manquantes: {missing}")
        return pd.DataFrame()

    return df[expected]


def charger_historique_intelligent(ticker: str) -> pd.DataFrame:
    try:
        df = fetch_yf_historical_data(ticker)
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"[INFO] Historique trouvé via YFinance pour {ticker}")
            return prepare_ohlcv(df)
        else:
            print(f"[YF WARNING] Données vides pour {ticker}")
    except Exception as e:
        print(f"[YF ERROR] {ticker}: {e}")

    try:
        df = fetch_finnhub_historical_data(ticker)
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"[INFO] Historique trouvé via Finnhub pour {ticker}")
            return prepare_ohlcv(df)
        else:
            print(f"[Finnhub Historical] No data for {ticker}")
    except Exception as e:
        print(f"[Finnhub ERROR] {ticker}: {e}")

    return pd.DataFrame()


def charger_intraday_intelligent(ticker: str) -> pd.DataFrame:
    try:
        df = fetch_finnhub_intraday_data(ticker)
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"[INFO] Intraday trouvé via Finnhub pour {ticker}")
            return prepare_ohlcv(df)
        else:
            raise ValueError("Finnhub vide")
    except Exception as e:
        print(f"[WARNING] Fallback YF déclenché pour {ticker}: {e}")
        try:
            df = fetch_yf_historical_data(ticker)  # fallback approximatif
            if isinstance(df, pd.DataFrame) and not df.empty:
                print(f"[INFO] Fallback YF intraday réussi pour {ticker}")
                return prepare_ohlcv(df)
        except Exception as fe:
            print(f"[ERROR] Échec total récupération données intraday pour {ticker}: {fe}")
    return pd.DataFrame()


def charger_donnees_ticker_intelligent(ticker: str) -> tuple:
    """
    Retourne un tuple contenant (df_historique, df_intraday)
    """
    historique = charger_historique_intelligent(ticker)
    intraday = charger_intraday_intelligent(ticker)
    return historique, intraday


def plot_dual_chart(ticker: str, df_hist: pd.DataFrame, df_intraday: pd.DataFrame):
    df_hist = prepare_ohlcv(df_hist)
    df_intraday = prepare_ohlcv(df_intraday)

    if df_hist.empty:
        st.warning(f"Aucune donnée historique disponible pour {ticker}")
        return
    if df_intraday.empty:
        st.warning(f"Aucune donnée intraday disponible pour {ticker}")
        return

    st.subheader(f"📈 Graphique de {ticker}")

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    df_hist["close"].plot(
        ax=ax1, title=f"{ticker} - Données Historiques (Daily)", grid=True
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Prix de clôture")
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    df_intraday["close"].plot(
        ax=ax2, title=f"{ticker} - Intraday (1m)", grid=True, color="orange"
    )
    ax2.set_xlabel("Heure")
    ax2.set_ylabel("Prix")
    st.pyplot(fig2)
