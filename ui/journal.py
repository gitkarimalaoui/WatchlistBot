
import streamlit as st
import pandas as pd
import sqlite3
from core.db import DB_PATH

def afficher_journal():
    st.header("📓 Journal des trades simulés")
    conn = None
    df = None
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM trades_simules ORDER BY date DESC",
            conn,
        )
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur lors du chargement du journal : {e}")
    finally:
        if conn is not None:
            conn.close()
    return df
