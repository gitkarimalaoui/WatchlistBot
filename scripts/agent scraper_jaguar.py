# scripts/scraper_jaguar.py

import asyncio
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import sys

# Ensure UTF-8 console output for emoji support
sys.stdout.reconfigure(encoding="utf-8")

# ——— Configuration ———
DB_PATH        = Path(__file__).parents[1] / "data" / "trades.db"
USER_DATA_DIR  = r"C:/Users/KARIM/Desktop/chrome_profile_bot"
JAGUAR_URL     = "https://www.moomoo.com/community/profile/jaguar-8-73431062"

# ——— Scraping + DB logic ———
async def scrape_and_upsert():
    # 1) Fetch posts
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR, headless=True
        )
        page = await browser.new_page()
        await page.goto(JAGUAR_URL)
        await page.wait_for_timeout(5000)

        elems = await page.query_selector_all('div[data-feed-rich-text-type="p"]')
        posts = []
        for el in elems:
            text = (await el.inner_text()).strip()
            m = re.match(r".*\\$(?P<ticker>\\w+)\\$\\s*(?P<desc>.+)", text)
            if m:
                posts.append({
                    "ticker": m.group("ticker"),
                    "description": m.group("desc").strip()
                })
        await browser.close()

    # 2) Upsert into watchlist
    conn = sqlite3.connect(DB_PATH)
    for post in posts:
        conn.execute("""
            INSERT INTO watchlist
              (ticker, source, date, description, updated_at)
            VALUES (?, 'Jaguar', ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ticker) DO UPDATE SET
              source=excluded.source,
              date=excluded.date,
              description=excluded.description,
              updated_at=CURRENT_TIMESTAMP
        """, (
            post["ticker"],
            datetime.now().isoformat(),
            post["description"]
        ))
    conn.commit()
    conn.close()

    print(f"✅ Scraped and upserted {len(posts)} Jaguar posts.")

# ——— Entry point ———
if __name__ == "__main__":
    asyncio.run(scrape_and_upsert())
