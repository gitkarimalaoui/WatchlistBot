"""Automatic ticker detection from pharma-related news.

This script fetches recent news articles via Finnhub, extracts tickers
mentioned in those articles, validates them using yfinance and stores
them in the ``watchlist`` table with source "NewsAuto".
"""

from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trades.db"
DEFAULT_KEYWORDS = ["fda", "approval", "results", "pr", "study"]


def get_recent_news_from_finnhub(days: int = 2) -> List[Dict]:
    """Return recent general news articles within ``days`` days."""
    if not FINNHUB_API_KEY:
        print("FINNHUB_API_KEY missing")
        return []

    url = "https://finnhub.io/api/v1/news"
    params = {"category": "general", "token": FINNHUB_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json()
    except Exception as exc:
        print(f"[ERROR] Finnhub news fetch failed: {exc}")
        return []

    cutoff = datetime.utcnow() - timedelta(days=days)
    recent: List[Dict] = []
    for art in articles:
        ts = art.get("datetime")
        if ts is None:
            continue
        try:
            dt = datetime.utcfromtimestamp(int(ts))
        except Exception:
            continue
        if dt >= cutoff:
            recent.append(art)
    return recent


def extract_tickers_from_news(news_list: List[Dict]) -> List[str]:
    """Extract potential US tickers from news items."""
    pattern = re.compile(r"(?:\$|\[)([A-Z]{1,5})(?:\]|)")
    tickers = set()
    for news in news_list:
        text = f"{news.get('headline','')} {news.get('summary','')}"
        for match in pattern.finditer(text):
            tickers.add(match.group(1))
        related = news.get("related", "")
        for t in related.split(','):
            t = t.strip().upper()
            if 0 < len(t) <= 5:
                tickers.add(t)
    return list(tickers)


def validate_ticker(ticker: str) -> bool:
    """Check basic liquidity requirements using yfinance."""
    try:
        info = yf.Ticker(ticker).fast_info
    except Exception as exc:
        print(f"[WARN] yfinance lookup failed for {ticker}: {exc}")
        return False

    price = info.get("lastPrice") or info.get("last_price")
    volume = info.get("lastVolume") or info.get("tenDayAverageVolume")
    shares = info.get("shares")

    if price is None or volume is None or shares is None:
        return False
    if price <= 0 or volume < 500_000 or shares > 200_000_000:
        return False
    return True


def insert_news_ticker_in_watchlist(ticker: str, news_data: Dict) -> None:
    """Upsert ticker into watchlist with provenance ``NewsAuto``."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO watchlist (ticker, source, date, description, updated_at)
            VALUES (?, 'NewsAuto', ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ticker) DO UPDATE SET
                source=CASE WHEN instr(source, 'NewsAuto') > 0 THEN source
                             ELSE COALESCE(source, '') || ' | NewsAuto' END,
                date=excluded.date,
                description=excluded.description,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                ticker,
                datetime.utcnow().isoformat(),
                news_data.get("headline", "")[:200],
            ),
        )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    news = get_recent_news_from_finnhub()
    if not news:
        print("No recent news found")
        return

    filtered = [
        n
        for n in news
        if any(kw in (n.get("headline", "") + n.get("summary", "")).lower() for kw in DEFAULT_KEYWORDS)
    ]

    extracted = extract_tickers_from_news(filtered)
    if not extracted:
        print("No tickers detected")
        return

    inserted = []
    for t in extracted:
        if validate_ticker(t):
            insert_news_ticker_in_watchlist(t, filtered[0])
            inserted.append(t)

    if inserted:
        print("Inserted tickers:", ", ".join(inserted))
    else:
        print("No valid tickers found")


if __name__ == "__main__":
    main()
