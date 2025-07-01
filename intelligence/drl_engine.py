from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

from utils.db_historical import load_historical

# Lazy imports of heavy libraries
try:  # pragma: no cover - optional dependency
    from finrl.agents.stablebaselines3.models import DRLAgent  # type: ignore
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv  # type: ignore
except Exception:  # pragma: no cover - environment without FinRL
    DRLAgent = None
    StockTradingEnv = None

MODEL_PATH = Path(__file__).resolve().parent / "models" / "trained_drl_model.pkl"


def _build_env(df: pd.DataFrame) -> Optional[StockTradingEnv]:
    if StockTradingEnv is None:
        return None
    return StockTradingEnv(df=df, turbulence_threshold=0)


def load_market_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Load historical data for ``ticker`` from the local database."""
    return load_historical(ticker, start, end)


def train_agent(tickers: List[str], start: str, end: str, steps: int = 1000) -> None:
    """Train a simple DRL agent on the given tickers and save the model."""
    if DRLAgent is None:
        raise ImportError("FinRL is not available")
    dfs = [load_market_data(t, start, end) for t in tickers]
    df = pd.concat(dfs, ignore_index=True)
    env = _build_env(df)
    if env is None:
        raise RuntimeError("Environment could not be created")
    agent = DRLAgent(env=env)
    model = agent.get_model("ppo")
    model.learn(total_timesteps=steps)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(MODEL_PATH))


def predict_for_ticker(ticker: str) -> Optional[str]:
    """Return the next action predicted by the trained model for ``ticker``."""
    if DRLAgent is None or not MODEL_PATH.exists():
        return None
    end = pd.Timestamp.now().strftime("%Y-%m-%d")
    start = (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    df = load_market_data(ticker, start, end)
    if df.empty:
        return None
    env = _build_env(df)
    if env is None:
        return None
    agent = DRLAgent(env=env)
    model = agent.get_model("ppo")
    model.load(str(MODEL_PATH))
    obs = env.reset()
    action, _state = model.predict(obs, deterministic=True)
    return str(action)
