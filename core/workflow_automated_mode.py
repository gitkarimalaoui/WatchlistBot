"""Automated IA workflow for WatchlistBot."""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import yfinance as yf

from config.config_manager import ConfigManager
from intelligence.ai_scorer import score_ai
from intelligence.drl_engine import predict_for_ticker
from intelligence.meta_ia import load_meta, save_meta
from intelligence.learn_from_trades import main as learn_from_trades_main
from simulation.execution_simulee import enregistrer_trade_simule
from utils.fda_fetcher import check_fda_match
from utils.order_executor import executer_ordre_reel_direct
from utils.telegram_alert import MISSING_CREDENTIALS, send_telegram_alert
from utils.utils_graph import charger_intraday_intelligent
from ui.utils_affichage_ticker import calculer_indicateurs
from utils.utils_signaux import is_buy_signal
from scripts.postmarket_scanner import scan_postmarket_watchlist
from utils.watchlist_live import get_watchlist_data_for_ui

DB_PATH = os.path.join("data", "trades.db")
CAPITAL_INITIAL = 2000.0


@dataclass
class TradeDecision:
    ticker: str
    price: float
    quantity: int
    strategy: str
    approved: bool
    confidence: float


def _get_price(ticker: str) -> float:
    """Return the latest close price using yfinance."""
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            return float(df["Close"].iloc[-1])
    except Exception:
        pass
    return 0.0


def generate_watchlist() -> List[Dict[str, Any]]:
    """Return sorted watchlist entries with AI scores applied."""
    raw = scan_postmarket_watchlist()
    entries = get_watchlist_data_for_ui(raw)
    scored: List[Dict[str, Any]] = []
    for itm in entries:
        ticker = itm.get("symbol") or itm.get("ticker")
        if not ticker:
            continue
        price = _get_price(ticker)
        if price < 1:
            continue
        itm["price"] = price
        itm["score_ai"] = score_ai(
            {
                "volume": itm.get("volume"),
                "float": itm.get("float"),
                "change_percent": itm.get("percent_change"),
            }
        )
        scored.append(itm)
    scored.sort(key=lambda x: x.get("score_ai", 0), reverse=True)
    return scored


def simulate_trades(tickers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Simulate trades for the given ticker list."""
    results: List[Dict[str, Any]] = []
    per_trade = CAPITAL_INITIAL / max(len(tickers), 1)
    for itm in tickers:
        ticker = itm.get("symbol") or itm.get("ticker")
        price = float(itm.get("price", 0))
        if not ticker or price <= 0:
            continue
        qty = int(per_trade // price)
        if qty <= 0:
            qty = 1
        res = enregistrer_trade_simule(
            ticker,
            price,
            qty,
            sl=price * 0.9,
            tp=price * 1.1,
            provenance="auto",
        )
        results.append({"ticker": ticker, **res})
    return results


def choose_strategy(ticker: str, score: float) -> str:
    """Return strategy name based on indicators and news."""
    df = charger_intraday_intelligent(ticker)
    indicateurs = calculer_indicateurs(df) or {}
    buy_signal = is_buy_signal({**indicateurs, "score_ia": score})
    pump_score = indicateurs.get("pump_pct_60s", 0)
    with sqlite3.connect(DB_PATH) as conn:
        has_fda = check_fda_match(conn, ticker)
    if pump_score > 5:
        return "trailing_dynamic"
    if has_fda:
        return "buy_hold_day"
    if buy_signal:
        return "scalping_aggressif"
    return "scalping_aggressif"


def validate_trade(ticker: str) -> float:
    """Return FinRL confidence score for ticker (0-1)."""
    try:
        action = predict_for_ticker(ticker)
        return 0.8 if action is not None else 0.0
    except Exception:
        return 0.0


def lancer_workflow_ia(
    config: Optional[ConfigManager] = None,
) -> Tuple[List[TradeDecision], bool]:
    """Main entry point for the autonomous IA workflow.

    Returns
    -------
    Tuple[List[TradeDecision], bool]
        The list of trade decisions and a flag indicating whether Telegram
        credentials were missing during notifications.
    """
    cfg = config or ConfigManager()
    _ = load_meta()  # ensure meta_ia.json exists

    watchlist = generate_watchlist()
    simulations = simulate_trades(watchlist)

    decisions: List[TradeDecision] = []
    missing_credentials = False
    for sim in simulations:
        ticker = sim["ticker"]
        price = sim.get("entry") or sim.get("prix_achat")
        qty = sim.get("quantity") or sim.get("quantite")
        score = next((w.get("score_ai", 0) for w in watchlist if (w.get("symbol") or w.get("ticker")) == ticker), 0)
        strategy = choose_strategy(ticker, score)
        conf = validate_trade(ticker)
        approved = conf >= 0.7
        if approved and cfg.get("trading_mode") == "real":
            executer_ordre_reel_direct(ticker, price, qty)
        else:
            res = send_telegram_alert(
                f"{ticker} {price}$ Qty:{qty} Strat:{strategy} Conf:{conf:.2f}"
            )
            if res == MISSING_CREDENTIALS:
                missing_credentials = True
        decisions.append(
            TradeDecision(
                ticker=ticker,
                price=float(price),
                quantity=int(qty),
                strategy=strategy,
                approved=approved,
                confidence=conf,
            )
        )

    learn_from_trades_main()
    meta = load_meta()
    meta.setdefault("history", []).append({"run": len(meta.get("history", [])) + 1})
    save_meta(meta)

    return decisions, missing_credentials
