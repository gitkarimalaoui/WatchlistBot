"""Example IA loop executing automatic scalping."""

from __future__ import annotations

import time

from movers_detector import get_top_movers
from pump_score import score_pump_ia
from execution.strategie_scalping import executer_strategie_scalping


def boucle_ia_once() -> None:
    """Run detection and scalping once."""
    movers = get_top_movers()
    for m in movers:
        res = score_pump_ia(m["ticker"])
        if res.get("score", 0) >= 80:
            executer_strategie_scalping(m["ticker"])


def boucle_ia(interval: int = 10) -> None:
    """Continuous loop running every ``interval`` seconds."""
    while True:
        boucle_ia_once()
        time.sleep(interval)


if __name__ == "__main__":  # pragma: no cover - CLI
    boucle_ia()
