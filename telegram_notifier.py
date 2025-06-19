import os
from typing import Dict
import requests


class TelegramNotifier:
    """Simplified notifier for trade events."""

    def __init__(self) -> None:
        self.test_mode = os.getenv("TEST_MODE", "False").lower() == "true"
        self.token = os.getenv("TELEGRAM_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    def send_trade_alert(self, alert_type: str, ticker: str, details: Dict) -> bool:
        """Send a Telegram alert or print when in test mode."""
        message = f"[{alert_type}] {ticker} - {details}"
        if self.test_mode or not self.token or not self.chat_id:
            print(f"[TEST MODE] {message}")
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message}
        try:
            resp = requests.post(url, data=payload, timeout=10)
            return resp.ok
        except Exception:
            return False
