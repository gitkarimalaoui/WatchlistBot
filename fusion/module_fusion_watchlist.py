
import json
import os

def charger_watchlists_sources(path_manuel='data/watchlists/watchlist_manuelle.json',
                                path_auto='data/watchlists/watchlist_auto.json',
                                path_ia='data/watchlists/watchlist_ia.json'):
    watchlists = {}

    # Charger chaque fichier s'il existe
    for label, path in [('manuel', path_manuel), ('auto', path_auto), ('ia', path_ia)]:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    watchlists[label] = json.load(f)
            except Exception as e:
                watchlists[label] = []
                print(f"[Erreur chargement {label}] {e}")
        else:
            watchlists[label] = []

    # Marquer la provenance et fusionner
    fusion = []
    for label, liste in watchlists.items():
        for ticker in liste:
            if isinstance(ticker, dict):
                ticker['provenance'] = label
                fusion.append(ticker)
            elif isinstance(ticker, str):
                fusion.append({'symbol': ticker, 'provenance': label})
    
    return fusion
