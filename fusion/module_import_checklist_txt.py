
import re

def extraire_tickers_depuis_txt(filepath):
    tickers = set()

    with open(filepath, "r", encoding="utf-8") as f:
        contenu = f.read()

        # Trouve tous les symboles de type $TICKER (avec ou sans .US)
        matches = re.findall(r"\$(\w+)(\.US)?", contenu)
        for match in matches:
            ticker = match[0].upper()
            if 1 < len(ticker) <= 6:  # filtrer les mots trop courts ou anormaux
                tickers.add(ticker)

    return sorted(tickers)
