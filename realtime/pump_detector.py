"""Detection de mouvements de prix anormaux et trailing stop."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from intelligence.ai_scorer import compute_global_score
from notifications.telegram_bot import envoyer_alerte_ia
from notifications.popup_trade import show_trade_popup
from simulation.simulate_trade_result import executer_trade_simule

RULES_PATH = os.path.join("config", "rules_auto.json")
TICKS_DIR = os.path.join("data", "ticks")


def load_rules(path: str = RULES_PATH) -> dict:
    """Charge les seuils de d\u00e9tection depuis ``rules_auto.json``."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "volume_ratio_min": 2.0,
        "price_spike_pct": 5.0,
        "trailing_stop_pct": 2.0,
        "order_qty": 1,
    }


def load_ticks(ticker: str) -> Optional[pd.DataFrame]:
    path = os.path.join(TICKS_DIR, f"{ticker}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    if "timestamp" not in df.columns or "c" not in df.columns:
        return None
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df


def compute_metrics(df: pd.DataFrame, minutes: int = 3) -> Optional[dict]:
    if df.empty:
        return None
    df = df.sort_values("timestamp")
    end = df["timestamp"].iloc[-1]
    start = end - pd.Timedelta(minutes=minutes)
    recent = df[df["timestamp"] >= start]
    if recent.empty:
        return None
    price_start = recent["c"].iloc[0]
    price_end = recent["c"].iloc[-1]
    price_change = (price_end - price_start) / price_start * 100
    vol_recent = recent["v"].sum() if "v" in df.columns else len(recent)
    prev = df[(df["timestamp"] < start) & (df["timestamp"] >= start - pd.Timedelta(minutes=minutes))]
    avg_vol = prev["v"].sum() if not prev.empty and "v" in df.columns else vol_recent
    vol_ratio = vol_recent / avg_vol if avg_vol else 0
    gscore = compute_global_score(0, 0, price_change, vol_recent, 0, "")
    return {
        "price_change": round(price_change, 2),
        "volume_ratio": round(vol_ratio, 2),
        "global_score": gscore,
        "last_price": price_end,
    }


def detect_pump(ticker: str, rules: Optional[dict] = None) -> Optional[dict]:
    df = load_ticks(ticker)
    if df is None:
        return None
    metrics = compute_metrics(df)
    if metrics is None:
        return None
    rules = rules or load_rules()
    if (
        metrics["price_change"] >= rules.get("price_spike_pct", 0)
        and metrics["volume_ratio"] >= rules.get("volume_ratio_min", 0)
    ):
        envoyer_alerte_ia(ticker, metrics["global_score"], metrics["price_change"])
        stop = metrics["last_price"] * (1 - rules.get("trailing_stop_pct", 0) / 100)
        qty = rules.get("order_qty", 1)
        show_trade_popup(ticker, metrics["last_price"], qty, stop)
        metrics["alert_sent"] = True
    else:
        metrics["alert_sent"] = False
    return metrics


@dataclass
class TrailingStop:
    entry_price: float
    trailing_pct: float

    def __post_init__(self) -> None:
        self.trailing_pct = self.trailing_pct / 100
        self.highest = self.entry_price
        self.stop = self.entry_price * (1 - self.trailing_pct)

    def update(self, price: float) -> None:
        if price > self.highest:
            self.highest = price
            self.stop = price * (1 - self.trailing_pct)

    def should_exit(self, price: float) -> bool:
        return price <= self.stop


def simulate_trailing_trade(ticker: str, prices: list[float], trail_pct: float = 2.0, qty: int = 1) -> Optional[dict]:
    if not prices:
        return None
    ts = TrailingStop(prices[0], trail_pct)
    entry = prices[0]
    for p in prices[1:]:
        ts.update(p)
        if ts.should_exit(p):
            return executer_trade_simule(ticker, entry, qty, None, None, exit_price=p)
    return executer_trade_simule(ticker, entry, qty, None, None, exit_price=prices[-1])
