import pandas as pd
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
