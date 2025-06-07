
import os
import json
import pytest
from fusion.module_fusion_watchlist import fusionner_watchlists
import sys

# Ensure UTF-8 console output for emoji support
sys.stdout.reconfigure(encoding="utf-8")

def test_fusion_watchlist():
    if not (os.path.exists('data/watchlists/watchlist_manuelle.json') or os.path.exists('data/watchlists/watchlist_auto.json')):
        pytest.skip('watchlist files missing', allow_module_level=False)
    tickers = fusionner_watchlists()
    assert isinstance(tickers, list), "Résultat de la fusion n'est pas une liste"
    assert len(tickers) > 0, "La fusion retourne une liste vide"
    assert len(tickers) == len(set(tickers)), "La fusion contient des doublons"
    print("✅ Test de fusion de watchlist réussi avec", len(tickers), "tickers.")

if __name__ == "__main__":
    test_fusion_watchlist()
