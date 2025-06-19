import streamlit as st
import pandas as pd
from watchlist_panel import render_watchlist_panel
from intelligence.training.utils_ai_predictor import charger_modele
from fusion.module_fusion_watchlist import charger_watchlists_sources
from intelligence.features.check_tickers import analyser_ticker

st.set_page_config(page_title="📊 Analyse IA des Tickers", layout="wide")
st.title("📊 Analyse complète des tickers (IA + Watchlist Fusionnée)")

MODELE_PATH = "models/modele_ia.pkl"

# Charger le modèle IA
try:
    modele = charger_modele(MODELE_PATH)
    st.success("✅ Modèle IA chargé.")
except Exception as e:
    modele = None
    st.warning(f"⚠️ Modèle IA non disponible : {e}")

# Charger la watchlist fusionnée
watchlist = charger_watchlists_sources()
if not watchlist:
    st.warning("Aucun ticker trouvé dans la watchlist fusionnée.")
    st.stop()

resultats = []
for ticker_obj in watchlist:
    symbol = ticker_obj.get("symbol")
    provenance = ticker_obj.get("provenance", "inconnue")
    try:
        features = analyser_ticker(symbol, return_features=True)
        if features and modele:
            score = modele.predict_proba([features])[0][1]
            resultats.append({
                "symbol": symbol,
                "score_ia": round(score * 100, 2),
                "provenance": provenance
            })
        else:
            resultats.append({
                "symbol": symbol,
                "score_ia": "Non évalué",
                "provenance": provenance
            })
    except Exception as e:
        resultats.append({
            "symbol": symbol,
            "score_ia": "Erreur",
            "provenance": provenance
        })

df = pd.DataFrame(resultats)
st.dataframe(df, use_container_width=True)
render_watchlist_panel()
