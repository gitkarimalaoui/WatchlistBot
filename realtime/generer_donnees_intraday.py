
# realtime/generer_donnees_intraday.py

from realtime.build_intraday_candles import build_candles
from realtime.utils_graph_local import generer_graphique_local

def generer_donnees_ticker(ticker: str, forcer=False):
    try:
        print(f"[⏳] Génération des données pour {ticker}...")

        # Appels de génération
        build_candles(ticker)
        generer_graphique_local(ticker)

        print(f"[✔] Données intraday générées pour {ticker}")
    except Exception as e:
        print(f"[❌] Erreur lors de la génération pour {ticker} : {e}")
