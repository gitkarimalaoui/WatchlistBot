
import streamlit as st
import pandas as pd
import sqlite3

def afficher_journal():
    st.header("📓 Journal des trades simulés")
    try:
        conn = sqlite3.connect("watchlist_bot.db")
        df = pd.read_sql_query("SELECT * FROM trades_simules ORDER BY date DESC", conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur lors du chargement du journal : {e}")