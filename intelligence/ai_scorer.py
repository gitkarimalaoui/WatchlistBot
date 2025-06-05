with open("rules_auto.json", "r") as f:
    RULES = json.load(f)

def score_ai(ticker_data):
    score = 0
    for key, weight in RULES.items():
        value = ticker_data.get(key)
        if isinstance(weight, (int, float)) and value is not None:
            try:
                score += weight * float(value)
            except (ValueError, TypeError):
                continue
    return round(score, 2)
