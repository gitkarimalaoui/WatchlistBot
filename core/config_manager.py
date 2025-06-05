import json
import os

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key: str, default=None):
        """Access nested configuration using dot notation, e.g. 'api.finnhub_key'."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

# Usage example:
config_manager = ConfigManager()

# Example: get the Finnhub API key
# finnhub_key = config_manager.get("api.finnhub_key")
