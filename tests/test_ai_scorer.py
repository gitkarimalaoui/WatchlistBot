from intelligence.ai_scorer import score_ai, compute_global_score

def test_score_ai_returns_value():
    sample = {"volume": 1000000, "float": 20000000, "change_percent": 5}
    result = score_ai(sample)
    assert isinstance(result, float)


def test_compute_global_score_range():
    score = compute_global_score(
        score_ai_val=5,
        gpt_score=7,
        percent_gain=10,
        volume=1_000_000,
        float_shares=20_000_000,
        sentiment="positif",
    )
    assert isinstance(score, float)
    assert 0 <= score <= 10
