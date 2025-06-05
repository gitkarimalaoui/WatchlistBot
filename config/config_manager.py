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
from typing import Any, Dict


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

    def get(self, key: str, default: Any | None = None) -> Any:
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

