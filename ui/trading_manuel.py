import streamlit as st
from datetime import datetime
from simulation.execution_simulee import enregistrer_trade_simule

from utils.execution_reelle import executer_ordre_reel

st.set_page_config(page_title="🛠️ Trading manuel", layout="wide")
st.title("🛠️ Trading manuel")



def enregistrer_achat(ticker, prix, quantite=1, sl=None, tp=None):
    """Enregistre un achat simulé directement en base."""
    enregistrer_trade_simule(
        ticker=ticker,
        entry_price=prix,
        quantity=quantite,
        sl=sl,
        tp=tp,
    )
    st.success(f"Achat simulé enregistré pour `{ticker}` à {prix:.2f} $")


def enregistrer_vente(ticker, prix, quantite=1, sl=None, tp=None):
    """Enregistre une vente simulée directement en base."""
    enregistrer_trade_simule(
        ticker=ticker,
        entry_price=prix,
        quantity=quantite,
        sl=sl,
        tp=tp,
        exit_price=prix,
    )
    st.success(f"Vente simulée enregistrée pour `{ticker}` à {prix:.2f} $")


ticker = st.text_input("🔤 Ticker", "")
prix = st.number_input("💵 Prix", min_value=0.0, step=0.01)
quantite = st.number_input("🔢 Quantité", min_value=1, step=1)
stop_loss = st.number_input("❗ Stop loss", min_value=0.0, step=0.01)

col1, col2, col3 = st.columns(3)

if col1.button("Simuler l'achat") and ticker and prix > 0:
    enregistrer_achat(ticker, prix)

if col2.button("Simuler la vente") and ticker and prix > 0:
    enregistrer_vente(ticker, prix)

if col3.button("Achat réel") and ticker and prix > 0 and quantite > 0:
    result = executer_ordre_reel(ticker, prix, int(quantite), "achat")
    if result["success"]:
        st.success(result["message"])
    else:
        st.error(result["message"])
