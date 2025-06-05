# config/config_manager.py
import os

class ConfigManager:
    def __init__(self):
        self.api_key_finnhub = os.getenv("FINNHUB_API_KEY", "your_default_api_key_here")
        self.refresh_interval = int(os.getenv("REFRESH_INTERVAL", "15"))
        self.debug_mode = os.getenv("DEBUG_MODE", "False") == "True"

config_manager = ConfigManager()
