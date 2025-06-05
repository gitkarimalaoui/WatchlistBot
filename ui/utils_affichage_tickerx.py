
import streamlit as st
from utils_graph_unifie import plot_dual_chart, charger_donnees_ticker_intelligent

def afficher_ticker_panel(ticker, stock, index):
    with st.expander(f"{index + 1}. {ticker}", expanded=False):
        st.markdown(f"**Symbole :** {ticker}")
        st.markdown(f"**Score :** {stock.get('score', 'N/A')}")
        st.markdown(f"**Prix actuel :** {stock.get('price', 'N/A')}")
        st.markdown(f"**Volume :** {stock.get('volume', 'N/A')}")
        st.markdown(f"**% Gain :** {stock.get('percent_gain', 'N/A')}")

        df_hist, df_intraday = charger_donnees_ticker_intelligent(ticker)

        if df_hist is not None and not df_hist.empty:
            plot_dual_chart(ticker, df_hist, df_intraday)
        else:
            st.warning("Données historiques indisponibles.")
