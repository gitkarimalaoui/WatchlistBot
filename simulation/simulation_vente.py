
import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="🔴 Simulation Vente", layout="wide")
st.title("🔴 Simulation de vente manuelle")

journal_path = os.path.join("data", "journal_simule.json")

def enregistrer_vente(ticker, prix, simulation_ia="non"):
    nouveau_trade = {
        "ticker": ticker,
        "action": "vente",
        "prix": round(prix, 2),
        "gain_net": 0,
        "datetime": datetime.now().isoformat(),
        "simulation_ia": simulation_ia
    }

    if os.path.exists(journal_path):
        with open(journal_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(nouveau_trade)

    with open(journal_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    st.success(f"Vente simulée enregistrée pour `{ticker}` à {prix:.2f} $")

# Interface utilisateur
ticker = st.text_input("🔤 Ticker", "")
prix = st.number_input("💰 Prix de vente", min_value=0.0, step=0.01)

if st.button("Simuler la vente") and ticker and prix > 0:
    enregistrer_vente(ticker, prix)
