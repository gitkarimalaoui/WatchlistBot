from __future__ import annotations

import asyncio
import os
import time
from typing import Dict, Any, Iterable, List

import aiohttp

from utils.market_scheduler import is_market_open
from pump_score import score_pump_ia
from utils.telegram_utils import send_telegram_message

_API_KEY = os.getenv("FINNHUB_API_KEY", "")
_CACHE: Dict[str, float] = {}


def _dedup(symbols: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for sym in symbols:
        base = sym.split(".")[0].upper()
        if base not in seen:
            seen.add(base)
            result.append(base)
    return result


async def _get_stock_candles(session: aiohttp.ClientSession, symbol: str) -> Dict[str, Any]:
    end = int(time.time())
    params = {
        "symbol": symbol,
        "resolution": "1",
        "from": end - 15 * 60,
        "to": end,
        "token": _API_KEY,
    }
    url = "https://finnhub.io/api/v1/stock/candle"
    for attempt in range(3):
        async with session.get(url, params=params) as resp:
            if resp.status == 429:
                await asyncio.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return await resp.json()
    return {}


def detect_pump(candles: Dict[str, Any]) -> bool:
    closes = candles.get("c", [])
    volumes = candles.get("v", [])
    if len(closes) < 2 or len(volumes) < 11:
        return False
    price_change = (closes[-1] - closes[-2]) / closes[-2] * 100
    avg_volume = sum(volumes[-11:-1]) / 10
    volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1
    return price_change >= 3.0 and volume_ratio >= 1.5


async def run_full_analysis(symbol: str) -> None:
    res = score_pump_ia(symbol)
    if res.get("score", 0) >= 80:
        send_telegram_message(
            f"Pump détecté sur {symbol} (score IA {res['score']})"
        )


async def scan_watchlist(watchlist: Iterable[str]) -> None:
    tickers = _dedup(watchlist)
    async with aiohttp.ClientSession() as session:
        while True:
            if not is_market_open():
                await asyncio.sleep(60)
                continue
            for symbol in tickers:
                last = _CACHE.get(symbol, 0.0)
                if time.time() - last < 60:
                    continue
                candles = await _get_stock_candles(session, symbol)
                _CACHE[symbol] = time.time()
                if detect_pump(candles):
                    await run_full_analysis(symbol)
            await asyncio.sleep(15)


if __name__ == "__main__":  # pragma: no cover - manual run
    wl_path = os.path.join("data", "watchlist_jaguar.txt")
    if os.path.exists(wl_path):
        with open(wl_path, "r", encoding="utf-8") as f:
            wl = [l.strip() for l in f if l.strip()]
    else:
        wl = []
    asyncio.run(scan_watchlist(wl))
