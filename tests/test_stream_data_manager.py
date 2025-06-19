import importlib
from datetime import datetime
import types
import pytest
pd = pytest.importorskip("pandas")


def _reload_module(monkeypatch):
    class DummyWS:
        def run_forever(self):
            pass

    monkeypatch.setattr('websocket.WebSocketApp', lambda *a, **k: DummyWS())
    monkeypatch.setattr('threading.Thread', lambda *a, **k: type('T', (), {'start': lambda self: None})())
    return importlib.reload(importlib.import_module('data.stream_data_manager'))


def test_get_latest_data_fallback(monkeypatch):
    df = pd.DataFrame(
        {"Close": [3.12], "Volume": [900000]},
        index=[pd.Timestamp("2024-01-01T00:00:00")],
    )
    monkeypatch.setattr('yfinance.download', lambda *a, **k: df)
    module = _reload_module(monkeypatch)

    res = module.get_latest_data('AAA')
    assert res['price'] == 3.12
    assert res['volume'] == 900000
    assert res['source'] == 'FALLBACK'
    assert res['status'] == 'WARN'


def test_get_latest_data_ws_cache(monkeypatch):
    module = _reload_module(monkeypatch)
    module.latest_data['AAA'] = {
        'price': 3.12,
        'volume': 900000,
        'timestamp': '2024-01-01T00:00:00',
        'source': 'WS',
        'status': 'OK',
    }
    monkeypatch.setattr(
        module,
        'datetime',
        types.SimpleNamespace(
            utcnow=lambda: datetime(2024, 1, 1, 0, 0, 9),
            fromisoformat=module.datetime.fromisoformat,
        ),
    )
    res = module.get_latest_data('AAA')
    assert res['source'] == 'WS'
    assert res['status'] == 'OK'
    assert res['price'] == 3.12
