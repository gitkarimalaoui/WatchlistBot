"""IA watchdog module for automatic opportunity detection."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from typing import Dict, Any

from intelligence.ai_scorer import score_ai
from utils.utils_graph import charger_intraday_intelligent
from ui.utils_affichage_ticker import calculer_indicateurs
from utils.fda_fetcher import check_fda_match
from utils.telegram_alert import send_telegram_alert
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trades.db")
THRESHOLDS_PATH = os.path.join("config", "thresholds.json")


def load_thresholds(path: str = THRESHOLDS_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "rsi_min": 65,
        "ema_short": 9,
        "ema_long": 21,
        "score_ai_min": 70,
        "volume_ratio_min": 1.5,
        "check_fda": True,
        "watch_interval": 60,
        "order_qty": 500,
        "stop_loss_pct": 10,
    }


def verifier_conditions_achat(ticker: str, thresholds: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Check if all trading conditions are met for ``ticker``."""
    thresholds = thresholds or load_thresholds()

    df_intraday = charger_intraday_intelligent(ticker)
    if df_intraday is None or df_intraday.empty:
        return {"ok": False}

    indicateurs = calculer_indicateurs(df_intraday)
    if not indicateurs:
        return {"ok": False}

    rsi = indicateurs.get("rsi")
    ema9 = indicateurs.get("ema9")
    ema21 = indicateurs.get("ema21")
    macd = indicateurs.get("macd")
    macd_signal = indicateurs.get("macd_signal")
    vwap = indicateurs.get("vwap")
    volume = indicateurs.get("volume")
    vol_avg = indicateurs.get("volume_avg", 1)
    price = indicateurs.get("price")
    volume_ratio = volume / vol_avg if vol_avg else 1.0

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT float, change_percent, score, has_fda FROM watchlist WHERE ticker = ?",
            (ticker,),
        ).fetchone()
        flt = row[0] if row else 0
        change_pct = row[1] if row else 0
        ai_score = row[2] if row else 0
        has_fda = row[3] if row else 0

    if not ai_score:
        ai_score = score_ai({"volume": volume, "float": flt, "change_percent": change_pct})

    details = []
    conditions = [
        rsi is not None and rsi > thresholds.get("rsi_min", 65),
        ema9 is not None and ema21 is not None and ema9 > ema21,
        macd is not None and macd_signal is not None and macd > macd_signal,
        price is not None and vwap is not None and price > vwap,
        volume_ratio >= thresholds.get("volume_ratio_min", 1.5),
        ai_score >= thresholds.get("score_ai_min", 70),
    ]

    if conditions[0]:
        details.append("RSI")
    if conditions[1]:
        details.append("EMA")
    if conditions[2]:
        details.append("MACD")
    if conditions[3]:
        details.append("VWAP")
    if conditions[4]:
        details.append("Volume")
    if conditions[5]:
        details.append("Score IA")

    fda_ok = bool(has_fda)
    if thresholds.get("check_fda", True) and not fda_ok:
        with sqlite3.connect(DB_PATH) as conn:
            fda_ok = check_fda_match(conn, ticker)
    if fda_ok:
        details.append("FDA")

    if all(conditions) and fda_ok:
        qty = thresholds.get("order_qty", 1)
        stop_pct = thresholds.get("stop_loss_pct", 10)
        stop_loss = price * (1 - stop_pct / 100) if price else None
        return {
            "ok": True,
            "ticker": ticker,
            "prix": round(price, 2) if price else None,
            "quantite": qty,
            "stop_loss": round(stop_loss, 2) if stop_loss else None,
            "message": "Conditions réunies : " + ", ".join(details),
        }

    return {"ok": False}


def _telegram_message(res: Dict[str, Any]) -> str:
    return (
        "🚨 OPPORTUNITÉ WATCHLISTBOT 🚨\n"
        f"💊 FDA DETECTÉE sur ${res['ticker']}\n"
        f"💵 Prix d’entrée : {res['prix']}$ | Qty : {res['quantite']}\n"
        "➡️ Valider dans l’interface ou ignorer."
    )


def surveiller_tickers(interval: int | None = None) -> None:
    """Background loop checking all tickers."""
    thresholds = load_thresholds()
    wait = interval or thresholds.get("watch_interval", 60)
    while True:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                rows = conn.execute("SELECT ticker FROM watchlist").fetchall()
            tickers = [r[0] for r in rows]
            for tic in tickers:
                res = verifier_conditions_achat(tic, thresholds)
                if res.get("ok"):
                    send_telegram_alert(_telegram_message(res))
                    st.session_state["watchdog_alert"] = res
        except Exception as exc:
            print(f"[watchdog] Error: {exc}")
        time.sleep(wait)


def start_watchdog_thread() -> None:
    if st.session_state.get("watchdog_thread"):
        return
    thread = threading.Thread(target=surveiller_tickers, daemon=True)
    thread.start()
    st.session_state["watchdog_thread"] = thread
