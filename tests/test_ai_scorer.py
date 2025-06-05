from intelligence.ai_scorer import score_ai

def test_score_ai_returns_value():
    sample = {"volume": 1000000, "float": 20000000, "change_percent": 5}
    result = score_ai(sample)
    assert isinstance(result, float)
