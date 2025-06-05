from utils.check_tickers import filtrer_tickers_valides

from pages.analyse_tickers import analyser_ticker_fusion
from simulations.simulation_achat import enregistrer_trade
from simulations.simulation_vente import enregistrer_vente
import time
import random
import sys

# Ensure UTF-8 console output for emoji support
sys.stdout.reconfigure(encoding="utf-8")

WATCHLIST = ["CMND", "RSLS", "TCTM", "AAPL", "GME"]

SCORE_SEUIL = 7
TP_PCT = 0.05  # Take Profit 5%
SL_PCT = 0.03  # Stop Loss 3%

def run_learning_loop():
    print("=== LANCEMENT DE LA BOUCLE D'APPRENTISSAGE IA ===")
    for ticker in WATCHLIST:
        print(f"Analyse de {ticker}...")
        resultats = analyser_ticker_fusion(ticker)
        score = resultats.get("score", 0)
        prix_achat = resultats.get("prix", 0)

        if score >= SCORE_SEUIL and prix_achat > 0:
            print(f"✅ Opportunité détectée (Score: {score}) -> Achat simulé de {ticker} à {prix_achat}")
            trade = enregistrer_trade(ticker, prix_achat, 100)

            # Simulation virtuelle d'évolution du prix (à remplacer par vrai suivi si besoin)
            coef = random.uniform(1 - SL_PCT, 1 + TP_PCT)
            prix_vente = round(prix_achat * coef, 2)
            time.sleep(0.5)  # Simule une attente courte

            resultat_vente = enregistrer_vente(ticker, prix_vente)
            print(f"💵 Vente simulée de {ticker} à {prix_vente} (variation: {round((prix_vente - prix_achat) / prix_achat * 100, 2)}%)")

        else:
            print(f"⛔ Ticker ignoré (score {score})")

    print("=== FIN DE LA BOUCLE IA ===")
