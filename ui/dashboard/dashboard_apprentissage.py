import streamlit as st
from watchlist_panel import render_watchlist_panel

st.title("🧠 Dashboard Apprentissage")

st.write("Visualisation des patterns gagnants/perdants détectés par l'IA.")
render_watchlist_panel()
