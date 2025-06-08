import pandas as pd
import pytest
from utils import utils_intraday as intra
from utils import utils_yf_historical as hist

@pytest.mark.asyncio
async def test_async_intraday_fallback(monkeypatch):
    monkeypatch.setattr(intra, "async_fetch_from_yfinance", lambda t: pd.DataFrame())
    monkeypatch.setattr(intra, "async_fetch_from_finnhub", lambda t: pd.DataFrame())
    monkeypatch.setattr(intra, "async_fetch_from_alphavantage", lambda t: pd.DataFrame())
    monkeypatch.setattr(intra, "async_fetch_from_fmp", lambda t: pd.DataFrame())
    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2024-01-01")], "close": [1.0]})
    monkeypatch.setattr(intra, "async_fetch_from_polygon", lambda t: sample)
    monkeypatch.setattr(intra, "ASYNC_SOURCES", [("Polygon", intra.async_fetch_from_polygon)])
    df = await intra.async_fetch_intraday_data("TSLA")
    assert df is not None
    assert not df.empty

@pytest.mark.asyncio
async def test_async_historical_fallback(monkeypatch):
    monkeypatch.setattr(hist, "async_fetch_from_yfinance", lambda t: pd.DataFrame())
    monkeypatch.setattr(hist, "async_fetch_from_finnhub", lambda t: pd.DataFrame())
    monkeypatch.setattr(hist, "async_fetch_from_alphavantage", lambda t: pd.DataFrame())
    monkeypatch.setattr(hist, "async_fetch_from_fmp", lambda t: pd.DataFrame())
    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2024-01-01")], "close": [1.0]})
    monkeypatch.setattr(hist, "async_fetch_from_polygon", lambda t: sample)
    monkeypatch.setattr(hist, "ASYNC_SOURCES", [("Polygon", hist.async_fetch_from_polygon)])
    df = await hist.async_fetch_historical_data("TSLA")
    assert df is not None
    assert not df.empty
