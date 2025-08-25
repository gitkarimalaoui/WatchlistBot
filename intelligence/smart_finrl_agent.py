from __future__ import annotations

import datetime
import importlib
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional, List

from core.db import DB_PATH
from intelligence.finrl_env_penny import PennyStockEnv
from utils.telegram_utils import send_telegram_message, MISSING_CREDENTIALS


def _log_metrics(metrics: Dict[str, object]) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS finrl_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                model_path TEXT,
                sharpe REAL,
                cumulative_return REAL
            )
            """
        )
        conn.execute(
            "INSERT INTO finrl_logs (date, model_path, sharpe, cumulative_return) VALUES (?, ?, ?, ?)",
            (
                datetime.datetime.utcnow().isoformat(),
                metrics.get("model_path"),
                metrics.get("sharpe_ratio"),
                metrics.get("cumulative_return"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def run_pipeline() -> Dict[str, object]:
    """Prepare data, train the FinRL model and log metrics."""
    prepare = importlib.import_module("models.finrl.prepare_data_for_finrl")
    data_path: Path = prepare.main()

    trainer = importlib.import_module("train_finrl_model")
    metrics: Dict[str, object] = trainer.train_from_config(data_path=data_path)

    _log_metrics(metrics)
    return metrics


def latest_model(checkpoint_dir: Path = Path("models/finrl/checkpoints")) -> Optional[Path]:
    paths = sorted(checkpoint_dir.glob("ppo_*.zip"))
    return paths[-1] if paths else None


def dummy_live_signals() -> Dict[str, str]:
    """Placeholder live signals using the latest model."""
    path = latest_model()
    if not path:
        return {}
    # Real implementation would load the model and produce signals.
    return {"signal": "HOLD", "model": str(path)}


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run_pipeline()

try:  # Optional heavy deps
    from stable_baselines3 import PPO, A2C, DQN
except Exception:  # pragma: no cover - optional environment
    PPO = A2C = DQN = None  # type: ignore


MODELS_DIR = Path(__file__).resolve().parent / "models"
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.FileHandler(LOG_DIR / "finrl_agent.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _fetch_watchlist_tickers() -> List[str]:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    try:
        rows = conn.execute("SELECT ticker FROM watchlist").fetchall()
    except Exception:
        return []
    finally:
        conn.close()
    return [r[0] for r in rows]


def lancer_apprentissage_rl(tickers: List[str], capital: float = 2000.0, model_type: str = "ppo") -> str | None:
    """Train a DRL agent on the given tickers and save the model."""
    if PPO is None:
        logger.error("stable-baselines3 not available")
        return None
    if not tickers:
        tickers = _fetch_watchlist_tickers()
    env = PennyStockEnv(tickers, initial_cash=capital)
    mapping = {"ppo": PPO, "a2c": A2C, "dqn": DQN}
    ModelCls = mapping.get(model_type.lower(), PPO)
    model = ModelCls("MlpPolicy", env, verbose=0)
    logger.info("Training %s agent on %d tickers", model_type, len(tickers))
    model.learn(total_timesteps=5000)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / f"{model_type.lower()}_trained.pkl"
    model.save(str(model_path))
    logger.info("Model saved to %s", model_path)
    return str(model_path)


def executer_trading_reel_auto(agent_model_path: str) -> None:
    """Run the trained agent and record simulated trades."""
    if PPO is None or not Path(agent_model_path).exists():
        logger.error("Model not available: %s", agent_model_path)
        return
    tickers = _fetch_watchlist_tickers()
    if not tickers:
        logger.warning("No tickers found for trading")
        return
    env = PennyStockEnv(tickers)
    model = PPO.load(agent_model_path, env=env)
    obs, _ = env.reset()
    done = False
    conn = sqlite3.connect(str(DB_PATH))
    missing_creds = False
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades_simules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                prix_achat REAL,
                quantite INTEGER,
                provenance TEXT,
                date DATETIME NOT NULL,
                UNIQUE(ticker, date)
            )
            """
        )
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, _reward, done, _, info = env.step(action)
            for idx, t in enumerate(tickers):
                act = float(action[idx])
                if act > 0.5:
                    price = env.data[t].iloc[env.current_step]["close"]
                    try:
                        conn.execute(
                            """
                            INSERT INTO trades_simules (ticker, prix_achat, quantite, provenance, date)
                            VALUES (?, ?, 1, 'finrl', datetime('now'))
                            """,
                            (t, price),
                        )
                    except sqlite3.IntegrityError:
                        logger.info("Trade already exists for %s", t)
                        continue
                    res = send_telegram_message(f"FinRL BUY {t} at {price:.2f}")
                    if res == MISSING_CREDENTIALS:
                        missing_creds = True
        conn.commit()
    finally:
        conn.close()
    if missing_creds:
        logger.warning("Telegram credentials missing")
    logger.info("Trading session complete")

