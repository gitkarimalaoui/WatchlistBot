import streamlit as st
from datetime import date
from modules.database import insert_charges_fixes

def interface_charges():
    """Streamlit UI for fixed charge entry.

    Returns:
        None
    """

    st.header("💼 Saisie des Charges Fixes")
    date_charge = st.date_input("Date", value=date.today())
    type_charge = st.selectbox("Type de charge", ["Hebdomadaire", "Mensuelle", "Annuelle"])

    salaires = ["serveur_1", "serveur_2", "barman_1", "barman_2", "femme_menage_1", "femme_menage_2"]
    autres = ["wifi", "electricite", "eau_magasin", "taxe_debit_boisson", "tva", "comptable", "taxe_professionnelle", "is_impot", "taxe_locale_terrasse"]

    st.subheader("Salaires")
    salaires_data = {s: st.number_input(s.replace("_", " ").title(), min_value=0.0, step=0.1, format="%.2f") for s in salaires}

    st.subheader("Autres Charges")
    autres_data = {a: st.number_input(a.replace("_", " ").title(), min_value=0.0, step=0.1, format="%.2f") for a in autres}

    data = {**salaires_data, **autres_data}

    if st.button("💾 Enregistrer les Charges"):
        insert_charges_fixes(str(date_charge), type_charge, data)
        st.success(f"✅ Charges {type_charge.lower()}s du {date_charge} enregistrées !")
