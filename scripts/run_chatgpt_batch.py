import asyncio
import logging
import requests
import sqlite3
import os
import platform
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.info

DB_PATH = Path(__file__).parent.parent / "data" / "trades.db"

print("Chemin relatif DB utilisé :", DB_PATH)
print("Chemin absolu DB :", DB_PATH.resolve())
print("Dossier courant (cwd) :", os.getcwd())
print("Chemin complet du script :", Path(__file__).resolve())

def log_debug_prompt():
    """Log useful environment details to help troubleshoot errors."""
    details = [
        "=== DEBUG PROMPT (copier-coller ci-dessous) ===",
        f"Python: {platform.python_version()}",
        f"OS: {platform.platform()}",
        f"Working dir: {os.getcwd()}",
        f"DB path: {DB_PATH.resolve()}",
        f"Script path: {Path(__file__).resolve()}",
        "Collez ce bloc lors d'une demande d'assistance pour accélérer le diagnostic.",
        "==============================================="
    ]
    log("\n".join(details))

PROMPT_INSTRUCTIONS = """\
Tu es un expert en day trading. Voici une liste de tickers avec leurs descriptions de news.
Analyse chaque ligne et fournis un score parmi [0,1,3,5,7,10] selon l’importance du catalyseur et le sentiment associé.
Réponds UNIQUEMENT avec un tableau CSV, chaque ligne au format symbol|score|sentiment. Aucun texte supplémentaire.
"""

MAX_DESC_CHARS = 200

def load_watchlist():
    """Charge les tickers et descriptions depuis la base SQLite, tronque chaque description."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker, description FROM watchlist WHERE description IS NOT NULL"
    ).fetchall()
    conn.close()

    unique = {}
    for ticker, desc in rows:
        text = desc.strip().replace("\n", " ")
        if len(text) > MAX_DESC_CHARS:
            text = text[:MAX_DESC_CHARS] + "..."
        if ticker not in unique and text:
            unique[ticker] = text
    return [{"symbol": t, "desc": d} for t, d in unique.items()]

def build_prompt(symbols):
    """Construit le prompt complet à injecter dans ChatGPT."""
    lines = [f"{s['symbol']}|{s['desc']}" for s in symbols]
    return PROMPT_INSTRUCTIONS + "\n" + "\n".join(lines)

def save_chat_history(prompt, response):
    """Enregistre le prompt et la réponse dans la table chatgpt_history."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO chatgpt_history(prompt, response) VALUES (?, ?)",
        (prompt, response)
    )
    conn.commit()
    conn.close()

def save_scores_from_response(response):
    """Parse la réponse ligne par ligne et enregistre dans news_score."""
    conn = sqlite3.connect(DB_PATH)
    saved = 0
    for line in response.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3:
            sym, sc, sent = parts
            try:
                sc_int = int(sc)
                conn.execute(
                    """
                    INSERT INTO news_score(symbol, score, sentiment, last_analyzed)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(symbol) DO UPDATE SET
                      score=excluded.score,
                      sentiment=excluded.sentiment,
                      last_analyzed=CURRENT_TIMESTAMP
                    """,
                    (sym, sc_int, sent)
                )
                saved += 1
            except ValueError:
                continue
    conn.commit()
    conn.close()
    log(f"✅ {saved} scores enregistrés.")

def get_browser_websocket_url():
    try:
        r = requests.get("http://localhost:9222/json/version")
        r.raise_for_status()
        return r.json()["webSocketDebuggerUrl"]
    except Exception as e:
        raise Exception(f"[FATAL] Impossible d'obtenir WebSocket URL du navigateur: {e}")

async def get_chatgpt_response(page, timeout_sec=90):
    """Attend et récupère la réponse ChatGPT sous forme de bloc code markdown contenant '|'."""
    raw = ""
    for _ in range(timeout_sec):
        await asyncio.sleep(1)
        blocks = await page.query_selector_all("div.markdown code")
        if blocks:
            candidate = await blocks[-1].inner_text()
            if "|" in candidate:
                raw = candidate
                break
    return raw

async def chatgpt_inject(prompt: str):
    ws_url = get_browser_websocket_url()
    log(f"[INFO] Connexion au navigateur via WebSocket: {ws_url}")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_url)

        all_pages = [pg for ctx in browser.contexts for pg in ctx.pages]
        log(f"[DEBUG] Nombre total de pages détectées : {len(all_pages)}")

        page = next((pg for pg in all_pages if "chat.openai.com" in pg.url), None)

        if not page:
            log("[WARN] Aucune page ChatGPT trouvée, création d'une nouvelle page...")
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await ctx.new_page()
            await page.goto("https://chat.openai.com/")
            await page.wait_for_load_state("domcontentloaded")
            log("[INFO] Nouvelle page ChatGPT ouverte.")

        # Inject prompt in the visible contenteditable div
        await page.evaluate(f"""
            (prompt) => {{
                const pm = document.querySelector('#prompt-textarea');
                if(pm) {{
                    pm.focus();
                    pm.innerText = prompt;
                    const event = new InputEvent('input', {{bubbles: true}});
                    pm.dispatchEvent(event);
                    return true;
                }}
                return false;
            }}
        """, prompt)

        log("Prompt injecté dans #prompt-textarea")

        # Simuler appui sur ENTRÉE sur le prompt textarea (élément contenteditable)
        await page.keyboard.press("Enter")
        log("⏎ Touche ENTRÉE simulée sur #prompt-textarea")

        # Attente de la réponse (90 secondes)
        raw_response = await get_chatgpt_response(page, timeout_sec=90)
        log(f"[INFO] Réponse brute récupérée ({len(raw_response)} caractères)")

        save_chat_history(prompt, raw_response)

        await browser.close()
        log("✅ Fermeture du navigateur Playwright.")

        return raw_response

async def run_batch():
    symbols = load_watchlist()
    if not symbols:
        log("Aucun ticker à scorer.")
        return

    prompt = build_prompt(symbols)
    log("[INFO] Prompt généré.")

    response = await chatgpt_inject(prompt)
    if not response:
        log("Aucune réponse reçue.")
        return

    save_scores_from_response(response)

if __name__ == "__main__":
    try:
        log_debug_prompt()
        asyncio.run(run_batch())
    except Exception as e:
        logging.error(f"Exception non gérée: {e}")
        log_debug_prompt()
        raise
