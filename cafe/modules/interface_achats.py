
import streamlit as st
from datetime import date, datetime
import sqlite3
import pandas as pd
from modules.database import insert_achat_quotidien

DB_PATH = 'cafe_management.db'

def get_achats_by_month(year, month):
    """Return purchases for the specified month.

    Args:
        year (int): Year of interest.
        month (int): Month number (1-12).

    Returns:
        pd.DataFrame: DataFrame of purchase records.
    """

    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year + 1 if month == 12 else year}-{(month % 12) + 1:02d}-01"
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('''
        SELECT * FROM achats_quotidiens
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    ''', conn, params=(start_date, end_date))
    conn.close()
    return df

def interface_achats():
    """Streamlit UI for recording and viewing purchases.

    Returns:
        None
    """

    st.header("🛒 Gestion des Achats Quotidiens")
    tab1, tab2 = st.tabs(["📝 Saisie des Achats", "📊 Consultation Mensuelle"])

    with tab1:
        date_achat = st.date_input("Date d'achat", value=date.today())
        mode = st.radio("Mode de saisie", ["Détail par produit", "Saisie directe du total"])
        achats_data = {}
        total_achats = 0

        if mode == "Détail par produit":
            st.subheader("Produits")
            fields = ["lait", "sucre", "eau", "viennoiserie", "pain", "the", "bonbon_gaz",
                      "banane", "pomme", "olive", "orange", "produit_nettoyage", "semoule", "fromage"]
            for i in range(0, len(fields), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(fields):
                        field = fields[i + j]
                        achats_data[field] = cols[j].number_input(field.replace("_", " ").title(), min_value=0.0, step=0.1, format="%.2f")
            total_achats = sum(achats_data.values())
        else:
            total_achats = st.number_input("💰 Total des achats (DH)", min_value=0.0, step=0.1, format="%.2f")

        if st.button("💾 Enregistrer les Achats"):
            achats_data["total_achats"] = total_achats
            insert_achat_quotidien(str(date_achat), achats_data)
            st.success(f"✅ Achats du {date_achat} enregistrés avec succès !")
            st.info(f"💰 Total des achats : {total_achats:.2f} DH")

    with tab2:
        year = st.selectbox("Année", range(2020, 2031), index=5, key="year_achat")
        month = st.selectbox("Mois", range(1, 13), index=datetime.now().month - 1, key="mois_achat")
        df = get_achats_by_month(year, month)

        if not df.empty:
            st.subheader("📅 Achats par Jour")
            df["date"] = pd.to_datetime(df["date"])
            st.dataframe(df)

            if "total_achats" in df.columns:
                total_mensuel = df["total_achats"].sum()
                st.metric("💰 Total Achats du Mois", f"{total_mensuel:.2f} DH")
        else:
            st.warning("Aucune donnée disponible pour ce mois.")
