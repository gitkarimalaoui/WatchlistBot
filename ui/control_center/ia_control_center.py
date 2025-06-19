import streamlit as st
from watchlist_panel import render_watchlist_panel

st.title("🔍 IA Control Center")

st.write("Centre de contrôle principal de l'IA, gestion des modules et des tests.")
render_watchlist_panel()
