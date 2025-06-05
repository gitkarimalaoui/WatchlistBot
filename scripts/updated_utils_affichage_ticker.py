
import streamlit as st
import time  # ← Obligatoire ici
from utils_graph_unifie import plot_dual_chart, import_donnees_ticker_intelligent

def afficher_ticker_panel(ticker, stock, i):
    with st.expander(f"{i+1}. {ticker} | Score: {stock.get('score', 0)} | Float: {stock.get('float', '?')}M | Vol: {stock.get('volume', '?')} | Gain: {stock.get('gain_percent', '?')}%", expanded=False):
        st.write("Données clés du ticker sélectionné.")

        # Chargement des données historiques et intraday
        df_historique, df_intraday = import_donnees_ticker_intelligent(ticker)

        # Affichage des graphiques
        if df_historique is not None and df_intraday is not None:
            plot_dual_chart(ticker, df_historique, df_intraday)
        else:
            st.warning("❌ Données historiques ou intraday indisponibles.")
