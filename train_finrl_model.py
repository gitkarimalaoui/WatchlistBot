"""Train a FinRL agent using configuration from models/finrl/config.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union


def load_config(path: Union[str, Path] = "models/finrl/config.json") -> dict:

    """Load JSON configuration file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)



def train_from_config(config_path: Union[str, Path] = "models/finrl/config.json") -> None:

    """Train a FinRL model using parameters from a JSON config."""
    config = load_config(config_path)

    # Import heavy libraries lazily so that tests not requiring them can run
    import pandas as pd  # type: ignore
    from finrl.agents.stablebaselines3.models import DRLAgent  # type: ignore
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv  # type: ignore

    env_kwargs = config.get("env", {})
    training_steps = int(config.get("training_steps", 10000))
    model_path = config.get("model_path", "models/finrl/trained_agent")

    # Placeholder dataframe; replace with real market data in practice
    df = pd.DataFrame()

    env = StockTradingEnv(df=df, **env_kwargs)
    agent = DRLAgent(env=env)
    model = agent.get_model("a2c")
    model.learn(total_timesteps=training_steps)
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    train_from_config()
