import importlib

import pytest


@pytest.fixture
def e2e_setup(monkeypatch, tmp_path):
    db_file = tmp_path / "trades.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    monkeypatch.setenv("TEST_MODE", "true")
    import core.db as core_db
    importlib.reload(core_db)
    from core import models
    models.Base.metadata.create_all(core_db.engine)
    yield str(db_file)


def test_end_to_end_trade_execution(e2e_setup, capsys):
    from decision_engine import DecisionEngine
    from simulation.execution_simulee import enregistrer_trade_simule
    from telegram_notifier import TelegramNotifier
    from core import db as core_db, models

    ticker_data = {
        "ticker": "XYZ",
        "score_ia": 85,
        "volume_ratio": 2.5,
        "price": 1.50,
        "target_price": 1.55,
        "has_fda": True,
    }

    engine = DecisionEngine()
    decision = engine.analyze_trade_decision(ticker_data)
    viability = engine.calculate_trade_viability(
        price_entry=1.50,
        price_target=1.55,
        quantity=1000,
        broker_fees={"commission_min": 1.0, "platform_fee_min": 1.0},
    )

    assert decision["confidence"] > 0.8
    assert viability["viable"]

    result = enregistrer_trade_simule("XYZ", 1.50, 1000, tp=1.55)

    notifier = TelegramNotifier()
    notifier.send_trade_alert("TRADE_EXECUTED", "XYZ", result)

    captured = capsys.readouterr()
    assert "TRADE_EXECUTED" in captured.out

    session = core_db.get_session()
    row = session.query(models.TradeSimule).filter_by(ticker="XYZ").first()
    session.close()
    assert row is not None and row.prix_achat == 1.50
