# scripts/batch_news_scoring.py

import sqlite3
import json
import hashlib
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DB_PATH = Path("data/trades.db")
USER_DATA_DIR = "C:/Users/KARIM/Desktop/chrome_profile_bot"  # same profile as Moomoo

def hash_desc(desc: str) -> str:
    return hashlib.sha256(desc.encode("utf-8")).hexdigest()

async def load_new_watchlist(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""
        SELECT w.ticker, w.description, n.desc_hash, n.last_analyzed, w.updated_at
        FROM watchlist w
        LEFT JOIN news_score n ON n.symbol = w.ticker
        WHERE w.description IS NOT NULL
    """).fetchall()
    conn.close()

    to_analyze = []
    for ticker, desc, old_hash, last_ana, updated_at in rows:
        new_hash = hash_desc(desc)
        if (old_hash is None
            or new_hash != old_hash
            or (last_ana is None and updated_at)
            or (last_ana and updated_at > last_ana)):
            to_analyze.append({"symbol": ticker, "desc": desc, "hash": new_hash})
    return to_analyze

def build_batch_prompt(watchlist, max_tickers=50):
    batch = [{"symbol": w["symbol"], "desc": w["desc"]} for w in watchlist[:max_tickers]]
    payload = {"tickers": batch}
    return (
        "Voici une liste de tickers et leurs descriptions :\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nPour chaque ticker, fournis :\n"
        + "1. \"symbol\"\n"
        + "2. \"summary\" (1–2 lignes)\n"
        + "3. \"score\" (0,1,3,5,7 ou 10 selon l’intérêt)\n\n"
        + "Réponds STRICTEMENT par un JSON : un tableau d’objets."
    )

async def chatgpt_batch_score(prompt: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False
        )
        page = await browser.new_page()
        await page.goto("https://chat.openai.com/")
        await page.wait_for_timeout(5000)

        textarea = await page.query_selector("textarea")
        await textarea.fill(prompt)
        await textarea.press("Enter")

        await page.wait_for_selector("div.markdown code", timeout=120000)
        code_blocks = await page.query_selector_all("div.markdown code")
        text = await code_blocks[-1].inner_text()
        await browser.close()

    return json.loads(text.strip())

def upsert_news_score(item, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO news_score(symbol, summary, score, desc_hash, last_analyzed)
        VALUES(?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(symbol) DO UPDATE SET
            summary=excluded.summary,
            score=excluded.score,
            desc_hash=excluded.desc_hash,
            last_analyzed=CURRENT_TIMESTAMP
    """, (item["symbol"], item["summary"], item["score"], item["hash"]))
    conn.commit()
    conn.close()

async def run_batch():
    to_analyze = await load_new_watchlist()
    if not to_analyze:
        return []
    prompt = build_batch_prompt(to_analyze)
    results = await chatgpt_batch_score(prompt)
    for item in results:
        upsert_news_score(item)
    return results

def run_batch_sync():
    """Synchronous entry point for Streamlit integration."""
    return asyncio.run(run_batch())
