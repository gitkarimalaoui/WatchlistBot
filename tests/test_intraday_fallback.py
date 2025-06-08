import pandas as pd
import importlib
from utils import utils_intraday as mod


def test_intraday_fallback(monkeypatch):
    monkeypatch.setattr(mod, "fetch_from_yfinance", lambda t: pd.DataFrame())
    monkeypatch.setattr(mod, "fetch_from_finnhub", lambda t: pd.DataFrame())
    monkeypatch.setattr(mod, "fetch_from_alphavantage", lambda t: pd.DataFrame())
    monkeypatch.setattr(mod, "fetch_from_fmp", lambda t: pd.DataFrame())
    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2024-01-01")], "close": [1.0]})
    monkeypatch.setattr(mod, "fetch_from_polygon", lambda t: sample)
    monkeypatch.setattr(mod, "SOURCES", [("Polygon", mod.fetch_from_polygon)])
    df = mod.fetch_intraday_data("TSLA")
    assert df is not None
    assert not df.empty


def test_intraday_missing_keys(monkeypatch):
    monkeypatch.delenv("FINNHUB_API_KEY", raising=False)
    monkeypatch.delenv("ALPHA_VANTAGE_API_KEY", raising=False)
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)

    mod_reload = importlib.reload(mod)
    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2024-01-01")], "close": [1.0]})
    monkeypatch.setattr(mod_reload, "fetch_from_yfinance", lambda t: sample)
    monkeypatch.setattr(mod_reload, "SOURCES", [("YF", mod_reload.fetch_from_yfinance)])

    df = mod_reload.fetch_intraday_data("TSLA")
    assert df is not None
    assert not df.empty


def test_intraday_custom_keys(monkeypatch):
    monkeypatch.setenv("FINNHUB_API_KEY", "X")
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "Y")
    monkeypatch.setenv("FMP_API_KEY", "Z")
    monkeypatch.setenv("POLYGON_API_KEY", "A")

    mod_reload = importlib.reload(mod)
    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2024-01-01")], "close": [1.0]})
    monkeypatch.setattr(mod_reload, "fetch_from_finnhub", lambda t: sample)
    monkeypatch.setattr(mod_reload, "SOURCES", [("Finnhub", mod_reload.fetch_from_finnhub)])

    df = mod_reload.fetch_intraday_data("TSLA")
    assert df is not None
    assert not df.empty
