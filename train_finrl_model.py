"""Train a FinRL agent using configuration from models/finrl/config.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Union
import shutil
import datetime

SAVED_MODEL_PATH = Path("models/finrl/saved_model/ppo_model.zip")



def load_config(path: Union[str, Path] = "models/finrl/config.json") -> dict:

    """Load JSON configuration file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)



def train_from_config(
    config_path: Union[str, Path] = "models/finrl/config.json",
    data_path: Union[str, Path] = "models/finrl/finrl_data.csv",
    checkpoint_dir: Union[str, Path] = "models/finrl/checkpoints",
) -> Dict[str, object]:

    """Train a FinRL model using parameters from a JSON config and return metrics."""

    config = load_config(config_path)

    # Import heavy libraries lazily so that tests not requiring them can run
    import pandas as pd  # type: ignore
    from finrl.agents.stablebaselines3.models import DRLAgent  # type: ignore
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv  # type: ignore

    env_kwargs = config.get("env", {})
    training_steps = int(config.get("training_steps", 1000))

    data_path = Path(data_path)
    if data_path.exists():
        df = pd.read_csv(data_path)
    else:
        df = pd.DataFrame()

    env = StockTradingEnv(df=df, **env_kwargs)
    agent = DRLAgent(env=env)
    model = agent.get_model("ppo")
    model.learn(total_timesteps=training_steps)

    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    save_path = Path(checkpoint_dir) / f"ppo_{timestamp}.zip"
    model.save(str(save_path))

    returns = df["close"].pct_change().dropna()
    cumulative_return = (
        (df["close"].iloc[-1] / df["close"].iloc[0] - 1) if len(df) >= 2 else 0.0
    )
    sharpe_ratio = (
        (returns.mean() / returns.std()) * (252 ** 0.5) if not returns.empty else 0.0
    )
    equity_curve = (1 + returns).cumprod().tolist()

    return {
        "model_path": str(save_path),
        "cumulative_return": float(cumulative_return),
        "sharpe_ratio": float(sharpe_ratio),
        "equity_curve": equity_curve,
    }


def launch_finrl_training(force: bool = False) -> Dict[str, object]:
    """Prepare data, train PPO model and copy it to ``SAVED_MODEL_PATH``."""
    from models.finrl import prepare_data_for_finrl

    if SAVED_MODEL_PATH.exists() and not force:
        return {"model_path": str(SAVED_MODEL_PATH)}

    csv_path = prepare_data_for_finrl.main()
    metrics = train_from_config(data_path=csv_path)

    SAVED_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(metrics["model_path"], SAVED_MODEL_PATH)
    metrics["model_path"] = str(SAVED_MODEL_PATH)
    return metrics


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    launch_finrl_training()
