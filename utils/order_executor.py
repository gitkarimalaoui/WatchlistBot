
import sqlite3
from datetime import datetime
import streamlit as st

from executer_ordre_moomoo import executer_ordre  # Appel du module réel

# Fonction de simulation de l'ordre
def simuler_ordre(ticker, prix_achat, quantite, frais, prix_cible, stop_loss):
    montant_total = prix_achat * quantite
    frais_total = max(frais["commission_min"], frais["commission"] * quantite) +                   min(montant_total * frais["plateforme_max_pct"], max(frais["plateforme_min"], frais["plateforme"] * quantite))

    conn = sqlite3.connect("trades.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades_simules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            prix_achat REAL,
            quantite INTEGER,
            frais_total REAL,
            prix_cible REAL,
            stop_loss REAL,
            date TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO trades_simules (ticker, prix_achat, quantite, frais_total, prix_cible, stop_loss, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticker, prix_achat, quantite, frais_total, prix_cible, stop_loss, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return {
        "ticker": ticker,
        "montant_total": montant_total,
        "frais_total": frais_total,
        "prix_cible": prix_cible,
        "stop_loss": stop_loss
    }

# Nouvelle fonction pour exécution réelle (sans confirmation utilisateur)
def executer_ordre_reel_direct(ticker, prix_achat, quantite):
    try:
        executer_ordre(ticker, prix_achat, quantite)
        return True, f"✅ Ordre réel envoyé pour {ticker} à {prix_achat} x {quantite}"
    except Exception as e:
        return False, f"❌ Échec lors de l'exécution réelle : {e}"
