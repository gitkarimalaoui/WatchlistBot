import os
import requests
import logging

logger = logging.getLogger(__name__)


def send_telegram_message(message: str) -> bool:
    """Send a Telegram message using credentials from environment variables.

    If ``TELEGRAM_BOT_TOKEN`` or ``TELEGRAM_CHAT_ID`` is missing, the function
    logs a warning and does nothing.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram credentials missing; message not sent")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        return resp.ok
    except Exception as exc:  # pragma: no cover - network error
        logger.error("Telegram notification failed: %s", exc)
        return False
