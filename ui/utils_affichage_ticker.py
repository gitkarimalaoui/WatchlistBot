
import os
import json
from datetime import datetime

import streamlit as st
from utils_graph import (
    plot_dual_chart,
    charger_historique_intelligent,
    charger_intraday_intelligent,
)
from utils.order_executor import executer_ordre_reel_direct

JOURNAL_PATH = os.path.join("data", "journal_simule.json")


def _enregistrer_trade(action, ticker, prix):
    trade = {
        "ticker": ticker,
        "action": action,
        "prix": round(prix, 2),
        "gain_net": 0,
        "datetime": datetime.now().isoformat(),
        "simulation_ia": "non",
    }
    if os.path.exists(JOURNAL_PATH):
        with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    data.append(trade)
    with open(JOURNAL_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def afficher_ticker_panel(ticker, stock, index):
    label = f"{index + 1}. {ticker}"
    with st.expander(label, expanded=False):
        st.markdown(f"**Score IA :** {stock.get('score', 'N/A')}")
        st.markdown(f"**Score global :** {stock.get('global_score', 'N/A')}")
        st.markdown(f"**Score GPT :** {stock.get('score_gpt', 'N/A')}")
        st.markdown(f"**Sentiment :** {stock.get('sentiment', 'N/A')}")
        st.markdown(f"**Source :** {stock.get('source', 'N/A')}")
        st.markdown(f"**Date :** {stock.get('date', 'N/A')}")
        st.markdown(f"**Description :** {stock.get('description', 'N/A')}")
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
            _enregistrer_trade("achat", ticker, prix)
            st.success(f"Achat simulé enregistré pour {ticker} à {prix:.2f} $")
        if c2.button("Simuler la vente", key=f"sim_sell_{ticker}_{index}"):
            _enregistrer_trade("vente", ticker, prix)
            st.success(f"Vente simulée enregistrée pour {ticker} à {prix:.2f} $")
        if c3.button("Achat réel", key=f"real_buy_{ticker}_{index}"):
            ok, msg = executer_ordre_reel_direct(ticker, prix, int(quantite), stop_loss)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
        if c4.button("Vente réelle", key=f"real_sell_{ticker}_{index}"):
            st.warning("Fonction vente réelle non implémentée")
