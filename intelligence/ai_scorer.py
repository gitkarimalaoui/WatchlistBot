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


def compute_global_score(
    score_ai_val,
    gpt_score,
    percent_gain,
    volume,
    float_shares,
    sentiment,
):
    """Blend multiple indicators into a single global score on a 0-10 scale."""

    def _safe_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    import math

    score_ai_norm = max(0.0, min(_safe_float(score_ai_val) / 10.0, 1.0))
    gpt_norm = max(0.0, min(_safe_float(gpt_score) / 10.0, 1.0))

    pct = _safe_float(percent_gain)
    pct_norm = (max(min(pct / 20.0, 1.0), -1.0) + 1.0) / 2.0

    vol = _safe_float(volume)
    vol_norm = min(math.log10(vol + 1) / 8.0, 1.0) if vol > 0 else 0.0

    flt = _safe_float(float_shares)
    flt_norm = 1.0 - min(math.log10(flt + 1) / 9.0, 1.0) if flt > 0 else 0.0

    s = str(sentiment or "").lower()
    if "pos" in s:
        sent_val = 1.0
    elif "neg" in s:
        sent_val = -1.0
    else:
        sent_val = 0.0
    sent_norm = (sent_val + 1.0) / 2.0

    metrics = [score_ai_norm, gpt_norm, pct_norm, vol_norm, flt_norm, sent_norm]
    return round(sum(metrics) / len(metrics) * 10.0, 2)
