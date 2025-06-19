from __future__ import annotations
import os
import time
from datetime import datetime, time as dt_time, timedelta, timezone
from typing import Optional
import requests
from config.config_manager import _load_dotenv

_load_dotenv()
_FINNHUB = os.getenv("FINNHUB_API_KEY")
_CACHE = {"ts": 0.0, "open": False}


def _is_open_local(now: Optional[datetime] = None) -> bool:
    now = now or datetime.utcnow()
    ny = now.astimezone(timezone(timedelta(hours=-4)))
    if ny.weekday() >= 5:
        return False
    return dt_time(9, 30) <= ny.time() <= dt_time(16, 0)


def is_market_open() -> bool:
    """Return ``True`` if US markets are currently open."""
    now = time.time()
    if now - _CACHE["ts"] < 60:
        return bool(_CACHE["open"])
    state = _is_open_local()
    if state and _FINNHUB:
        try:
            resp = requests.get(
                "https://finnhub.io/api/v1/stock/market-status",
                params={"exchange": "US", "token": _FINNHUB},
                timeout=5,
            )
            data = resp.json()
            state = bool(data.get("isOpen", state))
        except Exception:
            pass
    _CACHE["ts"] = now
    _CACHE["open"] = state
    return state
