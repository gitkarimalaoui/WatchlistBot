from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from gymnasium import Env, spaces

from utils.db_intraday import load_intraday_smart


class PennyStockEnv(Env):
    """Simple trading environment using intraday data from the local DB."""

    def __init__(
        self,
        tickers: List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        initial_cash: float = 10000.0,
    ) -> None:
        super().__init__()
        self.tickers = tickers
        self.start = start
        self.end = end
        self.initial_cash = initial_cash
        self.data: Dict[str, pd.DataFrame] = {}
        for t in tickers:
            df = load_intraday_smart(t, start=start)
            if end is not None and not df.empty:
                df = df[df["timestamp"] <= end]
            self.data[t] = df.reset_index(drop=True)
        lengths = [len(df) for df in self.data.values() if not df.empty]
        self.max_steps = max(min(lengths) - 1, 1) if lengths else 1
        self.action_space = spaces.Box(low=-1, high=1, shape=(len(tickers),))
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(1 + 2 * len(tickers),)
        )
        self._seed()
        self.reset()

    def _seed(self, seed: Optional[int] = None) -> None:
        np.random.seed(seed)

    def _get_prices(self) -> List[float]:
        return [
            self.data[t].iloc[self.current_step]["close"]
            if not self.data[t].empty
            else 0.0
            for t in self.tickers
        ]

    def _get_state(self) -> np.ndarray:
        prices = self._get_prices()
        holdings = [self.position[t] for t in self.tickers]
        state = np.array([self.cash] + prices + holdings, dtype=np.float32)
        return state

    def _portfolio_value(self) -> float:
        prices = self._get_prices()
        return float(self.cash + np.dot(prices, [self.position[t] for t in self.tickers]))

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.current_step = 0
        self.cash = float(self.initial_cash)
        self.position = {t: 0.0 for t in self.tickers}
        return self._get_state(), {}

    def step(self, action: np.ndarray):
        action = np.clip(action, -1, 1)
        prices = self._get_prices()
        prev_val = self._portfolio_value()
        for idx, t in enumerate(self.tickers):
            price = prices[idx]
            if price <= 0:
                continue
            a = float(action[idx])
            if a > 0:  # buy
                invest_amt = self.cash * a
                shares = invest_amt / price
                self.cash -= shares * price
                self.position[t] += shares
            elif a < 0:  # sell
                shares = min(-a * self.position[t], self.position[t])
                self.cash += shares * price
                self.position[t] -= shares
        self.current_step += 1
        done = self.current_step >= self.max_steps
        cur_val = self._portfolio_value()
        reward = cur_val - prev_val
        state = self._get_state()
        info = {"portfolio_value": cur_val}
        return state, reward, done, False, info

    def render(self) -> None:
        value = self._portfolio_value()
        print(f"Step {self.current_step} Portfolio Value: {value:.2f} Cash: {self.cash:.2f}")
