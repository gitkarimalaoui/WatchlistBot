import asyncio
import logging
import sqlite3
import json
import os
import platform
import subprocess
import time
import hashlib
from datetime import datetime
from pathlib import Path


from intelligence.token_utils import count_tokens

# ---- Logging configuration ----
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "run_chatgpt_batch.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    force=True,
)

log = logging.info

# Persistent Chrome profile directory
PROFILE_DIR = Path.home() / ".watchlistbot_chrome"
PROFILE_DIR.mkdir(exist_ok=True)

DB_PATH = Path(__file__).parent.parent / "data" / "trades.db"

log(f"Chemin relatif DB utilisé : {DB_PATH}")
log(f"Chemin absolu DB : {DB_PATH.resolve()}")
log(f"Dossier courant (cwd) : {os.getcwd()}")
log(f"Chemin complet du script : {Path(__file__).resolve()}")


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
        "===============================================",
    ]
    log("\n".join(details))


PROMPT_INSTRUCTIONS = """\
Tu es un expert en day trading. Voici une liste de tickers avec leurs descriptions de news.
Analyse chaque ligne et fournis un score parmi [0,1,3,5,7,10] selon l'importance du catalyseur et le sentiment associé.
Réponds UNIQUEMENT avec un tableau CSV, chaque ligne au format symbol|score|sentiment. Aucun texte supplémentaire.
"""

MAX_DESC_CHARS = 200


def hash_desc(desc: str) -> str:
    """Return SHA256 hash for the given description."""
    return hashlib.sha256(desc.encode("utf-8")).hexdigest()


def load_watchlist():
    """Return entries needing (re)analysis and count of skipped ones."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT w.ticker, w.description, n.desc_hash, n.last_analyzed
        FROM watchlist w
        LEFT JOIN news_score n ON n.symbol = w.ticker
        WHERE w.description IS NOT NULL
        """
    ).fetchall()
    conn.close()

    to_analyze = []
    skipped = 0
    today = datetime.now().date()

    for ticker, desc, old_hash, last_ana in rows:
        text = desc.strip().replace("\n", " ")
        if len(text) > MAX_DESC_CHARS:
            text = text[:MAX_DESC_CHARS] + "..."
        new_hash = hash_desc(text)
        up_to_date = (
            old_hash == new_hash
            and last_ana
            and datetime.fromisoformat(last_ana).date() == today
        )
        if text and not up_to_date:
            to_analyze.append({"symbol": ticker, "desc": text, "hash": new_hash})
        else:
            skipped += 1

    log(f"[INFO] {skipped} lignes ignorées, {len(to_analyze)} à traiter")
    return to_analyze


def build_prompt(symbols, max_tokens: int = 1800):
    """Construit le prompt en plusieurs blocs de taille raisonnable.

    Parameters
    ----------
    symbols : list | str
        Liste de dictionnaires ``{"symbol": .., "desc": ..}`` ou chaine déjà
        formatée. Dans ce dernier cas, l'ancien comportement est conservé.
    max_tokens : int, optional
        Nombre maximum de tokens par bloc retourné.

    Returns
    -------
    list[str] | str
        Une liste de prompts ne dépassant pas ``max_tokens`` tokens ou une chaine
        unique si l'entrée était une chaine.
    """

    if isinstance(symbols, str):
        return PROMPT_INSTRUCTIONS + "\n" + symbols

    lines = [f"{s['symbol']}|{s['desc']}" for s in symbols]
    chunks = []
    current = []
    tokens = count_tokens(PROMPT_INSTRUCTIONS)
    newline_token_count = count_tokens("\n")
    for line in lines:
        line_tokens = count_tokens(line)
        if tokens + line_tokens + newline_token_count > max_tokens and current:
            chunks.append(PROMPT_INSTRUCTIONS + "\n" + "\n".join(current))
            current = [line]
            tokens = count_tokens(PROMPT_INSTRUCTIONS) + newline_token_count + line_tokens
        else:
            tokens += newline_token_count
            current.append(line)
            tokens += line_tokens
    if current:
        chunks.append(PROMPT_INSTRUCTIONS + "\n" + "\n".join(current))

    return chunks if len(chunks) > 1 else chunks[0]


def save_chat_history(prompt, response):
    """Enregistre le prompt et la réponse dans la table chatgpt_history."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO chatgpt_history(prompt, response) VALUES (?, ?)",
        (prompt, response),
    )
    conn.commit()
    conn.close()


def save_scores_from_response(response, desc_hash_map=None):
    """Enregistre des scores dans la table ``news_score``.

    ``response`` peut être soit la chaîne CSV originale retournée par ChatGPT,
    soit une liste d'objets ``{"symbol": .., "score": .., "sentiment": ..,
    "summary": ..}`` générée par le LLM local.
    """

    conn = sqlite3.connect(DB_PATH)
    saved = 0

    if isinstance(response, str):
        try:
            parsed = json.loads(response)
        except Exception:
            parsed = None

        if parsed is not None:
            if isinstance(parsed, dict):
                items = [parsed]
            else:
                items = list(parsed)
        else:
            lines = response.splitlines()
            items = []
            for line in lines:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    items.append({"symbol": parts[0], "score": parts[1], "sentiment": parts[2]})
    else:
        items = list(response)

    for obj in items:
        sym = obj.get("symbol")
        sent = obj.get("sentiment")
        summary = obj.get("summary")
        try:
            sc_int = int(obj.get("score"))
        except (TypeError, ValueError):
            continue
        if not sym:
            continue
        desc_hash = desc_hash_map.get(sym) if desc_hash_map else None
        conn.execute(
            """
            INSERT INTO news_score(symbol, summary, score, sentiment, last_analyzed, desc_hash)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ON CONFLICT(symbol) DO UPDATE SET
              summary=excluded.summary,
              score=excluded.score,
              sentiment=excluded.sentiment,
              last_analyzed=CURRENT_TIMESTAMP,
              desc_hash=excluded.desc_hash
            """,
            (sym, summary, sc_int, sent, desc_hash),
        )
        conn.execute(
            "UPDATE watchlist SET score=? WHERE ticker=?",
            (sc_int, sym),
        )
        saved += 1

    conn.commit()
    conn.close()
    log(f"✅ {saved} scores enregistrés.")


def find_chrome_executable():
    """Find Chrome executable path based on OS."""
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser(
                r"~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
            ),
        ]
    elif platform.system() == "Darwin":
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    else:
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def is_chrome_running_with_debug():
    """Check if Chrome is already running with debug port."""
    import requests
    try:
        response = requests.get("http://localhost:9222/json/version", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def kill_existing_chrome(force_restart: bool = False):
    """Kill existing Chrome processes if force_restart is True."""
    if not force_restart:
        return

    log("[INFO] Fermeture des processus Chrome existants...")
    import psutil
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if "chrome" in proc.info["name"].lower():
                proc.kill()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass


def start_chrome_with_debug(force_restart: bool = False):
    """Start Chrome with debugging enabled."""
    if is_chrome_running_with_debug() and not force_restart:
        log("[INFO] Chrome avec port de debug déjà en cours d'exécution.")
        return True

    chrome_path = find_chrome_executable()
    if not chrome_path:
        log("[ERROR] Chrome non trouvé. Veuillez installer Google Chrome.")
        return False

    log(f"[INFO] Chrome trouvé: {chrome_path}")

    kill_existing_chrome(force_restart)
    if force_restart:
        time.sleep(2)

    chrome_args = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-default-apps",
        "--disable-popup-blocking",
        "https://chat.openai.com/",
    ]

    try:
        subprocess.Popen(
            chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log("[INFO] Chrome démarré avec port de debug...")

        for _ in range(30):
            if is_chrome_running_with_debug():
                log("[INFO] Chrome prêt avec port de debug!")
                return True
            time.sleep(1)

        log("[ERROR] Chrome n'a pas pu démarrer avec le port de debug.")
        return False

    except Exception as e:
        log(f"[ERROR] Erreur lors du démarrage de Chrome: {e}")
        return False


def get_browser_websocket_url(force_restart: bool = False):
    """Get the WebSocket URL for browser debugging."""
    if not start_chrome_with_debug(force_restart=force_restart):
        raise Exception("[FATAL] Impossible de démarrer Chrome avec le port de debug.")

    try:
        import requests
        r = requests.get("http://localhost:9222/json/version", timeout=5)
        r.raise_for_status()
        return r.json()["webSocketDebuggerUrl"]
    except Exception as e:
        raise Exception(
            f"[FATAL] Impossible d'obtenir WebSocket URL du navigateur: {e}"
        )


async def get_chatgpt_response(page, timeout_sec=90):
    """Attend et récupère la réponse ChatGPT sous forme de bloc code markdown contenant '|'."""
    log("[INFO] Attente de la réponse ChatGPT...")
    raw = ""

    for i in range(timeout_sec):
        await asyncio.sleep(1)

        blocks = await page.query_selector_all("div.markdown code")
        if blocks:
            candidate = await blocks[-1].inner_text()
            if "|" in candidate and len(candidate.split("\n")) > 2:
                raw = candidate
                log(f"[INFO] Réponse détectée après {i+1} secondes")
                break

        if (i + 1) % 10 == 0:
            log(f"[INFO] Attente... {i+1}/{timeout_sec} secondes")

    if not raw:
        log("[WARN] Aucune réponse valide détectée dans le délai imparti")

    return raw


async def chatgpt_inject(prompt: str):
    """Inject prompt into ChatGPT and get response."""
    from playwright.async_api import async_playwright
    ws_url = get_browser_websocket_url()
    log("[INFO] Connexion au navigateur via WebSocket")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(ws_url)
            log("[INFO] Connexion Playwright établie")

            all_pages = [pg for ctx in browser.contexts for pg in ctx.pages]
            log(f"[DEBUG] Nombre total de pages détectées : {len(all_pages)}")

            page = None
            for pg in all_pages:
                try:
                    if "chat.openai.com" in pg.url:
                        page = pg
                        break
                except Exception:
                    continue

            if not page:
                log("[INFO] Création d'une nouvelle page ChatGPT...")
                ctx = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = await ctx.new_page()
                await page.goto("https://chat.openai.com/")
                await page.wait_for_load_state("domcontentloaded")
                log("[INFO] Page ChatGPT chargée")

            await asyncio.sleep(3)

            selectors_to_try = [
                "#prompt-textarea",
                'div[contenteditable="true"]',
                'textarea[placeholder*="Message"]',
                'div[data-testid="textbox"]',
            ]

            input_found = False
            for selector in selectors_to_try:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        log(f"[INFO] Zone de saisie trouvée: {selector}")

                        await element.click()
                        await page.keyboard.down("Control")
                        await page.keyboard.press("a")
                        await page.keyboard.up("Control")
                        await element.fill(prompt)

                        log("[INFO] Prompt injecté")
                        input_found = True
                        break
                except Exception as e:
                    log(f"[DEBUG] Sélecteur {selector} échoué: {e}")
                    continue

            if not input_found:
                raise Exception("Zone de saisie ChatGPT non trouvée")

            await page.keyboard.press("Enter")
            log("[INFO] Prompt envoyé")

            raw_response = await get_chatgpt_response(page, timeout_sec=120)

            if raw_response:
                log(f"[INFO] Réponse récupérée ({len(raw_response)} caractères)")
                save_chat_history(prompt, raw_response)
            else:
                log("[WARN] Aucune réponse valide reçue")

            await browser.close()
            log("✅ Navigateur fermé")

            return raw_response

        except Exception as e:
            log(f"[ERROR] Erreur dans chatgpt_inject: {e}")
            try:
                await browser.close()
            except Exception:
                pass
            raise


async def run_batch():
    """Main function to run the batch analysis."""
    try:
        entries = load_watchlist()
        if not entries:
            log("Aucun ticker à scorer.")
            return

        log(f"[INFO] {len(entries)} tickers à analyser")
        hash_map = {e["symbol"]: e.get("hash") for e in entries}
        prompt_chunks = build_prompt([{"symbol": e["symbol"], "desc": e["desc"]} for e in entries])
        if isinstance(prompt_chunks, list):
            # Concatène les blocs pour ChatGPT en ne gardant les instructions qu'une fois
            instr_lines = PROMPT_INSTRUCTIONS.splitlines()
            all_lines = []
            for idx, chunk in enumerate(prompt_chunks):
                lines = chunk.splitlines()
                if idx == 0:
                    all_lines.extend(lines)
                else:
                    all_lines.extend(lines[len(instr_lines) :])
            prompt = "\n".join(all_lines)
        else:
            prompt = prompt_chunks

        log("[INFO] Prompt généré")
        log("=== PROMPT UTILISÉ ===")
        log(prompt)
        log("=== FIN PROMPT ===")

        response = await chatgpt_inject(prompt)
        if not response:
            log("[ERROR] Aucune réponse reçue de ChatGPT")
            return

        save_scores_from_response(response, desc_hash_map=hash_map)
        log("✅ Analyse terminée avec succès")

    except Exception as e:
        log(f"[ERROR] Erreur dans run_batch: {e}")
        log_debug_prompt()
        raise


if __name__ == "__main__":
    try:
        log_debug_prompt()
        log("[INFO] Démarrage de l'analyse batch ChatGPT...")
        asyncio.run(run_batch())
    except KeyboardInterrupt:
        log("[INFO] Arrêt demandé par l'utilisateur")
    except Exception as e:
        logging.error(f"Exception non gérée: {e}")
        log_debug_prompt()
        raise
