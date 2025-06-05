
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(page_title="📅 Dashboard Journalier", layout="wide")
st.title("📅 Dashboard Journalier des Trades")

JOURNAL_PATH = os.path.join("data", "journal_simule.json")

# Charger les données du journal
if os.path.exists(JOURNAL_PATH):
    with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    df = pd.DataFrame(data)

    if not df.empty and "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["date"] = df["datetime"].dt.date

        today = datetime.now().date()
        df_today = df[df["date"] == today]

        total_today = len(df_today)
        total_achats = df_today[df_today["action"] == "achat"]
        total_ventes = df_today[df_today["action"] == "vente"]
        total_pnl = df_today["gain_net"].sum()

        st.markdown("### 🔎 Résumé du jour")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total trades", total_today)
        col2.metric("Achats", len(total_achats))
        col3.metric("Ventes", len(total_ventes))
        col4.metric("PnL (Net)", f"{total_pnl:.2f} $", delta_color="inverse" if total_pnl < 0 else "normal")
    else:
        st.warning("Le journal ne contient pas de données valides pour aujourd'hui.")
else:
    st.error("📭 Base de journal non trouvée. Lance une simulation pour la générer.")
