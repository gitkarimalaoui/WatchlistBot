
import streamlit as st
import plotly.express as px
from datetime import datetime
from modules.database import get_data_by_period, get_chiffre_affaire_by_period

def interface_rapports_mensuels():
    st.header("📊 Rapports Mensuels")
    year = st.selectbox("Année", range(2020, 2031), index=5)
    month = st.selectbox("Mois", range(1, 13), index=datetime.now().month - 1)

    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year + 1 if month == 12 else year}-{1 if month == 12 else month + 1:02d}-01"
    show_rapport(start_date, end_date)

def interface_rapports_annuels():
    st.header("📊 Rapports Annuels")
    year = st.selectbox("Sélectionner l'année", range(2020, 2031), index=5)
    start_date = f"{year}-01-01"
    end_date = f"{year + 1}-01-01"
    show_rapport(start_date, end_date)

def show_rapport(start_date, end_date):
    achats_df, charges_df = get_data_by_period(start_date, end_date)
    chiffre_df = get_chiffre_affaire_by_period(start_date, end_date)

    total_achats = achats_df.drop(columns=['id', 'date'], errors='ignore').sum(numeric_only=True).sum() if not achats_df.empty else 0
    total_charges = charges_df.drop(columns=['id', 'date', 'type_charge'], errors='ignore').sum(numeric_only=True).sum() if not charges_df.empty else 0
    total_ca = chiffre_df['total'].sum() if not chiffre_df.empty else 0
    benefice_net = total_ca - (total_achats + total_charges)

    st.metric("📈 Chiffre d'Affaire", f"{total_ca:.2f} DH")
    st.metric("📉 Bénéfice Net", f"{benefice_net:.2f} DH")
    st.metric("🛒 Achats", f"{total_achats:.2f} DH")
    st.metric("💼 Charges", f"{total_charges:.2f} DH")
    st.metric("💰 Total", f"{(total_achats + total_charges):.2f} DH")

    if not achats_df.empty:
        st.subheader("📈 Répartition des Achats")
        achats_sum = achats_df.drop(columns=['id', 'date'], errors='ignore').sum()
        fig = px.pie(values=achats_sum.values, names=achats_sum.index)
        st.plotly_chart(fig, use_container_width=True)

    if not charges_df.empty:
        st.subheader("📈 Répartition des Charges")
        charges_sum = charges_df.drop(columns=['id', 'date', 'type_charge'], errors='ignore').sum()
        fig = px.pie(values=charges_sum.values, names=charges_sum.index)
        st.plotly_chart(fig, use_container_width=True)
