from __future__ import annotations

import csv
import os
import sqlite3
from datetime import datetime
from typing import Optional, Tuple

try:
    import speech_recognition as sr  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    sr = None  # type: ignore

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None  # type: ignore

from config.config_manager import config_manager
from core.db import DB_PATH

LOG_FILE = "journal_vocal.csv"


def _speak(text: str) -> None:
    """Vocalise ``text`` using ``pyttsx3`` when available."""
    print(text)
    if pyttsx3 is None:
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def _log(user_input: str, interpretation: str, action: str, status: str) -> None:
    """Append an interaction row to :data:`LOG_FILE`."""
    write_header = not os.path.exists(LOG_FILE)
    row = [datetime.utcnow().isoformat(), user_input, interpretation, action, status]
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["timestamp", "user_input", "interpretation", "action", "status"])
        writer.writerow(row)


def _recognize(timeout: int = 5) -> Optional[str]:
    """Capture audio from the microphone and return recognized text."""
    if sr is None:
        return None
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎤 Parlez...")
            audio = recognizer.listen(source, timeout=timeout)
        return recognizer.recognize_google(audio, language="fr-FR")
    except Exception as exc:  # pragma: no cover - microphone handling
        print(f"[voice] {exc}")
        return None


def interpret_command(text: str) -> Tuple[str, Optional[str]]:
    """Return (action, param) for ``text``."""
    t = text.lower().strip()
    if "liste des tickers" in t:
        return "list_tickers", None
    if t.startswith("exécute achat de") or t.startswith("execute achat de"):
        ticker = t.split("de", 1)[1].strip().upper()
        return "buy", ticker
    if "meilleurs scores ia" in t:
        return "best_scores", None
    if "ferme la journée" in t:
        return "close_day", None
    return "ask_ai", text


def _list_tickers() -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT ticker FROM watchlist").fetchall()
        conn.close()
        if not rows:
            return "Aucun ticker."
        return ", ".join(r[0] for r in rows)
    except Exception as exc:
        return f"Erreur: {exc}"


def _best_scores() -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT ticker, score FROM watchlist WHERE score IS NOT NULL ORDER BY score DESC LIMIT 3"
        ).fetchall()
        conn.close()
        if not rows:
            return "Aucun score disponible."
        return "; ".join(f"{t}:{s}" for t, s in rows)
    except Exception as exc:
        return f"Erreur: {exc}"


def _simulate_buy(ticker: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS trades_simules (id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT, date TEXT)"
        )
        conn.execute(
            "INSERT INTO trades_simules (ticker, date) VALUES (?, ?)",
            (ticker, datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()
        return f"Ordre simulé pour {ticker}."
    except Exception as exc:
        return f"Erreur: {exc}"


def _close_day() -> str:
    try:
        from ui.page_modules.cloture_journee import cloturer_journee

        cloturer_journee()  # type: ignore
        return "Clôture journalière exécutée."
    except Exception as exc:
        return f"Erreur: {exc}"


def _ask_openai(question: str) -> str:
    if not config_manager.get("use_voice_assistant", False):
        return "Question reçue: " + question
    try:
        import openai  # type: ignore
    except Exception:
        return question
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return question
    openai.api_key = api_key
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
        )
        return res.choices[0].message["content"].strip()
    except Exception:
        return question


def handle(text: str) -> str:
    action, param = interpret_command(text)
    if action == "list_tickers":
        result = _list_tickers()
    elif action == "buy" and param:
        result = _simulate_buy(param)
    elif action == "best_scores":
        result = _best_scores()
    elif action == "close_day":
        result = _close_day()
    else:
        result = _ask_openai(text)
    _log(text, param or "", action, "ok")
    _speak(result)
    return result


def lancer_assistant_vocal(timeout: int = 5) -> None:
    """Main loop for the voice assistant."""
    if not config_manager.get("use_voice_assistant", False):
        print("Voice assistant disabled in configuration.")
        return
    while True:
        user_text = _recognize(timeout)
        if not user_text:
            continue
        if user_text.lower() in {"quit", "exit", "stop"}:
            break
        handle(user_text)

