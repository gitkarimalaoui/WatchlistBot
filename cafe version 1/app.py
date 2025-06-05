import streamlit as st
from modules.database import init_database
from modules.interface_achats import interface_achats
from modules.interface_charges import interface_charges
from modules.interface_rapports import interface_rapports_mensuels, interface_rapports_annuels

st.set_page_config(page_title="Gestion Café", page_icon="☕", layout="wide")

def main():
    init_database()
    st.title("☕ Gestion de Café")
    st.sidebar.title("Navigation")

    pages = {
        "Saisie des Achats": interface_achats,
        "Saisie des Charges": interface_charges,
        "Rapports Mensuels": interface_rapports_mensuels,
        "Rapports Annuels": interface_rapports_annuels
    }

    choice = st.sidebar.selectbox("Choisir une page", list(pages.keys()))
    pages[choice]()

if __name__ == "__main__":
    main()
