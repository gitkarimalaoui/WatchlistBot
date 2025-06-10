"""Simple AI trading loop using simulated trades."""

import random
import sys
from typing import Iterable

from intelligence.ticker_analysis import score_ticker
from simulation.execution_simulee import enregistrer_trade_simule
from intelligence.learn_from_trades import main as learn_from_trades_main

WATCHLIST = ["CMND", "RSLS", "TCTM", "AAPL", "GME"]
SCORE_SEUIL = 50.0  # minimum AI score in percent
TP_PCT = 0.05
SL_PCT = 0.03


def _simulate_trade(ticker: str, entry: float) -> dict:
    sl = round(entry * (1 - SL_PCT), 2)
    tp = round(entry * (1 + TP_PCT), 2)
    return enregistrer_trade_simule(ticker, entry, 1, sl=sl, tp=tp)


def run_learning_loop(cycles: int = 1, learn: bool = True, watchlist: Iterable[str] = WATCHLIST) -> None:
    """Loop over tickers, score them and simulate trades."""
    sys.stdout.reconfigure(encoding="utf-8")
    for _ in range(cycles):
        print("=== NOUVEAU CYCLE ===")
        for ticker in watchlist:
            score = score_ticker(ticker)
            print(f"{ticker} -> score {score}")
            if score >= SCORE_SEUIL:
                entry_price = round(random.uniform(5, 10), 2)
                result = _simulate_trade(ticker, entry_price)
                print(f"Trade simulé {ticker} gain {result['gain_net']}")
        if learn:
            try:
                learn_from_trades_main()
            except Exception as e:  # pragma: no cover - optional learning
                print(f"Erreur apprentissage: {e}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run_learning_loop()
