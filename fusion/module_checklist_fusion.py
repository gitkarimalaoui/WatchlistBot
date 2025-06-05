
import pandas as pd
import os
import json

# Chargement automatique des différentes sources si disponibles
def charger_sources_checklist():
    meta_ia, tickers_manuels, rules_auto = {}, [], {}
    txt_content = ""
    csv_data = pd.DataFrame()

    # Checklist IA
    try:
        with open("config/meta_ia.json", "r") as f:
            meta_ia = json.load(f)
    except:
        meta_ia = {}

    # Checklist manuelle
    try:
        with open("data/tickers_manuels.json", "r") as f:
            tickers_manuels = json.load(f)
    except:
        tickers_manuels = []

    # Règles automatiques
    try:
        with open("config/rules_auto.json", "r") as f:
            rules_auto = json.load(f)
    except:
        rules_auto = {}

    # Checklist .txt
    try:
        with open("data/WatchList.txt", "r") as f:
            txt_content = f.read()
    except:
        txt_content = ""

    # Checklist .csv
    try:
        csv_data = pd.read_csv("data/WatchList.csv")
    except:
        csv_data = pd.DataFrame()

    return {
        "ia": meta_ia,
        "manuels": tickers_manuels,
        "rules": rules_auto,
        "txt_checklist": txt_content,
        "csv_checklist": csv_data
    }

# Fusion manuelle + IA
def fusionner_tous_les_tickers(meta_ia, tickers_manuels):
    tickers = set(tickers_manuels)
    tickers.update(meta_ia.keys())
    return list(tickers)

# Génération de checklist enrichie
def generer_checklist_fusionnee(meta_ia, rules_auto, tickers_total, tickers_manuels):
    resultat = []
    for ticker in tickers_total:
        origine = []
        if ticker in tickers_manuels:
            origine.append("Manuel")
        if ticker in meta_ia:
            origine.append("IA")
        score = meta_ia.get(ticker, {}).get("score", 0)
        mots_cles = meta_ia.get(ticker, {}).get("mots_cles_news", [])
        volume = meta_ia.get(ticker, {}).get("volume", 0)
        gain_pct = meta_ia.get(ticker, {}).get("gain_pct", 0)
        float_max = meta_ia.get(ticker, {}).get("float", 0)

        resultat.append({
            "Ticker": ticker,
            "Origine": ", ".join(origine),
            "Score IA": score,
            "mots_cles_news": ", ".join(mots_cles) if mots_cles else "",
            "Check mots_cles_news": "✅" if mots_cles else "❌",
            "seuil_gain_pour_selection": gain_pct,
            "Check seuil_gain_pour_selection": "✅" if gain_pct > rules_auto.get("gain_pct_min", 0) else "❌",
            "seuil_volume": volume,
            "Check seuil_volume": "✅" if volume > rules_auto.get("volume_min", 0) else "❌",
            "float_max": float_max,
            "Check float_max": "✅" if float_max < rules_auto.get("float_max", 99999999) else "❌",
        })

    return pd.DataFrame(resultat)
