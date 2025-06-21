"""Example IA loop executing automatic scalping."""

from __future__ import annotations

import time

from movers_detector import get_top_movers
from pump_score import score_pump_ia
from execution.strategie_scalping import executer_strategie_scalping
from data.fundamental_filters import get_fundamental_data
from db.fundamentals import update_fundamentals


def boucle_ia() -> None:
    """Run detection and scalping once."""
    movers = get_top_movers()
    for m in movers:
        fundamentals = get_fundamental_data(m["ticker"])
        update_fundamentals(
            m["ticker"],
            fundamentals.get("pdufa_date"),
            fundamentals.get("market_cap"),
            fundamentals.get("de_ratio"),
            fundamentals.get("cash_runway"),
        )
        res = score_pump_ia(m["ticker"])
        if res.get("score", 0) >= 80:
            executer_strategie_scalping(m["ticker"])


def boucle_ia_loop(interval: int = 10) -> None:
    """Continuous loop running every ``interval`` seconds."""
    while True:
        boucle_ia()
        time.sleep(interval)


if __name__ == "__main__":  # pragma: no cover - CLI
    boucle_ia_loop()
