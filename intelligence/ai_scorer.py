"""AI scoring utilities."""

import json
import os

_RULES_PATH = os.path.join(os.path.dirname(__file__), "rules_auto.json")

with open(_RULES_PATH, "r", encoding="utf-8") as f:
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
