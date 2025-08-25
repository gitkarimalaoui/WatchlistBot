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
from typing import Any, Dict, Iterable, List, Set

import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).resolve().parents[1] / "data" / "trades.db"))
DEFAULT_KEYWORDS = ["fda", "approval", "results", "pr", "study", "clinical", "drug"]


def get_recent_news_from_finnhub(days: int = 2) -> List[Dict[str, Any]]:
    """Fetch recent general news and filter to the last ``days`` days."""
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
    recent: List[Dict[str, Any]] = []
    for art in articles:
        ts = art.get("datetime")
        if ts is None:
            continue
        try:
            dt = datetime.utcfromtimestamp(int(ts))
        except Exception:
            continue
        if dt >= cutoff:
            recent.append(
                {
                    "title": art.get("headline", ""),
                    "summary": art.get("summary", ""),
                    "date": dt.isoformat(),
                    "url": art.get("url", ""),
                    "source": art.get("source", ""),
                    "related": art.get("related", ""),
                }
            )
    return recent


def extract_tickers_from_news(news_list: Iterable[Dict[str, Any]]) -> List[str]:
    """Extract potential US tickers from news items."""
    pattern = re.compile(r"(?:\$|\(|\[)([A-Z]{1,5})(?:\)|\]|)")
    tickers: Set[str] = set()
    for news in news_list:
        text = f"{news.get('title', '')} {news.get('summary', '')}"
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


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create required tables if they don't already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            source TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS watchlist_set_updated_at
        AFTER UPDATE ON watchlist
        FOR EACH ROW
        BEGIN
            UPDATE watchlist SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS news_by_ticker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            title TEXT,
            summary TEXT,
            url TEXT,
            source TEXT,
            UNIQUE(ticker, date)
        )
        """
    )
    conn.commit()


def insert_news_ticker_in_watchlist(conn: sqlite3.Connection, ticker: str, news_data: Dict[str, Any]) -> bool:
    """Insert or update a ticker in watchlist and record its news.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active connection to the database.
    ticker : str
        Symbol to insert/update.
    news_data : Dict[str, Any]
        News dictionary with keys ``title``, ``summary``, ``date``, ``url`` and ``source``.

    Returns
    -------
    bool
        ``True`` if a new ticker was inserted, ``False`` otherwise.
    """

    row = conn.execute(
        "SELECT 1 FROM watchlist WHERE ticker = ?",
        (ticker,),
    ).fetchone()
    inserted = row is None

    if inserted:
        conn.execute(
            """
            INSERT INTO watchlist (ticker, source, description)
            VALUES (?, 'NewsAuto', ?)
            """,
            (ticker, news_data.get("title", "")[:200]),
        )
    else:
        conn.execute(
            """
            UPDATE watchlist
            SET source = CASE WHEN instr(COALESCE(source, ''), 'NewsAuto') > 0
                               THEN source
                               ELSE COALESCE(source, '') || ' | NewsAuto' END
            WHERE ticker = ?
            """,
            (ticker,),
        )

    conn.execute(
        """
        INSERT OR IGNORE INTO news_by_ticker (ticker, date, title, summary, url, source)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ticker,
            news_data.get("date"),
            news_data.get("title"),
            news_data.get("summary"),
            news_data.get("url"),
            news_data.get("source"),
        ),
    )
    conn.commit()
    return inserted


def main() -> None:
    news = get_recent_news_from_finnhub()
    if not news:
        print("No recent news found")
        return

    conn = sqlite3.connect(DB_PATH)
    _ensure_schema(conn)

    added = 0
    updated = 0

    for article in news:
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        if not any(kw in text for kw in DEFAULT_KEYWORDS):
            continue

        tickers = extract_tickers_from_news([article])
        if not tickers:
            continue

        for t in tickers:
            if not validate_ticker(t):
                continue
            inserted = insert_news_ticker_in_watchlist(conn, t, article)
            if inserted:
                added += 1
            else:
                updated += 1

    conn.close()

    if added or updated:
        if added:
            print(f"✅ {added} nouveaux tickers ajoutés à la watchlist")
        if updated:
            print(f"🔁 {updated} tickers mis à jour avec des news récentes")
    else:
        print("No valid tickers found")


if __name__ == "__main__":
    main()
