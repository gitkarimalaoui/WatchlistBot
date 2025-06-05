
import streamlit as st
from v6.pages import patterns

st.set_page_config(page_title="WatchlistBot - Tableau de bord", layout="wide")

st.title("📊 Bienvenue dans WatchlistBot")
st.header("🔍 Analyse des opportunités avec IA + Watchlists")

# Appelle le module d'affichage de la page patterns
patterns.afficher_page_patterns()
