"""Unified configuration manager.

This module merges the features that were previously split between
``config/config_manager.py`` and ``core/config_manager.py``. It loads
configuration values from an optional JSON file and allows environment
variables to override or supplement these values. Access to settings is
provided via the :py:meth:`ConfigManager.get` method using dot notation.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def _load_dotenv(path: str = ".env") -> None:
    """Populate ``os.environ`` from a simple ``.env`` file if present.

    The function now attempts to locate the ``.env`` file relative to the
    repository root so that scripts executed from subdirectories still load
    the configuration correctly.
    """
    candidate_paths = [
        os.path.abspath(path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", path),
    ]

    for env_path in candidate_paths:
        if not os.path.exists(env_path):
            continue
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key, value)
        except Exception:
            # Any error just leaves the environment unchanged
            pass
        else:
            break


# Load environment variables early so subsequent code can access them
_load_dotenv()


class ConfigManager:
    """Load configuration from a JSON file and environment variables."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Return configuration with environment variables applied."""

        config: Dict[str, Any] = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                config.update(json.load(f))

        # Environment variables override config file values when present
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        if finnhub_key is not None:
            config["finnhub_api"] = finnhub_key
        else:
            config.setdefault("finnhub_api", "your_default_api_key_here")

        refresh_interval = os.getenv("REFRESH_INTERVAL")
        if refresh_interval is not None:
            try:
                config["refresh_interval"] = int(refresh_interval)
            except ValueError:
                config["refresh_interval"] = 15
        else:
            config.setdefault("refresh_interval", 15)

        debug_mode = os.getenv("DEBUG_MODE")
        if debug_mode is not None:
            config["debug_mode"] = debug_mode == "True"
        else:
            config.setdefault("debug_mode", False)

        return config

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Access nested configuration values using dot notation."""

        keys = key.split(".")
        value: Any = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


config_manager = ConfigManager()

