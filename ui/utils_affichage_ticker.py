
from simulation.execution_simulee import enregistrer_trade_simule

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Dict

try:  # Optional dependency, may not be installed
    from streamlit_autorefresh import st_autorefresh
except Exception:  # pragma: no cover - fallback when package missing
    st_autorefresh = None  # type: ignore

from utils_graph import (
    plot_dual_chart,
    charger_historique_intelligent,
    charger_intraday_intelligent,
)
from utils.order_executor import executer_ordre_reel_direct


def calculer_indicateurs(df: pd.DataFrame) -> Optional[Dict[str, float]]:

    """Calcule quelques indicateurs techniques simples."""

    if df is None or df.empty:
        return None

    df = df.copy()
    close = df["close"].astype(float)

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14, min_periods=14).mean()
    avg_loss = loss.rolling(14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()

    vwap = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()

    volume_avg = df["volume"].rolling(50, min_periods=1).mean()

    return {
        "rsi": rsi.iloc[-1],
        "ema9": ema9.iloc[-1],
        "ema21": ema21.iloc[-1],
        "macd": macd.iloc[-1],
        "macd_signal": macd_signal.iloc[-1],
        "vwap": vwap.iloc[-1],
        "volume": df["volume"].iloc[-1],
        "volume_avg": volume_avg.iloc[-1],
        "price": close.iloc[-1],
    }


def calculer_score_indicateurs(data: dict) -> int:
    """Calcule un score simple basé sur plusieurs indicateurs."""

    score = 0
    if 50 < data.get("rsi", 0) < 70:
        score += 10
    if data.get("ema9", 0) > data.get("ema21", 0):
        score += 15
    if data.get("price", 0) > data.get("vwap", 0):
        score += 15
    if data.get("macd", 0) > data.get("macd_signal", 0):
        score += 10
    if data.get("volume", 0) > 1.5 * data.get("volume_avg", 0):
        score += 10
    if data.get("float", 0) < 20_000_000:
        score += 5
    if data.get("catalyst"):
        score += 15
    return min(score, 100)


def _enregistrer_trade(ticker: str, prix: float, quantite: int = 1, sl=None, tp=None, exit_price=None):
    """Enregistre un trade simulé dans la base de données."""
    enregistrer_trade_simule(
        ticker=ticker,
        entry_price=prix,
        quantity=quantite,
        sl=sl,
        tp=tp,
        exit_price=exit_price,
    )

def afficher_ticker_panel(ticker, stock, index):
    label = f"{index + 1}. {ticker}"
    with st.expander(label, expanded=False):
        if st_autorefresh:
            st_autorefresh(interval=30 * 1000, key=f"refresh_{ticker}_{index}")
        if st.button("🔄 Rafraîchir", key=f"btn_refresh_{ticker}_{index}"):
            st.experimental_rerun()

        df_intraday = charger_intraday_intelligent(ticker)
        indicateurs = calculer_indicateurs(df_intraday)
        catalyst = "FDA" if stock.get("has_fda") else ""
        if indicateurs:
            indicateurs["float"] = float(stock.get("float", 0) or 0)
            indicateurs["catalyst"] = catalyst
            score_local = calculer_score_indicateurs(indicateurs)
        else:
            score_local = 0

        ratio = (
            indicateurs.get("volume", 0) / indicateurs.get("volume_avg", 1)
            if indicateurs
            else 0
        )

        rsi = indicateurs.get("rsi") if indicateurs else None
        ema9 = indicateurs.get("ema9") if indicateurs else None
        ema21 = indicateurs.get("ema21") if indicateurs else None
        macd = indicateurs.get("macd") if indicateurs else None
        macd_signal = indicateurs.get("macd_signal") if indicateurs else None
        vwap = indicateurs.get("vwap") if indicateurs else None
        price = indicateurs.get("price") if indicateurs else None
        volume = indicateurs.get("volume") if indicateurs else None

        rsi_str = f"{rsi:.2f}" if rsi is not None else "N/A"
        ema9_str = f"{ema9:.2f}" if ema9 is not None else "N/A"
        ema21_str = f"{ema21:.2f}" if ema21 is not None else "N/A"
        macd_str = f"{macd:.2f}" if macd is not None else "N/A"
        macd_signal_str = f"{macd_signal:.2f}" if macd_signal is not None else "N/A"
        vwap_str = f"{vwap:.2f}" if vwap is not None else "N/A"
        price_str = f"{price}" if price is not None else "N/A"
        volume_str = f"{volume}" if volume is not None else "N/A"

        st.markdown(
            f"""
🔎 **Indicateurs Clés**
- **RSI (14)** : {rsi_str} {'🟢' if rsi is not None and 50 < rsi < 70 else '🔴'}
- **EMA 9 / 21** : {ema9_str} / {ema21_str} {'✅' if ema9 is not None and ema21 is not None and ema9 > ema21 else '❌'}
- **MACD** : {macd_str} vs Signal {macd_signal_str}
- **VWAP** : {vwap_str} (current price: {price_str})
- **Volume** : {volume_str} ({ratio:.2f}x)
- **Float** : {float(stock.get('float', 0))/1_000_000:.0f}M {'⚡' if stock.get('float',0) < 20_000_000 else ''}
- **Catalyseur détecté** : {catalyst or 'Aucun'}
- **Score IA** : {score_local}/100 {'🟢' if score_local>80 else '🟡' if score_local>60 else '🔴'}
"""
        )

        if df_intraday is not None and not df_intraday.empty:
            df = df_intraday.copy()
            df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
            df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
            df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()

            fig, ax = plt.subplots()
            ax.plot(df["timestamp"], df["close"], label="Price")
            ax.plot(df["timestamp"], df["vwap"], label="VWAP")
            ax.plot(df["timestamp"], df["ema9"], label="EMA9", linestyle="--")
            ax.plot(df["timestamp"], df["ema21"], label="EMA21", linestyle="--")
            ax.legend()
            st.pyplot(fig)

        st.markdown(f"**Score IA :** {stock.get('score', 'N/A')}")
        st.markdown(f"**Score global :** {stock.get('global_score', 'N/A')}")
        st.markdown(f"**Score GPT :** {stock.get('score_gpt', 'N/A')}")
        st.markdown(f"**Sentiment :** {stock.get('sentiment', 'N/A')}")
        st.markdown(f"**Source :** {stock.get('source', 'N/A')}")
        st.markdown(f"**Date :** {stock.get('date', 'N/A')}")
        st.markdown(f"**Description :** {stock.get('description', 'N/A')}")
        if stock.get('has_fda'):
            st.markdown("🧬 **FDA match**", unsafe_allow_html=True)
        st.markdown(f"**Dernier prix :** {stock.get('price', 'N/A')}")
        st.markdown(f"**Volume :** {stock.get('volume', 'N/A')}")
        st.markdown(
            f"**% Gain :** {stock.get('percent_gain', stock.get('change_percent', 'N/A'))}"
        )
        st.markdown(f"**Float :** {stock.get('float', 'N/A')}")

        details_key = f"details_{ticker}_{index}"
        details_state_key = f"{details_key}_state"
        if st.button("Afficher détails", key=details_key):
            st.session_state[details_state_key] = not st.session_state.get(details_state_key, False)

        if st.session_state.get(details_state_key, False):
            df_hist = charger_historique_intelligent(ticker)
            df_intraday = charger_intraday_intelligent(ticker)
            if df_hist is not None and not df_hist.empty:
                plot_dual_chart(ticker, df_hist, df_intraday)
            else:
                st.warning("Données historiques indisponibles.")

        prix = st.number_input(
            "💵 Prix", min_value=0.0, step=0.01, key=f"prix_{ticker}_{index}"
        )
        quantite = st.number_input(
            "🔢 Quantité", min_value=1, step=1, value=1, key=f"qty_{ticker}_{index}"
        )
        stop_loss = st.number_input(
            "❗ Stop loss", min_value=0.0, step=0.01, key=f"sl_{ticker}_{index}"
        )
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Simuler l'achat", key=f"sim_buy_{ticker}_{index}"):
            _enregistrer_trade(ticker, prix, int(quantite), sl=stop_loss)
            st.success(f"Achat simulé enregistré pour {ticker} à {prix:.2f} $")
        if c2.button("Simuler la vente", key=f"sim_sell_{ticker}_{index}"):
            _enregistrer_trade(ticker, prix, int(quantite), exit_price=prix)
            st.success(f"Vente simulée enregistrée pour {ticker} à {prix:.2f} $")
        if c3.button("Achat réel", key=f"real_buy_{ticker}_{index}"):
            ok, msg = executer_ordre_reel_direct(ticker, prix, int(quantite), stop_loss)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
        if c4.button("Vente réelle", key=f"real_sell_{ticker}_{index}"):
            st.warning("Fonction vente réelle non implémentée")
