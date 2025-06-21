
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path
from core.db import DB_PATH

st.markdown("## 📊 Tableau de bord")

# Débogage du chemin
db_path = Path(DB_PATH)
st.info(f"📁 Utilisation de la base : {db_path}")

if not db_path.exists():
    st.error("❌ Base de données introuvable.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    st.write(f"📆 Date actuelle utilisée : {today}")

    try:
        df_today = pd.read_sql_query("SELECT * FROM trades_simules WHERE datetime LIKE ?", conn, params=(today + "%",))
        if df_today.empty:
            st.warning("⚠️ Aucun trade simulé pour aujourd'hui.")
        else:
            total_day = len(df_today)
            pnl_day = round(df_today["gain_net"].sum(), 2)

            st.markdown("### 📅 Résumé du jour")
            st.metric("Nombre de trades", total_day)
            st.metric("PnL (jour)", f"{pnl_day} $", delta_color="inverse" if pnl_day < 0 else "normal")
    except Exception as e:
        st.error(f"Erreur lors du chargement des trades_simules : {e}")

    try:
        mois_actuel = datetime.now().strftime("%Y-%m")
        df_mois = pd.read_sql_query("SELECT * FROM stats_journalieres WHERE jour LIKE ?", conn, params=(mois_actuel + "%",))

        if df_mois.empty:
            st.warning("⚠️ Aucune statistique disponible pour ce mois.")
        else:
            total_trades_mois = df_mois["total_trades"].sum()
            pnl_mois = df_mois["gain_net"].sum()

            st.markdown("### 📆 Résumé du mois")
            st.metric("Trades (mois)", total_trades_mois)
            st.metric("PnL (mois)", f"{round(pnl_mois, 2)} $", delta_color="inverse" if pnl_mois < 0 else "normal")
    except Exception as e:
        st.error(f"Erreur lors du chargement de stats_journalieres : {e}")

    conn.close()
