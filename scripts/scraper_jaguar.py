# scripts/scraper_jaguar.py

import asyncio
import re
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Paths and URLs
BASE_DIR       = Path(__file__).parents[1]
WATCHLIST_PATH = BASE_DIR / "data" / "watchlist_jaguar.txt"
PROFILE_URL    = "https://www.moomoo.com/community/profile/jaguar-8-73431062"
USER_DATA_DIR  = r"C:/Users/KARIM/Desktop/chrome_profile_bot"

def extraire_tickers_et_descriptions(texte):
    """
    Extract (TICKER, DESCRIPTION) pairs from concatenated post text.
    Matches patterns like: $Company Name (TICKER.US)$
    """
    pattern = r'\$([^\$()]+)\s+\(([A-Z]{1,5})\.US\)\$'
    matches = re.findall(pattern, texte)
    results = []
    for company, ticker in matches:
        idx = texte.find(f"${company}")
        extrait = texte[max(0, idx - 80): idx + len(company) + 20]
        extrait = extrait.replace('\n', ' ').strip().replace('|', '-')
        results.append((ticker.strip(), extrait))
    return results

async def scraper_watchlist():
    # 1) Launch browser and fetch posts
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=True
        )
        page = await browser.new_page()
        await page.goto(PROFILE_URL)
        await page.wait_for_timeout(5000)

        blocks = await page.query_selector_all('div[data-feed-rich-text-type="p"]')
        texte_concat = "\n---\n".join([await b.inner_text() for b in blocks])

        await browser.close()

    # 2) Extract tickers & descriptions
    tickers_descs = extraire_tickers_et_descriptions(texte_concat)

    # 3) Write to TXT file
    os.makedirs(WATCHLIST_PATH.parent, exist_ok=True)
    with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
        for ticker, desc in tickers_descs:
            f.write(f"{ticker} | {desc}\n")

    # Plain ASCII status message
    print(f"Scraper complete: {len(tickers_descs)} tickers extracted to {WATCHLIST_PATH}")

if __name__ == "__main__":
    asyncio.run(scraper_watchlist())
