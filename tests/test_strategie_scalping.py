import importlib
from datetime import datetime
import pytest
pd = pytest.importorskip("pandas")

STRAT_PATH = 'execution.strategie_scalping'


def _setup_indicators(monkeypatch):
    monkeypatch.setattr(f'{STRAT_PATH}.get_rsi', lambda t: 70)
    monkeypatch.setattr(f'{STRAT_PATH}.get_ema', lambda t, p: {9: 2.0, 21: 1.0})
    monkeypatch.setattr(f'{STRAT_PATH}.get_vwap', lambda t: 10.0)
    monkeypatch.setattr(f'{STRAT_PATH}.get_macd', lambda t: (1.0, 0.0))
    monkeypatch.setattr(f'{STRAT_PATH}.get_volume', lambda t, i="1m": 900000 if i=="1m" else 100000)
    monkeypatch.setattr(f'{STRAT_PATH}.get_last_price', lambda t: 3.12)
    monkeypatch.setattr(f'{STRAT_PATH}.get_price_5s_ago', lambda t: 3.0)
    monkeypatch.setattr(f'{STRAT_PATH}.get_float', lambda t: 50_000_000)
    monkeypatch.setattr(f'{STRAT_PATH}.get_catalyseur_score', lambda t: 0.8)
    monkeypatch.setattr(f'{STRAT_PATH}.check_breakout_sustain', lambda m,v1,v2: True)
    monkeypatch.setattr(f'{STRAT_PATH}.get_atr', lambda t: 0.5)
    df_gap = pd.DataFrame({
        'Open': [1.0, 1.1],
        'Close': [1.0, 1.0],
    }, index=pd.date_range('2024-01-01', periods=2))
    monkeypatch.setattr('yfinance.download', lambda *a, **k: df_gap)
    monkeypatch.setattr(f'{STRAT_PATH}.get_latest_data', lambda t: {
        'price': 3.12,
        'volume': 900000,
        'timestamp': '2024-01-01T00:00:00',
        'source': 'WS',
        'status': 'OK',
    })


def test_compute_score(monkeypatch):
    strat = importlib.import_module(STRAT_PATH)
    _setup_indicators(monkeypatch)
    res = strat._compute_score('AAA')
    assert res['score'] == 100
    assert res['source'] == 'WS'
    assert res['atr'] == 0.5
    assert res['gap_pct'] == pytest.approx(10.0)


def test_executer_strategie_scalping(monkeypatch):
    strat = importlib.import_module(STRAT_PATH)
    _setup_indicators(monkeypatch)
    monkeypatch.setattr(strat, '_compute_score', lambda t: {
        'score': 100,
        'price': 3.12,
        'momentum': 1.05,
        'volume': 900000,
        'source': 'WS',
        'atr': 0.5,
        'gap_pct': 10.0,
        'stop_loss': 3.0,
        'take_profit': 3.2,
        'trailing_atr': 0.7,
    })
    monkeypatch.setattr(strat, 'get_nb_trades_du_jour', lambda t, d: 0)
    monkeypatch.setattr(strat, 'executer_ordre_reel', lambda *a, **k: {'status': 'filled'})
    alerts = []
    monkeypatch.setattr(strat, 'envoyer_alerte_ia', lambda *a, **k: alerts.append(a))
    trades = []
    monkeypatch.setattr(strat, 'enregistrer_trade_auto', lambda *a, **k: trades.append(a))
    monkeypatch.setattr(strat.time, 'sleep', lambda s: None)

    class FakeDT:
        @classmethod
        def utcnow(cls):
            return datetime(2024, 1, 1, 15, 0, 0)

    monkeypatch.setattr(strat, 'datetime', FakeDT)

    res = strat.executer_strategie_scalping('AAA')
    assert res['ordre'] == {'status': 'filled'}
    assert alerts
    assert trades
