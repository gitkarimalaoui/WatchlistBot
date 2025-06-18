import time
from movers_detector import update_price, get_pump_pct, get_top_movers


def test_get_top_movers(monkeypatch):
    prices = [100, 101.6]
    now = time.time()
    update_price("ABC", prices[0], now - 59)
    update_price("ABC", prices[1], now)

    monkeypatch.setattr(
        "movers_detector.get_latest_data",
        lambda t: {"price": prices[1], "volume": 1000, "status": "OK"},
    )

    res = get_top_movers(["ABC"])
    assert res
    assert res[0]["ticker"] == "ABC"
    assert res[0]["pump_pct_60s"] >= 1.5
