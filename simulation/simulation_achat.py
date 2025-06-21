
import streamlit as st
from datetime import datetime
from simulation.execution_simulee import enregistrer_trade_simule

st.set_page_config(page_title="🟢 Simulation Achat", layout="wide")
st.title("🟢 Simulation d'achat manuel")

def enregistrer_achat(ticker, prix, quantite=1, sl=None, tp=None):
    """Enregistre un achat simulé dans la base."""
    enregistrer_trade_simule(
        ticker=ticker,
        entry_price=prix,
        quantity=quantite,
        sl=sl,
        tp=tp,
    )
    st.success(f"Achat simulé enregistré pour `{ticker}` à {prix:.2f} $")

# Interface utilisateur
ticker = st.text_input("🔤 Ticker", "")
prix = st.number_input("💵 Prix d'achat", min_value=0.0, step=0.01)

if st.button("Simuler l'achat") and ticker and prix > 0:
    enregistrer_achat(ticker, prix)
