import re

FEATURES = [
    "manual_input",
    "filter_by_source",
    "batch_analysis",
    "scraper_jaguar",
    "display_metrics",
]

def test_features_markers():
    text = open("ui/app_unifie_watchlistbot.py", encoding="utf-8").read()
    for feat in FEATURES:
        assert re.search(fr"# FEATURE: {feat}", text), f"Missing FEATURE: {feat}"
        assert re.search(fr"# /FEATURE: {feat}", text), f"Missing end marker for {feat}"
