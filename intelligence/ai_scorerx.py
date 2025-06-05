
import json

# Charger les règles (pondérations des critères)
with open("rules_auto.json", "r") as f:
    RULES = json.load(f)

def score_ai(ticker_data):
    """
    Calcule un score basé sur les règles pondérées définies dans rules_auto.json.
    ticker_data : dict avec les clés présentes dans les règles.
    Exemple attendu : {
        "price": 2.3,
        "volume": 1000000,
        "float": 15e6,
        "change_percent": 56.8
    }
    """
    score = 0
    for key, weight in RULES.items():
        value = ticker_data.get(key)
        if value is not None:
            try:
                score += weight * float(value)
            except (ValueError, TypeError):
                continue
    return round(score, 2)
