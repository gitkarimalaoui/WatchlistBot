
import streamlit as st
from datetime import datetime
from simulation.execution_simulee import enregistrer_trade_simule

st.set_page_config(page_title="🔴 Simulation Vente", layout="wide")
st.title("🔴 Simulation de vente manuelle")

def enregistrer_vente(ticker, prix, quantite=1, sl=None, tp=None):
    """Enregistre une vente simulée dans la base."""
    enregistrer_trade_simule(
        ticker=ticker,
        entry_price=prix,
        quantity=quantite,
        sl=sl,
        tp=tp,
        exit_price=prix,
    )
    st.success(f"Vente simulée enregistrée pour `{ticker}` à {prix:.2f} $")

# Interface utilisateur
ticker = st.text_input("🔤 Ticker", "")
prix = st.number_input("💰 Prix de vente", min_value=0.0, step=0.01)

if st.button("Simuler la vente") and ticker and prix > 0:
    enregistrer_vente(ticker, prix)
