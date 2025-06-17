import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_API_KEY:
    raise ValueError("FINNHUB_API_KEY not found in environment variables")
DEFAULT_KEYWORDS = ["FDA", "approval", "results", "study", "PR", "clinical"]


def fetch_news_finnhub(
    ticker: str, from_days: int = 2, keywords: Optional[List[str]] = None
) -> List[Dict]:
    if keywords is None:
        keywords = DEFAULT_KEYWORDS

    today = datetime.utcnow()
    from_date = (today - timedelta(days=from_days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    url = (
        f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={from_date}"
        f"&to={to_date}&token={FINNHUB_API_KEY}"
    )
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erreur API Finnhub pour {ticker}: {response.status_code}")
        return []

    articles = response.json()
    filtered = []

    for article in articles:
        headline = article.get("headline", "").lower()
        summary = article.get("summary", "").lower()
        if any(kw.lower() in headline or kw.lower() in summary for kw in keywords):
            filtered.append(
                {
                    "datetime": article.get("datetime"),
                    "headline": article.get("headline"),
                    "summary": article.get("summary"),
                    "url": article.get("url"),
                    "source": article.get("source"),
                }
            )

    return filtered
