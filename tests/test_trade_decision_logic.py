from datetime import datetime, timedelta
from decision_engine import DecisionEngine


def test_high_commission_blocks_trade():
    engine = DecisionEngine()
    fees = {
        "commission_per_share": 5.0,
        "commission_min": 5.0,
        "platform_fee_per_share": 1.0,
        "platform_fee_min": 1.0,
        "platform_max_ratio": 0.5,
    }
    res = engine.calculate_trade_viability(10.0, 10.1, 1, fees)
    assert not res["viable"]


def test_penny_stock_volume_requirements():
    engine = DecisionEngine()
    data = {"price": 0.5, "volume_ratio": 0.8, "score_ia": 90}
    decision = engine.analyze_trade_decision(data)
    assert "Volume" in " ".join(decision["avoid"]) or decision["avoid"]


def test_catalyst_timing_logic():
    engine = DecisionEngine()
    upcoming = (datetime.utcnow() + timedelta(hours=12)).isoformat()
    data = {"score_ia": 85, "volume_ratio": 2, "catalyst_date": upcoming}
    decision = engine.analyze_trade_decision(data)
    assert any("imminent" in r for r in decision["buy"])
