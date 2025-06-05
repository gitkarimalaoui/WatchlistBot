
import os

def test_watchlist_file_exists():
    assert os.path.exists("data/watchlist_jaguar.txt"), "Le fichier watchlist_jaguar.txt est manquant"
