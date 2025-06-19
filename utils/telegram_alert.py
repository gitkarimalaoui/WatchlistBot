from .telegram_utils import send_telegram_message


def send_telegram_alert(message: str) -> bool:
    """Backward compatible wrapper around ``send_telegram_message``."""
    return send_telegram_message(message)
