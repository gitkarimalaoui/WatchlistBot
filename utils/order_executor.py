
from datetime import datetime
import streamlit as st

from sqlalchemy.orm import Session
from core.db import get_session
from core.models import TradeSimule

from executer_ordre_moomoo import executer_ordre  # Appel du module réel

# Fonction de simulation de l'ordre
def simuler_ordre(ticker, prix_achat, quantite, frais, prix_cible, stop_loss):
    montant_total = prix_achat * quantite
    frais_total = max(frais["commission_min"], frais["commission"] * quantite) +                   min(montant_total * frais["plateforme_max_pct"], max(frais["plateforme_min"], frais["plateforme"] * quantite))
    session = get_session()
    trade = TradeSimule(
        ticker=ticker,
        prix_achat=prix_achat,
        quantite=quantite,
        frais=frais_total,
        montant_total=montant_total,
        sl=stop_loss,
        tp=prix_cible,
        exit_price=None,
        provenance="manuel",
        date=datetime.now(),
        note=""
    )
    session.add(trade)
    session.commit()
    session.close()

    return {
        "ticker": ticker,
        "montant_total": montant_total,
        "frais_total": frais_total,
        "prix_cible": prix_cible,
        "stop_loss": stop_loss
    }

# Nouvelle fonction pour exécution réelle (sans confirmation utilisateur)
def executer_ordre_reel_direct(ticker, prix_achat, quantite, stop_loss=None):
    try:
        executer_ordre(ticker, prix_achat, quantite, stop_loss)
        sl_msg = f" avec stop loss {stop_loss}" if stop_loss else ""
        return True, f"✅ Ordre réel envoyé pour {ticker} à {prix_achat} x {quantite}{sl_msg}"
    except Exception as e:
        return False, f"❌ Échec lors de l'exécution réelle : {e}"
