from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

from config.config_manager import _load_dotenv, config_manager

# Ensure environment variables are loaded
_load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY") or config_manager.get("finnhub_api")


def _missing_key() -> bool:
    return not FINNHUB_API_KEY or "your_default_api_key_here" in str(FINNHUB_API_KEY)


def fetch_news_finnhub(
    ticker: str,
    from_days: int = 2,
    keywords: Optional[List[str]] = None,
) -> List[Dict]:
    """Retrieve recent Finnhub news for ``ticker`` and filter by keywords.

    Parameters
    ----------
    ticker : str
        Stock symbol (e.g. "SNPX").
    from_days : int, optional
        Number of days to look back from today. Default is 2.
    keywords : list[str], optional
        Keywords used to filter news headlines and summaries.

    Returns
    -------
    list[dict]
        Filtered news entries with ``datetime``, ``headline``, ``summary``, ``url``
        and ``source`` fields.
    """

    if keywords is None:
        keywords = ["FDA", "approval", "results", "study", "PR", "clinical"]

    if _missing_key():
        return []

    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=from_days)

    params = {
        "symbol": ticker,
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "token": FINNHUB_API_KEY,
    }

    try:
        response = requests.get(
            "https://finnhub.io/api/v1/company-news", params=params, timeout=10
        )
        response.raise_for_status()
        items = response.json()
    except Exception:
        return []

    kw_lower = [k.lower() for k in keywords]
    results: List[Dict] = []
    for item in items:
        headline = item.get("headline", "")
        summary = item.get("summary", "")
        text = f"{headline} {summary}".lower()
        if any(k in text for k in kw_lower):
            results.append(
                {
                    "datetime": item.get("datetime"),
                    "headline": headline,
                    "summary": summary,
                    "url": item.get("url"),
                    "source": item.get("source"),
                }
            )

    return results
