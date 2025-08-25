from intelligence.ai_scorer import (
    score_ai,
    compute_global_score,
    load_model_by_version,
)

def test_score_ai_returns_value():
    sample = {"volume": 1000000, "float_shares": 20000000, "change_percent": 5}
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


def test_load_model_by_version_predictions():
    model = load_model_by_version("dummy_model_v1")
    pred0 = model.predict([[0]])[0]
    pred1 = model.predict([[1]])[0]
    assert pred0 == 0
    assert pred1 == 1
