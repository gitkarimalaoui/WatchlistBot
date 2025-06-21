from typing import Dict, Optional

import yfinance as yf
import pandas as pd

try:
    import requests  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover - optional dep missing
    requests = None  # type: ignore
    BeautifulSoup = None  # type: ignore


def _fetch_pdufa_date(ticker: str) -> Optional[str]:
    """Return upcoming PDUFA date for ``ticker`` if available."""
    if requests is None or BeautifulSoup is None:
        return None
    try:
        url = f"https://www.biopharmcatalyst.com/company/{ticker.lower()}"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table tr")
        for row in rows:
            cells = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cells) >= 2 and "PDUFA" in cells[1].upper():
                try:
                    date = pd.to_datetime(cells[0]).date().isoformat()
                    return date
                except Exception:
                    continue
    except Exception:
        return None
    return None


def _get_key_fundamentals(ticker: str) -> Dict[str, Optional[float]]:
    """Fetch market cap, debt/equity ratio and cash runway from Yahoo Finance."""
    info = {}
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        info = {}
    market_cap = info.get("marketCap")
    total_debt = info.get("totalDebt")
    equity = info.get("totalStockholderEquity")
    cash = info.get("totalCash")
    operating_cf = info.get("operatingCashflow")
    de_ratio = (float(total_debt) / float(equity)) if total_debt and equity else None
    cash_runway = None
    try:
        if cash and operating_cf:
            monthly_cf = float(operating_cf) / 12.0
            if monthly_cf < 0:
                cash_runway = float(cash) / abs(monthly_cf)
    except Exception:
        cash_runway = None
    return {
        "market_cap": float(market_cap) if market_cap else None,
        "de_ratio": float(de_ratio) if de_ratio is not None else None,
        "cash_runway": float(cash_runway) if cash_runway is not None else None,
    }


def get_fundamental_data(ticker: str) -> Dict[str, Optional[float | str]]:
    """Return PDUFA date and fundamental metrics for ``ticker``."""
    data = _get_key_fundamentals(ticker)
    data["pdufa_date"] = _fetch_pdufa_date(ticker)
    return data
