
from simulation.execution_simulee import enregistrer_trade_simule
from decision_engine import DecisionEngine
from telegram_notifier import TelegramNotifier

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
from movers_detector import get_momentum
from utils.progress_tracker import get_latest_progress
from utils.execution_reelle import executer_ordre_reel
from utils_signaux import is_buy_signal

engine = DecisionEngine()
notifier = TelegramNotifier()

BROKER_FEES = {
    "commission_per_share": 0.0049,
    "commission_min": 0.99,
    "platform_fee_per_share": 0.005,
    "platform_fee_min": 1.0,
    "platform_max_ratio": 0.01,
}


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


def _ia_score(t: dict, return_breakdown: bool = False):
    """Calcule un score pondéré basé sur les indicateurs fournis.

    Parameters
    ----------
    t : dict
        Dictionnaire contenant au moins ``rsi``, ``ema9``, ``ema21``, ``vwap``,
        ``price`` et ``volume_ratio``.
    return_breakdown : bool, optional
        Retourne un tuple ``(score, details)`` lorsque ``True``.

    Returns
    -------
    float or tuple
        Score entre 0 et 100 ou ``(score, details)``.
    """

    score = 0
    details = {}

    # RSI (pondération : 20)
    rsi = t.get("rsi", 0)
    comp = 0
    if 50 < rsi < 70:
        comp = 15
    elif rsi >= 70:
        comp = 5
    score += comp
    details["RSI"] = comp

    # EMA crossover (pondération : 25)
    ema9 = t.get("ema9")
    ema21 = t.get("ema21")
    comp = 0
    if ema9 is not None and ema21 is not None:
        if ema9 > ema21:
            comp = 25
        elif ema9 == ema21:
            comp = 10
    score += comp
    details["EMA"] = comp

    # VWAP (pondération : 15)
    price = t.get("price")
    vwap = t.get("vwap")
    comp = 0
    if price and vwap:
        if price > vwap:
            comp = 15
        else:
            comp = 5
    score += comp
    details["VWAP"] = comp

    # Volume ratio (pondération : 15)
    volume_ratio = t.get("volume_ratio", 1.0)
    comp = 0
    if volume_ratio > 1.5:
        comp = 15
    elif volume_ratio > 1.2:
        comp = 10
    score += comp
    details["Vol"] = comp

    # FDA / PR / news catalyst (pondération : 25)
    catalyst = str(t.get("source", "")).lower()
    comp = 0
    if "fda" in catalyst or "newspr" in catalyst:
        comp = 25
    score += comp
    details["FDA"] = comp

    final_score = min(score, 100)
    if return_breakdown:
        return final_score, details
    return final_score


def _calc_atr(df: pd.DataFrame, period: int = 14) -> Optional[float]:
    """Calculate the Average True Range from intraday data."""
    if df is None or df.empty or len(df) < period:
        return None
    df = df.copy()
    df["prev_close"] = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - df["prev_close"]).abs(),
            (df["low"] - df["prev_close"]).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]
    return float(atr)


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
            st.rerun()

        df_intraday = charger_intraday_intelligent(ticker)
        indicateurs = calculer_indicateurs(df_intraday)
        catalyst = "FDA" if stock.get("has_fda") else ""
        if indicateurs:
            indicateurs["float"] = float(stock.get("float", 0) or 0)
            indicateurs["catalyst"] = catalyst
            stock.update(indicateurs)
        else:
            stock.update({})

        ratio = (
            indicateurs.get("volume", 0) / indicateurs.get("volume_avg", 1)
            if indicateurs
            else 0
        )
        stock["volume_ratio"] = ratio
        stock["source"] = stock.get("source", "")

        score_local, details = _ia_score(stock, return_breakdown=True)

        rsi = indicateurs.get("rsi") if indicateurs else None
        ema9 = indicateurs.get("ema9") if indicateurs else None
        ema21 = indicateurs.get("ema21") if indicateurs else None
        macd = indicateurs.get("macd") if indicateurs else None
        macd_signal = indicateurs.get("macd_signal") if indicateurs else None
        vwap = indicateurs.get("vwap") if indicateurs else None
        price = indicateurs.get("price") if indicateurs else None
        volume = indicateurs.get("volume") if indicateurs else None

        # Mise à jour du dict stock pour les évaluations de signal
        stock["ema9"] = ema9
        stock["ema21"] = ema21
        stock["macd"] = macd
        stock["macd_signal"] = macd_signal
        stock["vwap"] = vwap
        stock["price"] = price
        stock["score_ia"] = stock.get("score", stock.get("score_ia", 0))
        stock["has_catalyst"] = bool(catalyst)

        rsi_str = f"{rsi:.2f}" if rsi is not None else "N/A"
        ema9_str = f"{ema9:.2f}" if ema9 is not None else "N/A"
        ema21_str = f"{ema21:.2f}" if ema21 is not None else "N/A"
        macd_str = f"{macd:.2f}" if macd is not None else "N/A"
        macd_signal_str = f"{macd_signal:.2f}" if macd_signal is not None else "N/A"
        vwap_str = f"{vwap:.2f}" if vwap is not None else "N/A"
        price_str = f"{price}" if price is not None else "N/A"
        volume_str = f"{volume}" if volume is not None else "N/A"

        # --- FLOAT : gestion robuste si None ---
        float_value = stock.get("float")
        if float_value is None:
            float_str = "N/A"
            float_flag = ""
        else:
            try:
                float_million = float(float_value) / 1_000_000
                float_str = f"{float_million:.1f}M"
                float_flag = "⚡" if float_value < 20_000_000 else ""
            except Exception:
                float_str = "N/A"
                float_flag = ""
        
        details_str = ", ".join(f"{k}:{v}" for k, v in details.items())
        st.markdown(
            f"""
🔎 **Indicateurs Clés**
- **RSI (14)** : {rsi_str} {'🟢' if rsi is not None and 50 < rsi < 70 else '🔴'}
- **EMA 9 / 21** : {ema9_str} / {ema21_str} {'✅' if ema9 is not None and ema21 is not None and ema9 > ema21 else '❌'}
- **MACD** : {macd_str} vs Signal {macd_signal_str}
- **VWAP** : {vwap_str} (current price: {price_str})
- **Volume** : {volume_str} ({ratio:.2f}x)
- **Float** : {float_str} {float_flag}
- **Catalyseur détecté** : {catalyst or 'Aucun'}
- **Score IA** : {score_local}/100 [{details_str}]
            """
        )

        # Utilisation du moteur de décision
        decision = engine.analyze_trade_decision(stock)
        if decision["buy"] and not decision["avoid"]:
            st.success("\n".join(decision["buy"]))
            stock["signal_level"] = "🟢"
            if st.button(f"Recevoir alerte pour {ticker}", key=f"alert_{ticker}_{index}"):
                st.info("Alerte activée pour ce ticker.")
        else:
            st.error("\n".join(decision["avoid"]))
            stock["signal_level"] = "🔴"

        st.markdown(f"**Niveau de signal :** {stock['signal_level']}")

        st.markdown("### 📌 Commentaire IA")
        if decision["buy"] and not decision["avoid"]:
            st.info("Ne pas vendre – tendance toujours favorable")
        confidence = decision.get("confidence", 0)
        st.markdown(f"**Confiance** : {confidence:.2f}")

        st.markdown("### 📤 Analyse de Sortie")
        momentum = get_momentum(ticker)
        if score_local >= 80 and momentum < 1:
            st.info("\u26a0\ufe0f Momentum faiblissant. Prêt pour une prise de profit ?")
        else:
            st.write("\u2705 Rien à signaler – dynamique toujours favorable.")

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

        st.markdown(f"**Score pondéré :** {score_local}/100 [{details_str}]")
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

        atr = _calc_atr(df_intraday)
        progress = get_latest_progress()
        capital = progress[1] if progress else 0
        stock["capital"] = capital
        suggestions = engine.generate_order_suggestions({**stock, "atr": atr, "capital": capital})
        quantite_precalc = suggestions["quantity"]
        prix_sl = suggestions["stop_loss"]
        prix_tp = suggestions["take_profit"]

        prix = st.number_input(
            "💵 Prix", min_value=0.0, step=0.01, value=suggestions["price"], key=f"prix_{ticker}_{index}"
        )
        quantite = st.number_input(
            "🔢 Quantité", min_value=1, step=1, value=quantite_precalc, key=f"qty_{ticker}_{index}"
        )
        stop_loss = st.number_input(
            "❗ Stop loss", min_value=0.0, step=0.01, value=prix_sl, key=f"sl_{ticker}_{index}"
        )
        take_profit = st.number_input(
            "📈 Take Profit", min_value=0.0, step=0.01, value=prix_tp, key=f"tp_{ticker}_{index}"
        )
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Simuler l'achat", key=f"sim_buy_{ticker}_{index}"):
            viability = engine.calculate_trade_viability(prix, take_profit, int(quantite), BROKER_FEES)
            if not viability["viable"]:
                st.error("🚫 Commissions trop élevées")
                notifier.send_trade_alert("TRADE_BLOCKED", ticker, viability)
            else:
                _enregistrer_trade(ticker, prix, int(quantite), sl=stop_loss, tp=take_profit)
                st.success(f"Achat simulé enregistré pour {ticker} à {prix:.2f} $")
                notifier.send_trade_alert("TRADE_EXECUTED", ticker, {"price": prix, "qty": int(quantite)})
        if c2.button("Simuler la vente", key=f"sim_sell_{ticker}_{index}"):
            _enregistrer_trade(ticker, prix, int(quantite), sl=stop_loss, tp=take_profit, exit_price=prix)
            st.success(f"Vente simulée enregistrée pour {ticker} à {prix:.2f} $")
        if c3.button("Achat réel", key=f"real_buy_{ticker}_{index}"):
            viability = engine.calculate_trade_viability(prix, take_profit, int(quantite), BROKER_FEES)
            if not viability["viable"]:
                st.error("🚫 Commissions trop élevées")
                notifier.send_trade_alert("TRADE_BLOCKED", ticker, viability)
            else:
                result = executer_ordre_reel(ticker, prix, int(quantite), "achat")
                if result["success"]:
                    st.success(result["message"])
                    notifier.send_trade_alert("TRADE_EXECUTED", ticker, result)
                else:
                    st.error(result["message"])
        if c4.button("Vente réelle", key=f"real_sell_{ticker}_{index}"):
            result = executer_ordre_reel(ticker, prix, int(quantite), "vente")
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])
