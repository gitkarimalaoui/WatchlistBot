import os
from typing import Dict
from utils.telegram_utils import send_telegram_message


class TelegramNotifier:
    """Simplified notifier for trade events."""

    def __init__(self) -> None:
        self.test_mode = os.getenv("TEST_MODE", "False").lower() == "true"

    def _format_trade_message(self, alert_type: str, ticker: str, details: Dict) -> str:
        action = details.get("action") or details.get("side")
        if not action:
            action = "Vente" if details.get("exit_price") else "Achat"
        price = details.get("price") or details.get("entry")
        qty = details.get("qty") or details.get("quantity")
        sl = details.get("sl") or details.get("stop_loss")
        tp = details.get("tp") or details.get("take_profit")
        source = details.get("source") or details.get("provenance", "Simulation")
        note = details.get("note")

        lines = ["\U0001F4BC TRADE EX\u00C9CUT\u00C9", f"Action : {action}", f"Ticker : {ticker}"]
        if price is not None:
            lines.append(f"Prix : {price}$")
        if qty is not None:
            lines.append(f"Quantit\u00E9 : {qty}")
        if sl is not None:
            lines.append(f"Stop Loss : {sl}")
        if tp is not None:
            lines.append(f"Take Profit : {tp}")
        if source:
            lines.append(f"Source : {source}")
        if note:
            lines.append(f"Note : {note}")
        return "\n".join(lines)

    def send_trade_alert(self, alert_type: str, ticker: str, details: Dict) -> bool:
        """Send a Telegram alert or print when in test mode."""
        message = self._format_trade_message(alert_type, ticker, details)
        if self.test_mode:
            print(f"[TEST MODE] {message}")
            return False
        return send_telegram_message(message)
