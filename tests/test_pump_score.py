from pump_score import score_pump_ia


def test_score_pump_ia(monkeypatch):
    monkeypatch.setattr(
        "pump_score.get_latest_data",
        lambda t: {"price": 10, "volume": 1_000_000, "status": "OK"},
    )
    monkeypatch.setattr("pump_score.get_rsi", lambda t: 70)
    monkeypatch.setattr("pump_score.get_ema", lambda t, p: {9: 10, 21: 9})
    monkeypatch.setattr("pump_score.get_vwap", lambda t: 11)
    monkeypatch.setattr("pump_score.get_float", lambda t: 50_000_000)
    monkeypatch.setattr("pump_score.get_macd", lambda t: (1.5, 1.0))
    monkeypatch.setattr("pump_score.get_pump_pct", lambda t: 2.0)
    monkeypatch.setattr("pump_score.get_momentum", lambda t: 1.5)

    res = score_pump_ia("ABC")
    assert res["score"] == 90
    assert res["pump_pct_60s"] == 2.0
    assert res["status"] == "OK"
