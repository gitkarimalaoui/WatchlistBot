
import os

def test_scraping_output():
    os.system("python scrapers/jaguar.py")
    assert os.path.exists("data/watchlist_jaguar.txt"), "Le fichier scraping n'a pas été généré"
