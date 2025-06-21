import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime

def cloturer_journee():
    st.title("🔒 Clôturer la Journée de Trading")

    date_selectionnee = st.date_input("📅 Sélectionnez une date à clôturer", key="date_cloture")
    date_str = date_selectionnee.strftime("%Y-%m-%d")

    st.success(f"📅 Date choisie : {date_str}")

    try:
        conn = sqlite3.connect("data/trades.db")
        st.success("✅ Connexion à la base réussie")
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return

    try:
        df = pd.read_sql_query("SELECT * FROM trades_simules", conn)
        st.success(f"📄 {len(df)} lignes chargées depuis trades_simules")
    except Exception as e:
        st.error(f"❌ Erreur chargement trades_simules : {e}")
        conn.close()
        return

    try:
        df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce')
        df = df.dropna(subset=["datetime"])
        st.success("📅 Parsing datetime effectué")
    except Exception as e:
        st.error(f"❌ Erreur parsing datetime : {e}")
        conn.close()
        return

    df_jour = df[df["datetime"].dt.strftime("%Y-%m-%d") == date_str]

    if df_jour.empty:
        st.warning("⚠️ Aucun trade trouvé pour cette date.")
        conn.close()
        return

    total_trades = len(df_jour)
    total_gain = df_jour["gain_net"].sum()
    total_perte = df_jour[df_jour["gain_net"] < 0]["gain_net"].sum()
    gain_net = total_gain

    tickers_analytics = ",".join(df_jour["ticker"].unique())

    st.markdown("### 🧾 Résumé de la journée :")
    st.metric("📊 Nombre de trades", total_trades)
    st.metric("💵 Gain total ($)", total_gain)
    st.metric("📉 Perte totale ($)", abs(total_perte))
    st.metric("📈 Gain net ($)", gain_net)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM stats_journalieres WHERE jour = ?", (date_str,))
    existe = cur.fetchone()[0] > 0

    if existe:
        st.warning("⚠️ Une clôture existe déjà pour cette date.")
        if not st.checkbox("🔁 Voulez-vous la remplacer ?"):
            conn.close()
            return
        cur.execute("DELETE FROM stats_journalieres WHERE jour = ?", (date_str,))
        conn.commit()

    if st.button("📦 Clôturer maintenant"):
        cur.execute(
            "INSERT INTO stats_journalieres (jour, total_trades, total_gain, total_perte, gain_net, tickers_analytiques) VALUES (?, ?, ?, ?, ?, ?)",
            (date_str, total_trades, total_gain, total_perte, gain_net, tickers_analytics)
        )
        conn.commit()
        st.success("✅ Journée clôturée avec succès.")

    conn.close()

if __name__ == "__main__":
    cloturer_journee()
