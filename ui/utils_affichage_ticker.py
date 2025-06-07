
import streamlit as st
from utils_graph import (
    plot_dual_chart,
    charger_historique_intelligent,
    charger_intraday_intelligent,
)

def afficher_ticker_panel(ticker, stock, index):
    st.markdown(f"### {index + 1}. {ticker}")

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

    key = f"show_{ticker}_{index}"
    state_key = f"{key}_state"
    if st.button("Afficher détails", key=key):
        st.session_state[state_key] = not st.session_state.get(state_key, False)

    if st.session_state.get(state_key, False):
        df_hist = charger_historique_intelligent(ticker)
        df_intraday = charger_intraday_intelligent(ticker)
        if df_hist is not None and not df_hist.empty:
            plot_dual_chart(ticker, df_hist, df_intraday)
        else:
            st.warning("Données historiques indisponibles.")
