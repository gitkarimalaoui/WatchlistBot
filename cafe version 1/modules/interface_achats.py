import streamlit as st
from datetime import date
from modules.database import insert_achat_quotidien

def interface_achats():
    st.header("📝 Saisie des Achats Quotidiens")
    date_achat = st.date_input("Date d'achat", value=date.today())

    st.subheader("Produits")
    fields = ["lait", "sucre", "eau", "viennoiserie", "pain", "the", "bonbon_gaz",
              "banane", "pomme", "olive", "orange", "produit_nettoyage", "semoule", "fromage"]

    values = {}
    for i in range(0, len(fields), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(fields):
                field = fields[i + j]
                values[field] = cols[j].number_input(field.replace("_", " ").title(), min_value=0.0, step=0.1, format="%.2f")

    if st.button("💾 Enregistrer les Achats"):
        insert_achat_quotidien(str(date_achat), values)
        st.success(f"✅ Achats du {date_achat} enregistrés avec succès !")
