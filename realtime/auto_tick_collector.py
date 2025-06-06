import streamlit as st
import os
import json
import pandas as pd
import time
from datetime import datetime
from realtime.build_intraday_candles import build_candles
from realtime.utils_graph_local import plot_candles
from tick_collector_launcher import start_tick_collector_background

TICKERS_PATH = os.path.join("data", "tickers_manuels.json")

def charger_tickers():
    if not os.path.exists(TICKERS_PATH):
        return []
    try:
        with open(TICKERS_PATH, "r") as f:
            data = json.load(f)
        return data.get("tickers", [])
    except Exception as e:
        st.error(f"Erreur lors du chargement des tickers : {e}")
        return []

def afficher_infos_ticker(ticker):
    st.subheader(f"📈 Données pour {ticker}")
    quote_path = os.path.join("data", "ticks", f"{ticker}.csv")
    if os.path.exists(quote_path):
        df = pd.read_csv(quote_path)
        if not df.empty:
            last = df.iloc[-1]
            st.write("Prix actuel", f"${last['c']:.2f}")
            st.write("Ouverture", f"${last['o']:.2f}")
            st.write("Haut", f"${last['h']:.2f}")
            st.write("Bas", f"${last['l']:.2f}")
        else:
            st.warning("Aucune donnée disponible.")
    else:
        st.warning("Fichier de données introuvable.")

def afficher_graphique_intraday(ticker):
    st.subheader("📉 Graphique intraday (local)")
    try:
        candles = build_candles(ticker)
        if candles.empty:
            st.error("Données graphiques introuvables pour ce ticker.")
        else:
            plot_candles(candles, ticker)
    except Exception as e:
        st.error(f"Erreur affichage graphique : {e}")

def main():
    st.set_page_config(layout="wide", page_title="WatchlistBot V6.2")
    st.title("⏱️ Analyse des tickers en temps réel")

    # Lancer la collecte de ticks en tâche de fond
    start_tick_collector_background()

    tickers = charger_tickers()
    st.success(f"{len(tickers)} tickers chargés.")
    st.json(tickers)

    if not tickers:
        return

    selected_ticker = st.selectbox("Sélectionner un ticker :", tickers)
    if selected_ticker:
        afficher_infos_ticker(selected_ticker)
        afficher_graphique_intraday(selected_ticker)

    # Rafraîchissement automatique toutes les 5 secondes
    st.write("Actualisation automatique dans 5s...")
    time.sleep(5)
    st.rerun()

def run():
    main()
