
import json
from v6.utils.module_fusion_watchlist import fusionner_watchlists

def test_fusion_watchlist():
    tickers = fusionner_watchlists()
    assert isinstance(tickers, list), "Résultat de la fusion n'est pas une liste"
    assert len(tickers) > 0, "La fusion retourne une liste vide"
    assert len(tickers) == len(set(tickers)), "La fusion contient des doublons"
    print("✅ Test de fusion de watchlist réussi avec", len(tickers), "tickers.")

if __name__ == "__main__":
    test_fusion_watchlist()
