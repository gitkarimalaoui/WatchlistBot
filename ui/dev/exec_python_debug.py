
import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="🧪 Zone avancée - Exécution & Maintenance", layout="wide")
st.title("🧪 Zone avancée - Exécution Python, Historique & Maintenance")

HISTORY_PATH = os.path.join("logs", "exec_history.json")
JOURNAL_PATH = os.path.join("data", "journal_simule.json")
IA_PATH = os.path.join("config", "meta_ia.json")

if not os.path.exists("logs"):
    os.makedirs("logs")

# Chargement historique
if os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []

# Zone d’exécution de code
st.subheader("▶️ Exécuter du code Python")
code_input = st.text_area("Code à exécuter :", height=250, value="from journal import enregistrer_trade_auto\nenregistrer_trade_auto(ticker='TEST', action='achat', prix=1.0, montant=100, frais=0.5, provenance='test')")

col1, col2 = st.columns([1, 2])
with col1:
    run_code = st.button("▶️ Exécuter")
with col2:
    save_code = st.button("💾 Sauvegarder dans l’historique")

if run_code:
    try:
        exec(code_input, globals())
        st.success("✅ Code exécuté avec succès.")
    except Exception as e:
        st.error(f"❌ Erreur : {e}")

if save_code:
    history.append({
        "timestamp": datetime.now().isoformat(),
        "code": code_input
    })
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    st.success("💾 Script ajouté à l’historique.")

# Historique
if history:
    st.subheader("🕓 Historique des scripts enregistrés")
    for item in reversed(history[-5:]):
        st.code(item["code"], language="python")

# Maintenance
st.subheader("🧹 Outils de nettoyage")

col3, col4 = st.columns(2)

with col3:
    if st.button("❌ Réinitialiser le journal des trades"):
        if os.path.exists(JOURNAL_PATH):
            os.remove(JOURNAL_PATH)
        st.success("✅ Journal supprimé.")

with col4:
    if st.button("♻️ Réinitialiser la base IA"):
        with open(IA_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        st.success("✅ Base IA vidée.")
