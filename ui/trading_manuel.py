import streamlit as st
from datetime import datetime
import json
import os

from utils.execution_reelle import executer_ordre_reel

st.set_page_config(page_title="🛠️ Trading manuel", layout="wide")
st.title("🛠️ Trading manuel")

journal_path = os.path.join("data", "journal_simule.json")


def enregistrer_achat(ticker, prix, simulation_ia="non"):
    nouveau_trade = {
        "ticker": ticker,
        "action": "achat",
        "prix": round(prix, 2),
        "gain_net": 0,
        "datetime": datetime.now().isoformat(),
        "simulation_ia": simulation_ia,
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
    st.success(f"Achat simulé enregistré pour `{ticker}` à {prix:.2f} $")


def enregistrer_vente(ticker, prix, simulation_ia="non"):
    nouveau_trade = {
        "ticker": ticker,
        "action": "vente",
        "prix": round(prix, 2),
        "gain_net": 0,
        "datetime": datetime.now().isoformat(),
        "simulation_ia": simulation_ia,
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
