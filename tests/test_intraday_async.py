import asyncio
import time
import pandas as pd
import pytest
from utils import utils_intraday as mod

def test_intraday_async_fallback(monkeypatch):
    async def none_fetch(t, s):
        await asyncio.sleep(0.01)
        return None
    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2024-01-01")], "close": [1.0]})
    async def good_fetch(t, s):
        await asyncio.sleep(0.01)
        return sample
    monkeypatch.setattr(mod, "ASYNC_SOURCES", [
        ("src1", none_fetch),
        ("src2", good_fetch),
        ("src3", none_fetch),
    ])
    df = asyncio.run(mod.fetch_intraday_data_async("TSLA"))
    assert df is not None and not df.empty

def test_intraday_concurrent(monkeypatch):
    calls = []
    def slow(name):
        async def _f(t, s):
            calls.append(name)
            await asyncio.sleep(0.05)
            return None
        return _f
    monkeypatch.setattr(mod, "ASYNC_SOURCES", [
        ("a", slow("a")),
        ("b", slow("b")),
        ("c", slow("c")),
    ])
    start = time.perf_counter()
    asyncio.run(mod.fetch_intraday_data_async("TSLA"))
    elapsed = time.perf_counter() - start
    assert elapsed < 0.15
    assert set(calls) == {"a", "b", "c"}


def test_sync_wrapper(monkeypatch):
    sample = pd.DataFrame({"timestamp": [pd.Timestamp("2024-01-01")], "close": [1.0]})

    async def good(t, s):
        return sample

    monkeypatch.setattr(mod, "ASYNC_SOURCES", [("x", good)])
    df = mod.fetch_intraday_data("TSLA")
    assert isinstance(df, pd.DataFrame)
