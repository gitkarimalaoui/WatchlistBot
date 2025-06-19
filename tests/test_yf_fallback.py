import types
import pytest
pd = pytest.importorskip("pandas")
from utils import utils_yf_historical as mod


def test_fallback(monkeypatch):
    # simulate missing data from yfinance
    dummy_yf = types.SimpleNamespace()
    dummy_yf.download = lambda *a, **k: pd.DataFrame()
    dummy_yf.Ticker = lambda t: types.SimpleNamespace(history=lambda **k: pd.DataFrame())
    monkeypatch.setattr(mod, "yf", dummy_yf, raising=False)

    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2020-01-01")], "close": [1.0]})
    monkeypatch.setattr(mod, "fetch_finnhub_historical_data", lambda t: sample)

    df = mod.fetch_historical_with_fallback("TSLA")
    assert df is not None
    assert not df.empty
    df = df[["timestamp", "close"]]
    assert list(df.columns) == ["timestamp", "close"]

