import importlib

import os

def test_env_keys_loading(monkeypatch):
    monkeypatch.setenv("FMP_API_KEY", "dummy")
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "dummy2")
    monkeypatch.setenv("POLYGON_API_KEY", "dummy3")
    monkeypatch.setenv("FINNHUB_API_KEY", "dummy4")
    import utils.utils_intraday as mod
    importlib.reload(mod)
    assert mod.FMP_API_KEY == "dummy"
    assert mod.ALPHA_VANTAGE_API_KEY == "dummy2"
    assert mod.POLYGON_API_KEY == "dummy3"
    assert mod.FINNHUB_API_KEY == "dummy4"
